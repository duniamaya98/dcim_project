import subprocess

def trigger_retraining():
    print("[AUTO RETRAIN] Starting retraining process...")
    subprocess.Popen(["python", "-m", "dcim_ai.training.train_anomaly_model"])
