"""
MT-023 Task 4 — LLM Model Registry

Manage fine-tuned LLM model versions with production/candidate status,
version control, and rollback capability.

Usage:
    # Register new model
    python -m dcim_ai.llm.model_registry register \
        --name dcim_assistant \
        --version v1.0 \
        --adapter-path /path/to/adapter

    # Promote to production
    python -m dcim_ai.llm.model_registry promote \
        --name dcim_assistant \
        --version v1.0

    # List versions
    python -m dcim_ai.llm.model_registry list --name dcim_assistant

    # Get active model
    python -m dcim_ai.llm.model_registry active --name dcim_assistant
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from sqlalchemy import text

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.data_loader import get_db_engine

engine = get_db_engine()

# =====================================================
# REGISTRY FUNCTIONS
# =====================================================

def register_llm_model(model_name, version, base_model, adapter_path, metrics, notes=None):
    """
    Register new LLM model version as candidate
    
    Args:
        model_name: Model identifier (e.g., 'dcim_assistant')
        version: Version string (e.g., 'v1.0')
        base_model: Base model name (e.g., 'Qwen/Qwen2.5-3B-Instruct')
        adapter_path: Absolute path to LoRA adapter directory
        metrics: Dict of training metrics
        notes: Optional notes
    """
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                INSERT INTO llm_model_registry 
                (model_name, version, base_model, adapter_path, metrics_json, status, notes)
                VALUES (:model_name, :version, :base_model, :adapter_path, :metrics, 'candidate', :notes)
            """), {
                "model_name": model_name,
                "version": version,
                "base_model": base_model,
                "adapter_path": adapter_path,
                "metrics": json.dumps(metrics),
                "notes": notes
            })
            conn.commit()
            print(f"✅ Registered {model_name} {version} as candidate")
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            raise

def promote_to_production(model_name, version):
    """
    Promote candidate model to production
    Automatically archives current production model
    
    Args:
        model_name: Model identifier
        version: Version to promote
    """
    with engine.connect() as conn:
        try:
            # Check if version exists and is candidate
            result = conn.execute(text("""
                SELECT status FROM llm_model_registry
                WHERE model_name = :model_name AND version = :version
            """), {"model_name": model_name, "version": version})
            
            row = result.fetchone()
            if not row:
                print(f"❌ Version {version} not found")
                return False
            
            if row._mapping["status"] == "production":
                print(f"⚠️  Version {version} is already in production")
                return True
            
            # Deactivate current production
            conn.execute(text("""
                UPDATE llm_model_registry
                SET is_active = FALSE, status = 'archived'
                WHERE model_name = :model_name AND is_active = TRUE
            """), {"model_name": model_name})
            
            # Activate new version
            conn.execute(text("""
                UPDATE llm_model_registry
                SET is_active = TRUE, status = 'production', activated_at = NOW()
                WHERE model_name = :model_name AND version = :version
            """), {"model_name": model_name, "version": version})
            
            conn.commit()
            print(f"✅ Promoted {model_name} {version} to production")
            return True
            
        except Exception as e:
            print(f"❌ Promotion failed: {e}")
            raise

def rollback_to_version(model_name, version):
    """
    Rollback to previous version
    
    Args:
        model_name: Model identifier
        version: Version to rollback to
    """
    print(f"Rolling back {model_name} to {version}...")
    return promote_to_production(model_name, version)

def get_active_model(model_name):
    """
    Get current production model
    
    Args:
        model_name: Model identifier
        
    Returns:
        Dict with version, adapter_path, metrics, or None
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT version, adapter_path, base_model, metrics_json, activated_at
            FROM llm_model_registry
            WHERE model_name = :model_name AND is_active = TRUE
            LIMIT 1
        """), {"model_name": model_name})
        
        row = result.fetchone()
        if row:
            metrics_json = row._mapping["metrics_json"]
            # Handle both string and dict (PostgreSQL JSONB returns dict)
            if isinstance(metrics_json, str):
                metrics = json.loads(metrics_json)
            else:
                metrics = metrics_json
            
            return {
                "version": row._mapping["version"],
                "adapter_path": row._mapping["adapter_path"],
                "base_model": row._mapping["base_model"],
                "metrics": metrics,
                "activated_at": str(row._mapping["activated_at"])
            }
        return None

def list_versions(model_name, status=None):
    """
    List all versions of a model
    
    Args:
        model_name: Model identifier
        status: Filter by status (candidate/production/archived)
        
    Returns:
        List of version dicts
    """
    with engine.connect() as conn:
        if status:
            result = conn.execute(text("""
                SELECT version, status, base_model, created_at, activated_at, is_active, notes
                FROM llm_model_registry
                WHERE model_name = :model_name AND status = :status
                ORDER BY created_at DESC
            """), {"model_name": model_name, "status": status})
        else:
            result = conn.execute(text("""
                SELECT version, status, base_model, created_at, activated_at, is_active, notes
                FROM llm_model_registry
                WHERE model_name = :model_name
                ORDER BY created_at DESC
            """), {"model_name": model_name})
        
        return [dict(row._mapping) for row in result]

def get_model_metrics(model_name, version):
    """
    Get training metrics for a specific version
    
    Args:
        model_name: Model identifier
        version: Version string
        
    Returns:
        Dict of metrics or None
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT metrics_json FROM llm_model_registry
            WHERE model_name = :model_name AND version = :version
        """), {"model_name": model_name, "version": version})
        
        row = result.fetchone()
        if row:
            metrics_json = row._mapping["metrics_json"]
            # Handle both string and dict (PostgreSQL JSONB returns dict)
            if isinstance(metrics_json, str):
                return json.loads(metrics_json)
            else:
                return metrics_json
        return None

# =====================================================
# CLI INTERFACE
# =====================================================

def cmd_register(args):
    """Register new model version"""
    # Load metadata if available
    metadata_path = Path(args.adapter_path).parent / "metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        base_model = metadata.get("base_model", args.base_model)
        metrics = {
            "train_loss": metadata.get("train_loss"),
            "dataset_size": metadata.get("dataset_size"),
            "epochs": metadata.get("epochs"),
            "train_runtime_seconds": metadata.get("train_runtime_seconds")
        }
    else:
        base_model = args.base_model
        metrics = {}
    
    register_llm_model(
        model_name=args.name,
        version=args.version,
        base_model=base_model,
        adapter_path=args.adapter_path,
        metrics=metrics,
        notes=args.notes
    )

def cmd_promote(args):
    """Promote model to production"""
    promote_to_production(args.name, args.version)

def cmd_rollback(args):
    """Rollback to previous version"""
    rollback_to_version(args.name, args.version)

def cmd_list(args):
    """List model versions"""
    versions = list_versions(args.name, args.status)
    
    if not versions:
        print(f"No versions found for {args.name}")
        return
    
    print(f"\n{'Version':<12} {'Status':<12} {'Active':<8} {'Created':<20} {'Base Model':<30}")
    print("-" * 90)
    
    for v in versions:
        active = "✓" if v["is_active"] else ""
        created = str(v["created_at"])[:19] if v["created_at"] else ""
        base = v["base_model"][:28] + "..." if len(v["base_model"]) > 30 else v["base_model"]
        
        print(f"{v['version']:<12} {v['status']:<12} {active:<8} {created:<20} {base:<30}")
    
    print()

def cmd_active(args):
    """Show active production model"""
    model = get_active_model(args.name)
    
    if not model:
        print(f"No active model for {args.name}")
        return
    
    print(f"\nActive Model: {args.name}")
    print(f"Version: {model['version']}")
    print(f"Base Model: {model['base_model']}")
    print(f"Adapter Path: {model['adapter_path']}")
    print(f"Activated At: {model['activated_at']}")
    print(f"\nMetrics:")
    for key, value in model['metrics'].items():
        print(f"  {key}: {value}")
    print()

def cmd_metrics(args):
    """Show metrics for specific version"""
    metrics = get_model_metrics(args.name, args.version)
    
    if not metrics:
        print(f"No metrics found for {args.name} {args.version}")
        return
    
    print(f"\nMetrics for {args.name} {args.version}:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print()

# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="LLM Model Registry Management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register new model version")
    register_parser.add_argument("--name", required=True, help="Model name")
    register_parser.add_argument("--version", required=True, help="Version string")
    register_parser.add_argument("--adapter-path", required=True, help="Path to adapter directory")
    register_parser.add_argument("--base-model", default="", help="Base model name")
    register_parser.add_argument("--notes", help="Optional notes")
    
    # Promote command
    promote_parser = subparsers.add_parser("promote", help="Promote to production")
    promote_parser.add_argument("--name", required=True, help="Model name")
    promote_parser.add_argument("--version", required=True, help="Version to promote")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to version")
    rollback_parser.add_argument("--name", required=True, help="Model name")
    rollback_parser.add_argument("--version", required=True, help="Version to rollback to")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List versions")
    list_parser.add_argument("--name", required=True, help="Model name")
    list_parser.add_argument("--status", choices=["candidate", "production", "archived"], help="Filter by status")
    
    # Active command
    active_parser = subparsers.add_parser("active", help="Show active model")
    active_parser.add_argument("--name", required=True, help="Model name")
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show metrics")
    metrics_parser.add_argument("--name", required=True, help="Model name")
    metrics_parser.add_argument("--version", required=True, help="Version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    commands = {
        "register": cmd_register,
        "promote": cmd_promote,
        "rollback": cmd_rollback,
        "list": cmd_list,
        "active": cmd_active,
        "metrics": cmd_metrics
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
