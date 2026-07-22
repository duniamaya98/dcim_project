import json
import random
import os
from collections import defaultdict

def process_dataset(input_file, out_dir):
    print(f"Processing {input_file}...")
    
    # Group by instruction to handle duplicates
    grouped_data = defaultdict(list)
    
    with open(input_file, 'r') as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                instruction = data.get("instruction", "")
                grouped_data[instruction].append(data)
            except Exception as e:
                pass
                
    # Balance: limit to max 20 samples per unique instruction to prevent overfitting
    balanced_data = []
    for inst, items in grouped_data.items():
        if len(items) > 20:
            balanced_data.extend(random.sample(items, 20))
        else:
            balanced_data.extend(items)
            
    print(f"Reduced from {sum(len(v) for v in grouped_data.values())} to {len(balanced_data)} balanced samples.")
    
    # Shuffle
    random.seed(42)
    random.shuffle(balanced_data)
    
    # Split 70 / 15 / 15
    n = len(balanced_data)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    train_set = balanced_data[:train_end]
    val_set = balanced_data[train_end:val_end]
    test_set = balanced_data[val_end:]
    
    # Write files
    os.makedirs(out_dir, exist_ok=True)
    
    def write_jsonl(data_list, filename):
        path = os.path.join(out_dir, filename)
        with open(path, 'w') as f:
            for item in data_list:
                f.write(json.dumps(item) + '\n')
        print(f"Wrote {len(data_list)} items to {filename}")
        
    write_jsonl(train_set, "train.jsonl")
    write_jsonl(val_set, "val.jsonl")
    write_jsonl(test_set, "test.jsonl")
    
    return len(train_set), len(val_set), len(test_set)

if __name__ == "__main__":
    base_dir = "/home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/datasets"
    input_file = os.path.join(base_dir, "dcim_instructions_enhanced.jsonl")
    out_dir = os.path.join(base_dir, "processed")
    process_dataset(input_file, out_dir)
