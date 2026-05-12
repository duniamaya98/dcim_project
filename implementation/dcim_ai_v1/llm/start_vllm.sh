#!/bin/bash

# Configuration
MODEL="casperhansen/llama-3-8b-instruct-awq"
QUANTIZATION="awq"
TP_SIZE=2
PORT=8000

echo "Starting vLLM Inference Server with $MODEL..."
echo "Using $TP_SIZE GPUs for Tensor Parallelism"

python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL \
    --quantization $QUANTIZATION \
    --tensor-parallel-size $TP_SIZE \
    --port $PORT \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192
