"""
MT-023 Task 4 — LLM Model Registry (Standalone Version)

Manage fine-tuned LLM model versions with production/candidate status,
version control, and rollback capability.

Usage:
    # Register new model
    python model_registry_standalone.py register \
        --name dcim_assistant \
        --version v1.0 \
        --adapter-path /path/to/adapter

    # Promote to production
    python model_registry_standalone.py promote \
        --name dcim_assistant \
        --version v1.0

    # List versions
    python model_registry_standalone.py list --name dcim_assistant

    # Get active model
    python model_registry_standalone.py active --name dcim_assistant
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'dcim_ai',
    'user': 'infra',
    'password': 'StrongPassword123'
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

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
        adapter_path: Path to LoRA adapter directory
        metrics: Dict with training metrics (loss, dataset_size, epochs, etc.)
        notes: Optional notes about this version
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if version already exists
        cur.execute("""
            SELECT id FROM llm_model_registry 
            WHERE model_name = %s AND version = %s
        """, (model_name, version))
        
        if cur.fetchone():
            print(f"❌ Model {model_name} {version} already registered")
            return False
        
        # Insert new model as candidate
        cur.execute("""
            INSERT INTO llm_model_registry 
            (model_name, version, base_model, adapter_path, status, metrics_json, notes)
            VALUES (%s, %s, %s, %s, 'candidate', %s, %s)
            RETURNING id
        """, (model_name, version, base_model, adapter_path, json.dumps(metrics), notes))
        
        model_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Registered {model_name} {version} (ID: {model_id})")
        print(f"   Status: candidate")
        print(f"   Base Model: {base_model}")
        print(f"   Adapter: {adapter_path}")
        print(f"   Metrics: {metrics}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error registering model: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def promote_to_production(model_name, version):
    """
    Promote model version to production (deactivate others)
    
    Args:
        model_name: Model identifier
        version: Version to promote
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if version exists
        cur.execute("""
            SELECT id, status FROM llm_model_registry 
            WHERE model_name = %s AND version = %s
        """, (model_name, version))
        
        result = cur.fetchone()
        if not result:
            print(f"❌ Model {model_name} {version} not found")
            return False
        
        model_id, current_status = result
        
        if current_status == 'production':
            print(f"ℹ️  Model {model_name} {version} already in production")
            return True
        
        # Deactivate all other versions
        cur.execute("""
            UPDATE llm_model_registry 
            SET is_active = FALSE, status = 'archived'
            WHERE model_name = %s AND is_active = TRUE
        """, (model_name,))
        
        # Activate this version
        cur.execute("""
            UPDATE llm_model_registry 
            SET status = 'production', is_active = TRUE, activated_at = NOW()
            WHERE id = %s
        """, (model_id,))
        
        conn.commit()
        
        print(f"✅ Promoted {model_name} {version} to production")
        print(f"   Previous active versions archived")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error promoting model: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def list_models(model_name=None):
    """
    List all model versions
    
    Args:
        model_name: Optional filter by model name
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if model_name:
            cur.execute("""
                SELECT * FROM llm_model_registry 
                WHERE model_name = %s 
                ORDER BY created_at DESC
            """, (model_name,))
        else:
            cur.execute("""
                SELECT * FROM llm_model_registry 
                ORDER BY model_name, created_at DESC
            """)
        
        models = cur.fetchall()
        
        if not models:
            print(f"No models found{' for ' + model_name if model_name else ''}")
            return
        
        print(f"\n{'='*80}")
        print(f"LLM Model Registry{' - ' + model_name if model_name else ''}")
        print(f"{'='*80}\n")
        
        for model in models:
            status_icon = "🟢" if model['is_active'] else "⚪"
            print(f"{status_icon} {model['model_name']} {model['version']}")
            print(f"   Status: {model['status']}")
            print(f"   Base Model: {model['base_model']}")
            print(f"   Adapter: {model['adapter_path']}")
            
            # Parse metrics
            if model['metrics_json']:
                if isinstance(model['metrics_json'], dict):
                    metrics = model['metrics_json']
                else:
                    metrics = json.loads(model['metrics_json'])
                print(f"   Metrics: loss={metrics.get('loss', 'N/A')}, "
                      f"dataset_size={metrics.get('dataset_size', 'N/A')}, "
                      f"epochs={metrics.get('epochs', 'N/A')}")
            
            print(f"   Registered: {model['created_at']}")
            if model['activated_at']:
                print(f"   Activated: {model['activated_at']}")
            if model['notes']:
                print(f"   Notes: {model['notes']}")
            print()
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    finally:
        cur.close()
        conn.close()


def get_active_model(model_name):
    """
    Get currently active production model
    
    Args:
        model_name: Model identifier
    
    Returns:
        Dict with model info or None
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT * FROM llm_model_registry 
            WHERE model_name = %s AND is_active = TRUE
            LIMIT 1
        """, (model_name,))
        
        model = cur.fetchone()
        
        if not model:
            print(f"❌ No active model found for {model_name}")
            return None
        
        print(f"\n{'='*80}")
        print(f"Active Model: {model['model_name']} {model['version']}")
        print(f"{'='*80}\n")
        print(f"Status: {model['status']}")
        print(f"Base Model: {model['base_model']}")
        print(f"Adapter Path: {model['adapter_path']}")
        
        # Parse metrics
        if model['metrics_json']:
            if isinstance(model['metrics_json'], dict):
                metrics = model['metrics_json']
            else:
                metrics = json.loads(model['metrics_json'])
            print(f"\nTraining Metrics:")
            print(f"  Loss: {metrics.get('loss', 'N/A')}")
            print(f"  Dataset Size: {metrics.get('dataset_size', 'N/A')}")
            print(f"  Epochs: {metrics.get('epochs', 'N/A')}")
            print(f"  Train Samples: {metrics.get('train_samples', 'N/A')}")
            print(f"  Eval Samples: {metrics.get('eval_samples', 'N/A')}")
        
        print(f"\nRegistered: {model['created_at']}")
        print(f"Activated: {model['activated_at']}")
        
        if model['notes']:
            print(f"\nNotes: {model['notes']}")
        
        print()
        
        return dict(model)
        
    except Exception as e:
        print(f"❌ Error getting active model: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def rollback_version(model_name, version):
    """
    Rollback to previous version
    
    Args:
        model_name: Model identifier
        version: Version to rollback to
    """
    print(f"Rolling back {model_name} to {version}...")
    return promote_to_production(model_name, version)


# =====================================================
# CLI
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="LLM Model Registry Management")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register new model version')
    register_parser.add_argument('--name', required=True, help='Model name')
    register_parser.add_argument('--version', required=True, help='Version (e.g., v1.0)')
    register_parser.add_argument('--base-model', default='Qwen/Qwen2.5-3B-Instruct', 
                                help='Base model name')
    register_parser.add_argument('--adapter-path', required=True, help='Path to adapter')
    register_parser.add_argument('--loss', type=float, help='Training loss')
    register_parser.add_argument('--dataset-size', type=int, help='Dataset size')
    register_parser.add_argument('--epochs', type=int, help='Number of epochs')
    register_parser.add_argument('--notes', help='Optional notes')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote to production')
    promote_parser.add_argument('--name', required=True, help='Model name')
    promote_parser.add_argument('--version', required=True, help='Version to promote')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List model versions')
    list_parser.add_argument('--name', help='Filter by model name')
    
    # Active command
    active_parser = subparsers.add_parser('active', help='Show active model')
    active_parser.add_argument('--name', required=True, help='Model name')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to version')
    rollback_parser.add_argument('--name', required=True, help='Model name')
    rollback_parser.add_argument('--version', required=True, help='Version to rollback to')
    
    args = parser.parse_args()
    
    if args.command == 'register':
        metrics = {}
        if args.loss:
            metrics['loss'] = args.loss
        if args.dataset_size:
            metrics['dataset_size'] = args.dataset_size
        if args.epochs:
            metrics['epochs'] = args.epochs
        
        register_llm_model(
            args.name, args.version, args.base_model, 
            args.adapter_path, metrics, args.notes
        )
    
    elif args.command == 'promote':
        promote_to_production(args.name, args.version)
    
    elif args.command == 'list':
        list_models(args.name)
    
    elif args.command == 'active':
        get_active_model(args.name)
    
    elif args.command == 'rollback':
        rollback_version(args.name, args.version)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
