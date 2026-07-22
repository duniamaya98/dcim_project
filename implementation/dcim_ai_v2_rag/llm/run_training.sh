#!/bin/bash
echo "=========================================================="
echo "🚀 STARTING DCIM AI FINE-TUNING PIPELINE"
echo "=========================================================="

echo "[1/3] Stopping llama-server to free up VRAM..."
sudo systemctl stop llama-server || { echo "Failed to stop llama-server. Are you sure it's running via systemd?"; }

# Wait for VRAM to clear
sleep 5

echo "[2/3] Running Quick Grid Search (Pre-split Dataset) on GPU 0..."
# Using the correct environment
/home/infra/rnd_rag-anything/ragavenv/bin/python3 finetune_proper.py --grid --quick

echo "[3/3] Restarting llama-server..."
sudo systemctl start llama-server || { echo "Failed to start llama-server. Please check systemctl status."; }

echo "=========================================================="
echo "✅ PIPELINE FINISHED"
echo "=========================================================="
