"""
MT-023 Task 3 — Fine-Tune Qwen2.5-7B-Instruct-AWQ dengan LoRA

Base model: Qwen/Qwen2.5-7B-Instruct-AWQ (4-bit AWQ, sudah lokal)
Method: LoRA on AWQ (tidak perlu QLoRA karena model sudah 4-bit)
Dataset: dcim_ai/llm/datasets/dcim_instructions.jsonl

Hardware requirement:
- 1x RTX 3070 Ti (8GB VRAM) — cukup untuk AWQ 4-bit + LoRA
- Stop llama-server dulu jika GPU penuh

Usage:
    python -m dcim_ai.llm.finetune_qlora
    python -m dcim_ai.llm.finetune_qlora --epochs 3 --batch-size 2 --gpu 0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "dcim_instructions.jsonl"
OUTPUT_BASE = Path(__file__).resolve().parent / "models"

# Model — QLoRA 4-bit via BitsAndBytes
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# LoRA config
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]

# Training defaults
DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 1
DEFAULT_GRAD_ACCUM = 16  # effective batch = 1 * 16 = 16
DEFAULT_LR = 2e-4
DEFAULT_MAX_SEQ_LEN = 512
DEFAULT_WARMUP_RATIO = 0.05
DEFAULT_GPU = 0


# =====================================================
# DATASET LOADING
# =====================================================

def load_dataset_from_jsonl(path, max_seq_len=1024):
    """Load instruction dataset and format for training"""
    from datasets import Dataset

    records = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                records.append({
                    "instruction": r["instruction"],
                    "input": r["input"],
                    "output": r["output"],
                })

    print(f"[DATA] Loaded {len(records)} instruction samples")

    dataset = Dataset.from_list(records)
    return dataset


def format_chat_template(example, tokenizer):
    """Format as Qwen2.5 chat template"""
    messages = [
        {"role": "system", "content": (
            "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis "
            "infrastruktur data center. Kamu memahami anomaly detection, drift analysis, "
            "root cause analysis, dan domain correlation pada sistem DCIM. "
            "Jawab dalam Bahasa Indonesia yang jelas dan teknis."
        )},
        {"role": "user", "content": f"{example['instruction']}\n\n{example['input']}"},
        {"role": "assistant", "content": example["output"]}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    return {"text": text}


# =====================================================
# MAIN TRAINING
# =====================================================

def train(args):
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

    # ─── GPU Setup ───
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    device = torch.device("cuda:0")

    print("=" * 60)
    print("MT-023 Task 3 — Fine-Tune DCIM AI Assistant (QLoRA)")
    print("=" * 60)
    print(f"Base model: {BASE_MODEL}")
    print(f"GPU: {args.gpu}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size} × {args.grad_accum} = {args.batch_size * args.grad_accum}")
    print(f"Learning rate: {args.lr}")
    print(f"Max seq len: {args.max_seq_len}")
    print(f"LoRA r={LORA_R}, alpha={LORA_ALPHA}")
    print()

    # ─── Version ───
    version = args.version or f"v{datetime.now().strftime('%Y%m%d_%H%M')}"
    output_dir = OUTPUT_BASE / version
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OUTPUT] {output_dir}")

    # ─── Load Tokenizer ───
    print("\n[1/5] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        trust_remote_code=True,
        padding_side="right"
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # ─── QLoRA 4-bit Config ───
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    # ─── Load Model ───
    print("[2/5] Loading model with 4-bit quantization...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map={"": device},
        trust_remote_code=True,
    )

    # Prepare for LoRA training
    model = prepare_model_for_kbit_training(model)

    # ─── LoRA Config ───
    print("[3/5] Applying LoRA...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ─── Load Dataset ───
    print("[4/5] Loading dataset...")
    dataset = load_dataset_from_jsonl(DATASET_PATH, max_seq_len=args.max_seq_len)

    # Format with chat template
    dataset = dataset.map(
        lambda x: format_chat_template(x, tokenizer),
        remove_columns=dataset.column_names
    )

    # Train/eval split
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]

    print(f"[DATA] Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")

    # ─── Training Args (SFTConfig for trl>=1.0) ───
    from trl import SFTConfig

    training_args = SFTConfig(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        weight_decay=0.01,
        warmup_ratio=DEFAULT_WARMUP_RATIO,
        lr_scheduler_type="cosine",
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        fp16=False,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        optim="paged_adamw_8bit",
        max_grad_norm=0.3,
        report_to="none",
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        max_length=args.max_seq_len,
        packing=False,
    )

    # ─── Trainer ───
    print("[5/5] Starting training...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
    )

    # Train
    print()
    train_result = trainer.train()

    # ─── Save ───
    print("\n[SAVE] Saving LoRA adapter...")
    adapter_path = output_dir / "adapter"
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))

    # Save metadata
    metadata = {
        "version": version,
        "base_model": BASE_MODEL,
        "method": "LoRA on AWQ",
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_target_modules": LORA_TARGET_MODULES,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "effective_batch_size": args.batch_size * args.grad_accum,
        "learning_rate": args.lr,
        "max_seq_len": args.max_seq_len,
        "dataset": str(DATASET_PATH),
        "dataset_size": len(dataset),
        "train_size": len(train_dataset),
        "eval_size": len(eval_dataset),
        "train_loss": train_result.training_loss,
        "train_runtime_seconds": train_result.metrics.get("train_runtime", 0),
        "created_at": datetime.now().isoformat(),
        "gpu": f"RTX 3070 Ti (GPU {args.gpu})",
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Save training metrics
    with open(output_dir / "train_metrics.json", "w") as f:
        json.dump(train_result.metrics, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"[DONE] Training complete!")
    print(f"  Adapter: {adapter_path}")
    print(f"  Metadata: {output_dir / 'metadata.json'}")
    print(f"  Loss: {train_result.training_loss:.4f}")
    print(f"  Runtime: {train_result.metrics.get('train_runtime', 0):.0f}s")
    print(f"{'=' * 60}")

    return output_dir


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune DCIM AI Assistant")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--grad-accum", type=int, default=DEFAULT_GRAD_ACCUM)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--max-seq-len", type=int, default=DEFAULT_MAX_SEQ_LEN)
    parser.add_argument("--gpu", type=int, default=DEFAULT_GPU)
    parser.add_argument("--version", type=str, default=None)

    args = parser.parse_args()
    train(args)
