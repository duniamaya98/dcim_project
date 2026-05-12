# DCIM Model Benchmarking

**Purpose**: Performance testing and benchmarking for LLM models in DCIM AI Platform  
**Location**: `/home/infra/dcim_project/implementation/dcim_benchmark/`

---

## 📊 Overview

This folder contains benchmarking tools to measure and compare performance of different LLM models used in the DCIM AI platform. The benchmarks focus on key metrics relevant to production deployment.

---

## 🔧 Benchmarking Tools

### 1. **benchmark.py**
Basic latency and throughput benchmark for LLM inference.

**Metrics**:
- Latency (seconds)
- Tokens generated
- Tokens per second (throughput)

**Usage**:
```bash
python benchmark.py
```

**Configuration**:
- Default endpoint: `http://localhost:11434/api/generate`
- Default model: `mistral:7b`
- Test prompt: "Explain anomaly detection in data center"

---

### 2. **benchmark_context_length.py**
Tests model performance with varying context lengths.

**Purpose**: Measure how latency and throughput scale with input context size.

**Usage**:
```bash
python benchmark_context_length.py
```

**Test Cases**:
- Short context (< 512 tokens)
- Medium context (512-2048 tokens)
- Long context (2048-4096 tokens)
- Very long context (> 4096 tokens)

---

### 3. **benchmark_ttft.py**
Measures Time To First Token (TTFT) - critical for streaming responses.

**Metrics**:
- TTFT (milliseconds)
- Total generation time
- Streaming latency

**Usage**:
```bash
python benchmark_ttft.py
```

**Importance**: TTFT is crucial for user experience in interactive applications. Lower TTFT means faster perceived response time.

---

### 4. **load_test.py**
Concurrent load testing to measure system behavior under stress.

**Metrics**:
- Concurrent request handling
- Average latency under load
- Throughput degradation
- Error rate

**Usage**:
```bash
python load_test.py
```

**Test Scenarios**:
- 1 concurrent user (baseline)
- 5 concurrent users
- 10 concurrent users
- 20 concurrent users

---

### 5. **gpu_log.csv**
GPU utilization logs during benchmarking.

**Metrics Tracked**:
- GPU utilization (%)
- Memory usage (MB)
- Temperature (°C)
- Power consumption (W)
- Timestamp

**Collection Method**:
```bash
nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv --loop=1 > gpu_log.csv
```

---

### 6. **benchmark_comparation/**
Comparative analysis between different models and configurations.

**Contents**:
- Model comparison reports
- Performance charts
- Configuration impact analysis
- Optimization recommendations

---

## 🎯 Key Metrics

### Latency Metrics
- **TTFT (Time To First Token)**: Time until first token is generated
- **Total Latency**: End-to-end response time
- **Per-Token Latency**: Average time per token

### Throughput Metrics
- **Tokens/Second**: Generation speed
- **Requests/Second**: System throughput
- **Concurrent Capacity**: Max concurrent users

### Resource Metrics
- **GPU Utilization**: GPU usage percentage
- **VRAM Usage**: Memory consumption
- **CPU Usage**: CPU overhead
- **Power Consumption**: Energy efficiency

---

## 📈 Benchmark Results (Example)

### Model: Qwen2.5-3B-Instruct (4-bit)
```
Hardware: NVIDIA RTX 3070 Ti (8GB VRAM)
Context Length: 512 tokens
Batch Size: 1

Metrics:
- TTFT: 45ms
- Total Latency: 2.3s
- Throughput: 87 tokens/sec
- GPU Utilization: 78%
- VRAM Usage: 3.2GB
```

### Model: Mistral-7B (4-bit)
```
Hardware: NVIDIA RTX 3070 Ti (8GB VRAM)
Context Length: 512 tokens
Batch Size: 1

Metrics:
- TTFT: 68ms
- Total Latency: 3.8s
- Throughput: 52 tokens/sec
- GPU Utilization: 92%
- VRAM Usage: 5.8GB
```

---

## 🚀 Running Benchmarks

### Prerequisites
```bash
# Activate environment
source /home/infra/rnd_rag-anything/ragavenv/bin/activate

# Install dependencies
pip install requests numpy pandas matplotlib
```

### Quick Benchmark Suite
```bash
cd /home/infra/dcim_project/implementation/dcim_benchmark

# 1. Basic benchmark
python benchmark.py

# 2. Context length test
python benchmark_context_length.py

# 3. TTFT measurement
python benchmark_ttft.py

# 4. Load test
python load_test.py

# 5. Monitor GPU (in separate terminal)
nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv --loop=1 > gpu_log.csv
```

### With Shortcuts
```bash
# Load shortcuts
source /home/infra/dcim_project/dcim_shortcuts.sh

# Go to benchmark folder
dcim-benchmark

# Run benchmarks
python benchmark.py
```

---

## 📊 Benchmark Comparison

### Use Cases

#### 1. **Model Selection**
Compare different models to choose the best for production:
- Qwen2.5-3B vs Mistral-7B vs Llama-3-8B
- 4-bit vs 8-bit quantization
- LoRA adapter vs full fine-tune

#### 2. **Hardware Optimization**
Test performance on different hardware:
- Single GPU vs Multi-GPU
- Different GPU models (3070 Ti vs 4090)
- CPU inference vs GPU inference

#### 3. **Configuration Tuning**
Optimize inference parameters:
- Batch size impact
- Context length limits
- Temperature and sampling settings

#### 4. **Production Readiness**
Validate system can handle production load:
- Peak concurrent users
- Response time SLA compliance
- Resource utilization limits

---

## 🔍 Analysis Tools

### GPU Log Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load GPU logs
df = pd.read_csv('gpu_log.csv')

# Plot utilization over time
plt.plot(df['timestamp'], df['utilization.gpu [%]'])
plt.xlabel('Time')
plt.ylabel('GPU Utilization (%)')
plt.title('GPU Utilization During Benchmark')
plt.show()
```

### Performance Comparison
```python
# Compare models
models = {
    'Qwen2.5-3B': {'latency': 2.3, 'throughput': 87, 'vram': 3.2},
    'Mistral-7B': {'latency': 3.8, 'throughput': 52, 'vram': 5.8}
}

# Calculate efficiency score
for model, metrics in models.items():
    efficiency = metrics['throughput'] / metrics['vram']
    print(f"{model}: {efficiency:.2f} tokens/sec/GB")
```

---

## 📝 Best Practices

### 1. **Consistent Environment**
- Use same hardware for all benchmarks
- Close other GPU applications
- Monitor system temperature

### 2. **Multiple Runs**
- Run each benchmark 3-5 times
- Calculate mean and standard deviation
- Discard outliers

### 3. **Realistic Workloads**
- Use production-like prompts
- Test with actual DCIM queries
- Include edge cases

### 4. **Document Everything**
- Record hardware specs
- Note software versions
- Save configuration files

---

## 🎯 Integration with DCIM AI

### Model Selection for MT-023
Benchmarks help choose the best model for fine-tuning:
- **Qwen2.5-3B**: Selected for balance of speed and quality
- **Training Time**: ~1.6 hours on RTX 3070 Ti
- **Inference Speed**: 87 tokens/sec (production-ready)

### Production Deployment
Benchmark results inform deployment decisions:
- **Recommended**: Qwen2.5-3B-Instruct (4-bit)
- **Max Concurrent Users**: 10-15 (single GPU)
- **Response Time SLA**: < 3 seconds (95th percentile)

---

## 📞 Related Documentation

- **MT-023 Complete Guide**: `../dcim_ai_v2_rag/llm/MT-023_COMPLETE_DOCUMENTATION.md`
- **Model Registry**: `../dcim_ai_v2_rag/llm/model_registry_standalone.py`
- **Project README**: `/home/infra/dcim_project/README.md`

---

## 🔄 Future Enhancements

### Planned Features
- [ ] Automated benchmark suite
- [ ] Performance regression detection
- [ ] Multi-GPU benchmarking
- [ ] Cost-per-token analysis
- [ ] Quality vs speed tradeoff analysis

### Advanced Metrics
- [ ] Perplexity measurement
- [ ] BLEU/ROUGE scores
- [ ] Hallucination rate
- [ ] Domain accuracy

---

**Last Updated**: May 12, 2026  
**Status**: Active  
**Maintainer**: DCIM AI Platform Team
