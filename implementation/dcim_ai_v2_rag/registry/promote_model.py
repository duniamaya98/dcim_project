import os
import json
import sys

REGISTRY_PATH = "dcim_ai/registry/registry.json"
MODELS_DIR = "dcim_ai/artifacts/models"


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        raise Exception("Registry file not found.")

    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=4)


def update_model_status(version, new_status):
    metadata_path = os.path.join(MODELS_DIR, version, "metadata.json")

    if not os.path.exists(metadata_path):
        raise Exception(f"Metadata not found for version {version}")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    metadata["status"] = new_status

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)


def promote_model(target_version):
    registry = load_registry()

    if target_version not in registry["available_models"]:
        raise Exception(f"Version {target_version} not found in registry.")

    current_prod = registry["current_production"]

    if current_prod == target_version:
        print(f"{target_version} is already in production.")
        return

    # Downgrade current production
    if current_prod is not None:
        update_model_status(current_prod, "archived")

    # Promote new version
    update_model_status(target_version, "production")
    registry["current_production"] = target_version

    # Ensure correlation config exists
    registry.setdefault("correlation_config", {
        "correlation_version": "c1.0",
        "correlation_strategy": "temporal_multi_domain_v1",
        "severity_matrix_version": "sm1.0"
    })

    save_registry(registry)

    print(f"Model {target_version} promoted to production successfully.")
    print(f"Correlation strategy: {registry['correlation_config']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m dcim_ai.registry.promote_model <version>")
        sys.exit(1)

    version = sys.argv[1]
    promote_model(version)