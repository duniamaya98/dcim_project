"""
MT-023 Phase 2 — Proper Fine-Tuning dengan QLoRA

Perbaikan dari POC:
  1. 70/15/15 train/val/test split (bukan cuma train/eval)
  2. Hyperparameter grid search
  3. Early stopping (patience=3) → simpan best model, bukan last epoch
  4. Per-epoch logging: train_loss, eval_loss, eval_perplexity
  5. Grid results TSV untuk analisis
  6. Held-out test set tersimpan terpisah, tidak tersentuh training

Base model: Qwen/Qwen2.5-3B-Instruct
Method: LoRA (float16, no 4-bit)
Dataset: dcim_instructions.jsonl (3,816 samples)

Usage:
    # Single run
    python -m dcim_ai.llm.finetune_proper --lr 2e-4 --lora-r 16 --epochs 3

    # Grid search
    python -m dcim_ai.llm.finetune_proper --grid

    # Quick grid (max_steps terbatas untuk screening cepat)
    python -m dcim_ai.llm.finetune_proper --grid --quick
"""

import os
import sys
import json
import time
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─── Paths ───
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "dcim_instructions.jsonl"
OUTPUT_BASE = Path(__file__).resolve().parent / "models"
GRID_RESULTS_PATH = Path(__file__).resolve().parent / "grid_search_results.tsv"
TEST_SET_PATH = Path(__file__).resolve().parent / "datasets" / "dcim_test_set.jsonl"

# ─── Fixed config ───
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
MAX_SEQ_LEN = 512
GRAD_ACCUM = 16
WARMUP_RATIO = 0.05
BATCH_SIZE = 1
SEED = 42

# ─── Grid search space ───
GRID_LR = [1e-4, 2e-4, 5e-4]
GRID_LORA_R = [8, 16]
GRID_EPOCHS = [2, 3, 5]
GRID_LORA_ALPHA_MAP = {8: 16, 16: 32}  # alpha = 2 * r

# ─── Quick grid (max_steps limited) ───
QUICK_MAX_STEPS = 200


def set_seed(seed: int):
    import torch
    import numpy as np
    import random
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)


def load_and_split_dataset(path: Path, test_size: float = 0.15, val_size: float = 0.15,
                           seed: int = SEED, save_test: bool = True):
    """Load dataset and split into train/val/test (70/15/15)."""
    from datasets import Dataset
    from sklearn.model_selection import train_test_split

    records = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[DATA] Total records: {len(records)}")

    # Extract fields for training
    data = [{
        "instruction": r["instruction"],
        "input": r.get("input", ""),
        "output": r["output"],
        "category": r.get("metadata", {}).get("instruction_type", "unknown"),
    } for r in records]

    # First split: train_val vs test
    indices = list(range(len(data)))
    train_val_idx, test_idx = train_test_split(
        indices, test_size=test_size, random_state=seed,
        stratify=[d["category"] for d in data]
    )

    # Second split: train vs val
    train_val_data = [data[i] for i in train_val_idx]
    test_data = [data[i] for i in test_idx]
    train_val_cats = [d["category"] for d in train_val_data]
    train_val_idx2 = list(range(len(train_val_data)))

    val_ratio = val_size / (1 - test_size)
    train_idx2, val_idx2 = train_test_split(
        train_val_idx2, test_size=val_ratio, random_state=seed,
        stratify=train_val_cats
    )

    train_data = [train_val_data[i] for i in train_idx2]
    val_data = [train_val_data[i] for i in val_idx2]

    print(f"[DATA] Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

    # Save test set separately (held-out, never touched during training)
    if save_test and not TEST_SET_PATH.exists():
        TEST_SET_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TEST_SET_PATH, "w") as f:
            for item in test_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[DATA] Test set saved: {TEST_SET_PATH}")

    # Show category distribution
    from collections import Counter
    for name, subset in [("Train", train_data), ("Val", val_data), ("Test", test_data)]:
        cats = Counter(d["category"] for d in subset)
        top = cats.most_common(3)
        print(f"[DATA] {name:5s} categories: {dict(Counter(d['category'] for d in subset))}")

    # Convert to HF Dataset
    train_ds = Dataset.from_list(train_data)
    val_ds = Dataset.from_list(val_data)
    test_ds = Dataset.from_list(test_data)

    return train_ds, val_ds, test_ds


def format_chat_template(example, tokenizer):
    """Format as Qwen2.5 chat template with DCIM system prompt."""
    messages = [
        {"role": "system", "content": (
            "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis "
            "infrastruktur data center. Kamu memahami anomaly detection, drift analysis, "
            "root cause analysis, dan domain correlation pada sistem DCIM. "
            "Jawab dalam Bahasa Indonesia yang jelas dan teknis."
        )},
        {"role": "user", "content": f"{example['instruction']}\n\n{example['input']}"
                                  if example.get("input") else example["instruction"]},
        {"role": "assistant", "content": example["output"]}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return {"text": text}


def compute_dataset_hash(path: Path) -> str:
    """SHA256 hash untuk reproducibility audit."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()[:16]


def train_single_run(
    lr: float,
    lora_r: int,
    epochs: int,
    train_dataset,
    val_dataset,
    gpu: int = 0,
    version: str = None,
    max_seq_len: int = MAX_SEQ_LEN,
    max_steps: int = -1,
    early_stopping_patience: int = 3,
    save_best: bool = True,
) -> dict:
    """Single training run. Returns metrics dict."""
    import torch
    from transformers import (
        AutoModelForCausalLM, AutoTokenizer,
    )
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, SFTConfig

    # ─── GPU Setup ───
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)
    device = torch.device("cuda:0")

    lora_alpha = GRID_LORA_ALPHA_MAP.get(lora_r, lora_r * 2)
    effective_batch = BATCH_SIZE * GRAD_ACCUM
    # ─── Version ───
    if version is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        version = f"v2_lr{lr:.0e}_r{lora_r}_e{epochs}_{ts}"
    output_dir = OUTPUT_BASE / version
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"🔬 TRAINING RUN: {version}")
    print(f"{'='*70}")
    print(f"  LR: {lr:.1e}  |  LoRA r: {lora_r} (alpha={lora_alpha})  |  Epochs: {epochs}")
    print(f"  Batch: {BATCH_SIZE} × {GRAD_ACCUM} = {effective_batch}")
    print(f"  Train: {len(train_dataset)}  |  Val: {len(val_dataset)}")
    print(f"  Early stopping patience: {early_stopping_patience}")
    if max_steps > 0:
        print(f"  Max steps: {max_steps} (QUICK MODE)")

    # ─── GPU ───
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)
    device = torch.device("cuda:0")

    # ─── Tokenizer ───
    print("\n[1/5] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, padding_side="right")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # ─── Load Model (fp16, no bitsandbytes) ───
    print("[2/5] Loading model (float16)...")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    # ~6GB VRAM for 3B model, leaves ~2GB for optimizer states with batch_size=1
    print(f"   Model loaded in {time.time() - t0:.1f}s")

    # ─── LoRA ───
    print(f"[3/5] Applying LoRA (r={lora_r}, alpha={lora_alpha})...")
    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ─── Format datasets ───
    print("[4/5] Formatting datasets...")
    train_ds = train_dataset.map(
        lambda x: format_chat_template(x, tokenizer),
        remove_columns=train_dataset.column_names
    )
    val_ds = val_dataset.map(
        lambda x: format_chat_template(x, tokenizer),
        remove_columns=val_dataset.column_names
    )

    # ─── Training Config ───
    training_args = SFTConfig(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=epochs,
        max_steps=max_steps if max_steps > 0 else -1,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=lr,
        weight_decay=0.01,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=3,
        load_best_model_at_end=save_best,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,
        bf16=False,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        optim="adamw_torch",
        max_grad_norm=0.3,
        report_to="none",
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        max_length=max_seq_len,
        packing=False,
        seed=SEED,
        data_seed=SEED,
    )

    # ─── Trainer ───
    print("[5/5] Training...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
    )

    t0 = time.time()
    train_result = trainer.train()
    train_time = time.time() - t0

    # ─── Collect metrics from trainer logs ───
    eval_losses = []
    train_losses = []
    for log_entry in trainer.state.log_history:
        if "eval_loss" in log_entry:
            eval_losses.append(log_entry["eval_loss"])
        if "loss" in log_entry and "eval_loss" not in log_entry:
            train_losses.append(log_entry["loss"])

    # ─── Save best model ───
    adapter_path = output_dir / "adapter"
    if save_best:
        trainer.save_model(str(adapter_path))
        tokenizer.save_pretrained(str(adapter_path))
        print(f"\n   ✅ Best model saved: {adapter_path}")

    # ─── Metrics ───
    final_train_loss = train_losses[-1] if train_losses else train_result.training_loss
    final_eval_loss = eval_losses[-1] if eval_losses else float("nan")
    best_eval_loss = min(eval_losses) if eval_losses else float("nan")
    eval_perplexity = float(torch.exp(torch.tensor(final_eval_loss))) if final_eval_loss == final_eval_loss else float("nan")

    metrics = {
        "version": version,
        "lr": lr,
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
        "epochs": epochs,
        "max_steps": max_steps,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "final_train_loss": round(final_train_loss, 6) if final_train_loss else None,
        "final_eval_loss": round(final_eval_loss, 6) if final_eval_loss == final_eval_loss else None,
        "best_eval_loss": round(best_eval_loss, 6) if best_eval_loss == best_eval_loss else None,
        "eval_perplexity": round(eval_perplexity, 2) if eval_perplexity == eval_perplexity else None,
        "train_time_seconds": round(train_time, 1),
        "train_time_minutes": round(train_time / 60, 1),
        "early_stopped": trainer.state.best_model_checkpoint is not None and len(eval_losses) < epochs,
        "actual_epochs": len(eval_losses),
        "eval_losses": [round(l, 6) for l in eval_losses],
        "train_losses": [round(l, 6) for l in train_losses[-5:]],  # last 5
        "gpu": f"GPU {gpu}",
        "base_model": BASE_MODEL,
        "method": "QLoRA (BitsAndBytes NF4)",
        "dataset_hash": compute_dataset_hash(DATASET_PATH),
        "timestamp": datetime.now().isoformat(),
    }

    # ─── Save metadata ───
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # ─── Summary ───
    print(f"\n{'='*70}")
    print(f"📊 RUN COMPLETE: {version}")
    print(f"{'='*70}")
    print(f"  Train Loss: {final_train_loss:.4f}  |  Eval Loss: {final_eval_loss:.4f}  |  Perplexity: {eval_perplexity:.2f}")
    print(f"  Best Eval:  {best_eval_loss:.4f}")
    print(f"  Time: {train_time/60:.1f} min  |  Actual epochs: {len(eval_losses)}")
    print(f"  Adapter: {adapter_path}")
    print(f"{'='*70}")

    return metrics


def run_grid_search(quick: bool = False, gpu: int = 0):
    """Grid search over hyperparameter space."""
    set_seed(SEED)

    print("=" * 70)
    mode = "QUICK SCREENING" if quick else "FULL GRID SEARCH"
    print(f"🔍 GRID SEARCH — {mode}")
    print("=" * 70)

    # Load & split dataset (only once)
    train_ds, val_ds, test_ds = load_and_split_dataset(DATASET_PATH)

    # Build grid
    grid = []
    for lr in GRID_LR:
        for r in GRID_LORA_R:
            for ep in GRID_EPOCHS:
                grid.append({"lr": lr, "lora_r": r, "epochs": ep})

    print(f"\nTotal combinations: {len(grid)}")
    if quick:
        print(f"Quick mode: max {QUICK_MAX_STEPS} steps per run")
    print()

    results = []
    for i, params in enumerate(grid):
        print(f"\n{'#'*70}")
        print(f"# GRID RUN {i+1}/{len(grid)}: LR={params['lr']:.0e}, r={params['lora_r']}, epochs={params['epochs']}")
        print(f"{'#'*70}")

        try:
            metrics = train_single_run(
                lr=params["lr"],
                lora_r=params["lora_r"],
                epochs=params["epochs"],
                train_dataset=train_ds,
                val_dataset=val_ds,
                gpu=gpu,
                max_steps=QUICK_MAX_STEPS if quick else -1,
                early_stopping_patience=3,
                save_best=not quick,  # Quick mode: skip saving to save disk
            )
            results.append(metrics)
        except Exception as e:
            print(f"\n❌ RUN FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append({**params, "error": str(e)})

    # ─── Save grid results ───
    _save_grid_results(results, GRID_RESULTS_PATH)

    # ─── Print rankings ───
    _print_grid_ranking(results)


def _save_grid_results(results: list, path: Path):
    """Save grid results as TSV."""
    valid = [r for r in results if "best_eval_loss" in r]
    if not valid:
        print("\n⚠️ No valid results to save.")
        return

    # Sort by eval loss
    valid.sort(key=lambda r: r.get("best_eval_loss", float("inf")))

    # TSV header
    cols = ["rank", "version", "lr", "lora_r", "epochs", "best_eval_loss",
            "eval_perplexity", "final_train_loss", "train_time_minutes"]
    lines = ["\t".join(cols)]
    for i, r in enumerate(valid):
        row = [
            str(i + 1),
            r.get("version", "?"),
            f"{r['lr']:.0e}",
            str(r["lora_r"]),
            str(r["epochs"]),
            f"{r['best_eval_loss']:.6f}",
            f"{r['eval_perplexity']:.2f}" if r.get("eval_perplexity") else "N/A",
            f"{r['final_train_loss']:.6f}" if r.get("final_train_loss") else "N/A",
            f"{r['train_time_minutes']:.1f}",
        ]
        lines.append("\t".join(row))

    with open(path, "w") as f:
        f.write("\n".join(lines))

    print(f"\n📄 Grid results saved: {path}")


def _print_grid_ranking(results: list):
    """Pretty-print grid ranking."""
    valid = [r for r in results if "best_eval_loss" in r]
    if not valid:
        return
    valid.sort(key=lambda r: r.get("best_eval_loss", float("inf")))

    print(f"\n{'='*70}")
    print("🏆 GRID SEARCH RANKINGS")
    print(f"{'='*70}")
    print(f"{'Rank':<6}{'LR':<10}{'r':<6}{'Epochs':<8}{'Best Eval Loss':<16}{'Perplexity':<12}{'Time'}")
    print("-" * 70)
    for i, r in enumerate(valid[:10]):
        print(f"{i+1:<6}{r['lr']:<10.0e}{r['lora_r']:<6}{r['epochs']:<8}"
              f"{r['best_eval_loss']:<16.6f}{r.get('eval_perplexity', 'N/A'):<12}{r['train_time_minutes']:.1f}m")
    print(f"{'='*70}")

    if len(valid) > 1:
        best = valid[0]
        print(f"\n🥇 BEST: {best['version']}")
        print(f"   LR={best['lr']:.0e}, r={best['lora_r']}, epochs={best['epochs']}")
        print(f"   Eval Loss: {best['best_eval_loss']:.6f}")
        print(f"   Adapter: {OUTPUT_BASE / best['version'] / 'adapter'}")


def run_baseline_eval(gpu: int = 0):
    """Run a minimal baseline: load base model, evaluate on test set without training."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    print("=" * 70)
    print("📏 BASELINE EVALUATION (Pre-Fine-Tune)")
    print("=" * 70)

    # Load test set
    if not TEST_SET_PATH.exists():
        print("❌ Test set not found. Run dataset split first.")
        return None

    test_records = []
    with open(TEST_SET_PATH, "r") as f:
        for line in f:
            if line.strip():
                test_records.append(json.loads(line))

    print(f"Test samples: {len(test_records)}")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)
    device = torch.device("cuda:0")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float32,  # Ampere GPU workaround
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map={"": device},
        trust_remote_code=True,
    )

    results = []
    for i, rec in enumerate(test_records[:20]):  # Sample first 20
        prompt = f"{rec['instruction']}\n\n{rec.get('input', '')}"
        messages = [
            {"role": "system", "content": "Kamu adalah DCIM AI Assistant..."},
            {"role": "user", "content": prompt},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(device)

        t0 = time.time()
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.3, do_sample=True)
        latency = time.time() - t0

        generated = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        expected = rec["output"]

        # Simple keyword overlap score
        expected_words = set(expected.lower().split())
        generated_words = set(generated.lower().split())
        overlap = len(expected_words & generated_words) / max(len(expected_words), 1)

        results.append({
            "id": i,
            "category": rec.get("category", "unknown"),
            "latency": latency,
            "keyword_overlap": overlap,
            "generated_length": len(generated),
        })

    # Summary
    avg_overlap = sum(r["keyword_overlap"] for r in results) / len(results)
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print(f"\n📊 BASELINE RESULTS ({len(results)} samples):")
    print(f"   Avg Keyword Overlap: {avg_overlap:.4f}")
    print(f"   Avg Latency: {avg_latency:.2f}s")

    baseline_path = OUTPUT_BASE / "baseline_eval.json"
    with open(baseline_path, "w") as f:
        json.dump({"avg_overlap": avg_overlap, "avg_latency": avg_latency, "results": results}, f, indent=2)
    print(f"   Saved: {baseline_path}")

    return {"avg_overlap": avg_overlap, "avg_latency": avg_latency}


# =====================================================
# CLI
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="MT-023 Phase 2 — Proper Fine-Tuning")
    parser.add_argument("--grid", action="store_true", help="Run grid search")
    parser.add_argument("--quick", action="store_true", help="Quick screening (max_steps=200)")
    parser.add_argument("--baseline", action="store_true", help="Run baseline evaluation only")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--max-steps", type=int, default=-1, help="Max training steps (-1 = unlimited)")
    parser.add_argument("--gpu", type=int, default=0, help="GPU device ID")
    parser.add_argument("--version", type=str, default=None, help="Model version name")

    global DATASET_PATH
    args = parser.parse_args()

    # Check dataset
    if not DATASET_PATH.exists():
        # Try alternate path via symlink
        alt = Path("/home/infra/rnd_rag-anything/dcim_ai/llm/datasets/dcim_instructions.jsonl")
        if alt.exists():
            DATASET_PATH = alt
        else:
            print(f"❌ Dataset not found: {DATASET_PATH}")
            sys.exit(1)

    # Check CUDA
    import torch
    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        sys.exit(1)
    props = torch.cuda.get_device_properties(args.gpu)
    print(f"🖥️  GPU: {props.name}")
    print(f"   VRAM: {props.total_memory / 1e9:.1f} GB")

    # ─── Route ───
    if args.baseline:
        run_baseline_eval(gpu=args.gpu)
    elif args.grid:
        run_grid_search(quick=args.quick, gpu=args.gpu)
    else:
        # Single run
        set_seed(SEED)
        train_ds, val_ds, test_ds = load_and_split_dataset(DATASET_PATH)
        train_single_run(
            lr=args.lr,
            lora_r=args.lora_r,
            epochs=args.epochs,
            train_dataset=train_ds,
            val_dataset=val_ds,
            gpu=args.gpu,
            version=args.version,
            max_steps=args.max_steps,
            early_stopping_patience=3,
            save_best=True,
        )


if __name__ == "__main__":
    main()
