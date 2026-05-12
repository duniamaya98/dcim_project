import os
import json
import time
import threading
import joblib

REGISTRY_PATH = "dcim_ai/registry/registry.json"
MODELS_DIR = "dcim_ai/artifacts/models"


class ModelManager:
    def __init__(self, check_interval=10):
        self.check_interval = check_interval
        self.current_version = None
        self.models = None
        self.pipeline = None
        self.baseline_stats = None
        self.correlation_config = {}
        self.lock = threading.Lock()

        self.load_model()
        threading.Thread(target=self.watch_registry, daemon=True).start()

    def get_registry_data(self):
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)

    def load_model(self):
        registry = self.get_registry_data()
        version = registry.get("current_production")
        correlation_config = registry.get("correlation_config", {})

        model_dir = os.path.join(MODELS_DIR, version)

        models = joblib.load(os.path.join(model_dir, "models.pkl"))
        pipeline = joblib.load(os.path.join(model_dir, "pipeline.pkl"))

        with open(os.path.join(model_dir, "baseline_stats.json"), "r") as f:
            baseline_stats = json.load(f)

        with self.lock:
            self.models = models
            self.pipeline = pipeline
            self.baseline_stats = baseline_stats
            self.current_version = version
            self.correlation_config = correlation_config

        print(f"[HOT-RELOAD] Active model: {version}")
        print(f"[HOT-RELOAD] Correlation config: {correlation_config}")

    def watch_registry(self):
        while True:
            time.sleep(self.check_interval)
            try:
                registry = self.get_registry_data()
                version = registry.get("current_production")

                if version != self.current_version:
                    print(f"[HOT-RELOAD] New production model detected: {version}")
                    self.load_model()

            except Exception as e:
                print("[HOT-RELOAD-ERROR]", e)

    def get(self):
        with self.lock:
            return (
                self.models,
                self.pipeline,
                self.baseline_stats,
                self.current_version,
                self.correlation_config
            )