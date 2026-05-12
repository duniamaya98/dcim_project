"""
MT-023 Task 4 — Export Fine-Tuned Model ke GGUF

Merge LoRA adapter dengan base model, lalu convert ke GGUF
untuk deployment via llama.cpp / Ollama.

Usage:
    # Step 1: Merge adapter
    python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step merge

    # Step 2: Convert ke GGUF (requires llama.cpp convert script)
    python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step convert

    # Step 3: Quantize (optional, model sudah dari AWQ)
    python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step quantize

    # All steps
    python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step all
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LLAMA_CPP_DIR = PROJECT_ROOT.parent / "llama.cpp"  # /home/infra/rnd_rag-anything/llama.cpp
BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct-AWQ"


def merge_adapter(adapter_path, output_path):
    """Merge LoRA adapter with base model into full model"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print("[MERGE] Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="cpu",  # merge on CPU to save VRAM
        trust_remote_code=True,
    )

    print(f"[MERGE] Loading adapter from {adapter_path}...")
    model = PeftModel.from_pretrained(base_model, adapter_path)

    print("[MERGE] Merging weights...")
    model = model.merge_and_unload()

    print(f"[MERGE] Saving merged model to {output_path}...")
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(str(output_path))

    # Copy tokenizer
    tokenizer = AutoTokenizer.from_pretrained(adapter_path, trust_remote_code=True)
    tokenizer.save_pretrained(str(output_path))

    print(f"[MERGE] Done! Merged model at: {output_path}")
    return output_path


def convert_to_gguf(merged_path, output_gguf):
    """Convert HF model to GGUF using llama.cpp convert script"""

    convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"

    if not convert_script.exists():
        # Try alternative location
        alt = Path("/home/infra/llama.cpp/convert_hf_to_gguf.py")
        if alt.exists():
            convert_script = alt
        else:
            print(f"[ERROR] convert_hf_to_gguf.py not found at:")
            print(f"  {convert_script}")
            print(f"  {alt}")
            print("Install llama.cpp first: git clone https://github.com/ggml-org/llama.cpp")
            return None

    print(f"[CONVERT] Using: {convert_script}")
    print(f"[CONVERT] Input: {merged_path}")
    print(f"[CONVERT] Output: {output_gguf}")

    cmd = [
        sys.executable, str(convert_script),
        str(merged_path),
        "--outfile", str(output_gguf),
        "--outtype", "f16",
    ]

    print(f"[CONVERT] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Conversion failed:")
        print(result.stderr)
        return None

    print(f"[CONVERT] Done! GGUF at: {output_gguf}")
    return output_gguf


def quantize_gguf(input_gguf, output_gguf, quant_type="Q4_K_M"):
    """Quantize GGUF model using llama.cpp quantize tool"""

    quantize_bin = LLAMA_CPP_DIR / "build" / "bin" / "llama-quantize"

    if not quantize_bin.exists():
        alt = Path("/home/infra/llama.cpp/build/bin/llama-quantize")
        if alt.exists():
            quantize_bin = alt
        else:
            print(f"[ERROR] llama-quantize not found. Build llama.cpp first.")
            return None

    print(f"[QUANTIZE] {quant_type}: {input_gguf} → {output_gguf}")

    cmd = [str(quantize_bin), str(input_gguf), str(output_gguf), quant_type]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Quantization failed:")
        print(result.stderr)
        return None

    print(f"[QUANTIZE] Done! {output_gguf}")
    return output_gguf


def create_ollama_modelfile(gguf_path, output_path):
    """Create Ollama Modelfile for easy deployment"""

    modelfile_content = f"""FROM {gguf_path}

SYSTEM \"\"\"Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis infrastruktur data center. Kamu memahami anomaly detection, drift analysis, root cause analysis, dan domain correlation pada sistem DCIM. Jawab dalam Bahasa Indonesia yang jelas dan teknis.\"\"\"

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_predict 512
"""

    modelfile_path = Path(output_path) / "Modelfile"
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)

    print(f"[OLLAMA] Modelfile created: {modelfile_path}")
    print(f"[OLLAMA] Deploy with: ollama create dcim-ai -f {modelfile_path}")
    return modelfile_path


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export fine-tuned model to GGUF")
    parser.add_argument("--adapter", type=str, required=True, help="Path to LoRA adapter")
    parser.add_argument("--step", type=str, default="all",
                        choices=["merge", "convert", "quantize", "all"],
                        help="Which step to run")
    parser.add_argument("--quant", type=str, default="Q4_K_M",
                        help="Quantization type (Q4_K_M, Q5_K_M, Q8_0)")
    parser.add_argument("--gpu", type=int, default=0)

    args = parser.parse_args()

    adapter_path = Path(args.adapter)
    version_dir = adapter_path.parent  # e.g., dcim_ai/llm/models/v1.0/

    merged_path = version_dir / "merged"
    gguf_f16 = version_dir / "dcim-ai-f16.gguf"
    gguf_quant = version_dir / f"dcim-ai-{args.quant}.gguf"

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    if args.step in ("merge", "all"):
        merge_adapter(str(adapter_path), str(merged_path))

    if args.step in ("convert", "all"):
        convert_to_gguf(str(merged_path), str(gguf_f16))

    if args.step in ("quantize", "all"):
        if gguf_f16.exists():
            quantize_gguf(str(gguf_f16), str(gguf_quant), args.quant)
            create_ollama_modelfile(str(gguf_quant), str(version_dir))
        else:
            print(f"[SKIP] F16 GGUF not found: {gguf_f16}")

    # Summary
    print(f"\n{'=' * 60}")
    print("EXPORT SUMMARY")
    print(f"{'=' * 60}")
    for f in [merged_path, gguf_f16, gguf_quant]:
        if Path(f).exists():
            if Path(f).is_dir():
                size = sum(p.stat().st_size for p in Path(f).rglob("*")) / 1024 / 1024
            else:
                size = Path(f).stat().st_size / 1024 / 1024
            print(f"  ✅ {f} ({size:.0f} MB)")
        else:
            print(f"  ❌ {f} (not created)")
