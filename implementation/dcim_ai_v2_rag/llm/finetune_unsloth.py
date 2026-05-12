"""
MT-023 Task 3 — Fine-Tune dengan Unsloth (Optimized Version)

Versi optimized menggunakan Unsloth untuk training 2-3x lebih cepat
dengan VRAM 30-40% lebih efisien dibanding HuggingFace Transformers biasa.

Base model: Qwen/Qwen2.5-3B-Instruct
Method: LoRA with Unsloth optimization
Dataset: dcim_ai/llm/datasets/dcim_instructions.jsonl

Advantages over standard HF:
- 2-3x faster training
- 30-40% less VRAM usage
- Built-in GGUF export
- Optimized gradient checkpointing
- Better packing

Hardware requirement:
- 1x RTX 3070 Ti (8GB VRAM) — cukup untuk 3B model + LoRA

Usage:
    # Basic
    python -m dcim_ai.llm.finetune_unsloth

    # Custom settings
    python -m dcim_ai.llm.finetune_unsloth \
        --max-steps 645 \
        --batch-size 2 \
        --gpu 0 \
        --export-gguf

    # Compare with HF version
    python -m dcim_ai.llm.finetune_unsloth --max-steps 100
    python -m dcim_ai.llm.finetune_qlora --epochs 1 --batch-size 1
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =====================================================
# CONFIGURATION
# =====================================================

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "dcim_instructions.jsonl"
OUTPUT_BASE = Path(__file__).resolve().parent / "models"

# Model configuration
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# LoRA config (optimized for Unsloth)
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0  # Unsloth optimal at 0
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]

# Training defaults (optimized for Unsloth)
DEFAULT_MAX_STEPS = 645  # ~3 epochs for 3,816 samples with batch=2, accum=8
DEFAULT_BATCH_SIZE = 2   # Can be higher with Unsloth
DEFAULT_GRAD_ACCUM = 8   # Can be lower with Unsloth
DEFAULT_LR = 2e-4
DEFAULT_MAX_SEQ_LEN = 512
DEFAULT_WARMUP_STEPS = 50
DEFAULT_GPU = 0

# =====================================================
# DATASET FORMATTING
# =====================================================

def format_dcim_chat_template(examples, tokenizer):
    """
    Format DCIM instruction dataset using chat template.
    Converts {instruction, input, output} to chat format.
    """
    texts = []
    
    for instruction, input_text, output in zip(
        examples["instruction"], 
        examples["input"], 
        examples["output"]
    ):
        # Build messages
        messages = [
            {
                "role": "system", 
                "content": (
                    "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis "
                    "infrastruktur data center. Kamu memahami anomaly detection, drift analysis, "
                    "root cause analysis, dan domain correlation pada sistem DCIM. "
                    "Jawab dalam Bahasa Indonesia yang jelas dan teknis."
                )
            },
            {
                "role": "user", 
                "content": f"{instruction}\n\n{input_text}" if input_text else instruction
            },
            {
                "role": "assistant", 
                "content": output
            }
        ]
        
        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)
    
    return {"text": texts}

# =====================================================
# MAIN TRAINING
# =====================================================

def train(args):
    import torch
    from unsloth import FastLanguageModel
    from trl import SFTTrainer, SFTConfig
    from datasets import load_dataset
    
    # ─── GPU Setup ───
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    
    print("=" * 70)
    print("🦥 MT-023 Task 3 — Fine-Tune DCIM AI Assistant (Unsloth Optimized)")
    print("=" * 70)
    print(f"Base model: {BASE_MODEL}")
    print(f"GPU: {args.gpu}")
    print(f"Max steps: {args.max_steps}")
    print(f"Batch size: {args.batch_size} × {args.grad_accum} = {args.batch_size * args.grad_accum}")
    print(f"Learning rate: {args.lr}")
    print(f"Max seq len: {args.max_seq_len}")
    print(f"LoRA r={LORA_R}, alpha={LORA_ALPHA}, dropout={LORA_DROPOUT}")
    print(f"Optimization: Unsloth (2-3x faster, 30-40% less VRAM)")
    print()
    
    # ─── Version ───
    version = args.version or f"v{datetime.now().strftime('%Y%m%d_%H%M')}_unsloth"
    output_dir = OUTPUT_BASE / version
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OUTPUT] {output_dir}")
    
    # ─── Load Model with Unsloth ───
    print("\n[1/6] Loading model with Unsloth optimization...")
    start_time = time.time()
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=args.max_seq_len,
        load_in_4bit=True,
        dtype=None,  # Auto-detect
    )
    
    load_time = time.time() - start_time
    print(f"   ✅ Model loaded in {load_time:.1f}s")
    
    # ─── Add LoRA with Unsloth ───
    print(f"\n[2/6] Adding LoRA adapters (r={LORA_R}, alpha={LORA_ALPHA})...")
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        use_gradient_checkpointing="unsloth",  # Unsloth optimized
        random_state=3407,
    )
    
    print("   ✅ LoRA adapters added")
    
    # ─── Load Dataset ───
    print(f"\n[3/6] Loading dataset: {DATASET_PATH.name}")
    
    dataset = load_dataset("json", data_files=str(DATASET_PATH), split="train")
    print(f"   Total samples: {len(dataset):,}")
    
    # Format dataset with chat template
    print("   Formatting with chat template...")
    dataset = dataset.map(
        lambda x: format_dcim_chat_template(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names,
    )
    
    # Split train/eval
    dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]
    
    print(f"   Train samples: {len(train_dataset):,}")
    print(f"   Eval samples: {len(eval_dataset):,}")
    print(f"   Example length: {len(train_dataset[0]['text'])} chars")
    
    # ─── Training Configuration ───
    print(f"\n[4/6] Configuring trainer...")
    
    # Calculate effective batch size
    effective_batch = args.batch_size * args.grad_accum
    print(f"   Effective batch size: {effective_batch}")
    print(f"   Estimated steps per epoch: {len(train_dataset) // effective_batch}")
    
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=SFTConfig(
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.grad_accum,
            max_steps=args.max_steps,
            learning_rate=args.lr,
            warmup_steps=args.warmup_steps,
            
            # Precision
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            
            # Logging & Saving
            output_dir=str(output_dir),
            logging_steps=10,
            save_steps=args.save_steps,
            eval_steps=args.save_steps,
            
            # Dataset config
            dataset_text_field="text",
            max_seq_length=args.max_seq_len,
            packing=True,  # Unsloth optimization
            
            # Optimization
            optim="adamw_8bit",  # Memory efficient
            weight_decay=0.01,
            lr_scheduler_type="linear",
            
            seed=3407,
        ),
    )
    
    print("   ✅ Trainer configured")
    
    # ─── Train ───
    print(f"\n[5/6] Training (max_steps={args.max_steps})...")
    print("   This will be 2-3x faster than standard HuggingFace!")
    print()
    
    train_start = time.time()
    stats = trainer.train()
    train_time = time.time() - train_start
    
    print()
    print(f"   ✅ Training complete!")
    print(f"   Final loss: {stats.training_loss:.4f}")
    print(f"   Training time: {train_time:.1f}s ({train_time/60:.1f} min)")
    print(f"   Throughput: {len(train_dataset) * (args.max_steps / (len(train_dataset) // effective_batch)) / train_time:.2f} samples/sec")
    
    # ─── Save ───
    print(f"\n[6/6] Saving model...")
    
    # Save LoRA adapter
    adapter_dir = output_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"   ✅ LoRA adapter saved: {adapter_dir}")
    
    # Save metadata
    metadata = {
        "version": version,
        "base_model": BASE_MODEL,
        "method": "LoRA with Unsloth",
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_dropout": LORA_DROPOUT,
        "lora_target_modules": LORA_TARGET_MODULES,
        "max_steps": args.max_steps,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "effective_batch_size": effective_batch,
        "learning_rate": args.lr,
        "max_seq_len": args.max_seq_len,
        "dataset": str(DATASET_PATH),
        "dataset_size": len(dataset),
        "train_size": len(train_dataset),
        "eval_size": len(eval_dataset),
        "train_loss": stats.training_loss,
        "train_runtime_seconds": train_time,
        "created_at": datetime.now().isoformat(),
        "gpu": f"GPU {args.gpu}",
        "optimization": "Unsloth (2-3x faster)",
    }
    
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Metadata saved: {output_dir / 'metadata.json'}")
    
    # ─── Export GGUF (Optional) ───
    if args.export_gguf:
        print(f"\n[BONUS] Exporting to GGUF...")
        gguf_dir = output_dir / "gguf"
        
        try:
            model.save_pretrained_gguf(
                str(gguf_dir),
                tokenizer,
                quantization_method=args.gguf_quant
            )
            print(f"   ✅ GGUF exported: {gguf_dir}")
            print(f"   Quantization: {args.gguf_quant}")
        except Exception as e:
            print(f"   ⚠️  GGUF export failed: {e}")
            print(f"   You can export manually later with export_gguf.py")
    
    # ─── Summary ───
    print()
    print("=" * 70)
    print("✅ Fine-tuning complete!")
    print("=" * 70)
    print(f"Model version: {version}")
    print(f"Adapter location: {adapter_dir}")
    print(f"Training time: {train_time/60:.1f} minutes")
    print(f"Final loss: {stats.training_loss:.4f}")
    print()
    print("Next steps:")
    print(f"  1. Evaluate: python -m dcim_ai.llm.evaluate_model --adapter {adapter_dir}")
    print(f"  2. Register: python -m dcim_ai.llm.model_registry register --name dcim_assistant --version {version} --adapter-path {adapter_dir}")
    if args.export_gguf:
        print(f"  3. Deploy: llama-server -m {gguf_dir}/unsloth.Q8_0.gguf")
    print("=" * 70)

# =====================================================
# CLI
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="MT-023 Fine-Tuning with Unsloth")
    
    # Training config
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS,
                        help=f"Max training steps (default: {DEFAULT_MAX_STEPS})")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help=f"Per-device batch size (default: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--grad-accum", type=int, default=DEFAULT_GRAD_ACCUM,
                        help=f"Gradient accumulation steps (default: {DEFAULT_GRAD_ACCUM})")
    parser.add_argument("--lr", type=float, default=DEFAULT_LR,
                        help=f"Learning rate (default: {DEFAULT_LR})")
    parser.add_argument("--max-seq-len", type=int, default=DEFAULT_MAX_SEQ_LEN,
                        help=f"Max sequence length (default: {DEFAULT_MAX_SEQ_LEN})")
    parser.add_argument("--warmup-steps", type=int, default=DEFAULT_WARMUP_STEPS,
                        help=f"Warmup steps (default: {DEFAULT_WARMUP_STEPS})")
    parser.add_argument("--save-steps", type=int, default=100,
                        help="Save checkpoint every N steps (default: 100)")
    
    # System config
    parser.add_argument("--gpu", type=int, default=DEFAULT_GPU,
                        help=f"GPU device ID (default: {DEFAULT_GPU})")
    parser.add_argument("--version", type=str, default=None,
                        help="Model version name (default: auto-generated)")
    
    # Export options
    parser.add_argument("--export-gguf", action="store_true",
                        help="Export to GGUF format after training")
    parser.add_argument("--gguf-quant", type=str, default="q8_0",
                        choices=["q4_k_m", "q5_k_m", "q8_0", "f16"],
                        help="GGUF quantization method (default: q8_0)")
    
    args = parser.parse_args()
    
    # Validate
    if not DATASET_PATH.exists():
        print(f"❌ Dataset not found: {DATASET_PATH}")
        print("   Run: python -m dcim_ai.llm.dataset_generator")
        sys.exit(1)
    
    # Check Unsloth installation
    try:
        import unsloth
        print(f"✅ Unsloth version: {unsloth.__version__}")
    except ImportError:
        print("❌ Unsloth not installed!")
        print("   Install: pip install 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'")
        sys.exit(1)
    
    # Train
    train(args)

if __name__ == "__main__":
    main()
