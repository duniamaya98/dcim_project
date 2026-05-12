import os
import json
import joblib

REGISTRY_PATH = "dcim_ai/registry/registry.json"
MODELS_DIR = "dcim_ai/artifacts/models"


def load_production_model():
    if not os.path.exists(REGISTRY_PATH):
        raise Exception("Registry file not found.")

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    current_version = registry.get("current_production")

    if not current_version:
        raise Exception("No production model set.")

    model_dir = os.path.join(MODELS_DIR, current_version)

    try:
        models = joblib.load(os.path.join(model_dir, "models.pkl"))
        pipeline = joblib.load(os.path.join(model_dir, "pipeline.pkl"))

        with open(os.path.join(model_dir, "baseline_stats.json"), "r") as f:
            baseline_stats = json.load(f)

        print(f"Loaded production model: {current_version}")
        return models, pipeline, baseline_stats, current_version

    except Exception as e:
        raise Exception(f"Failed to load production model: {e}")