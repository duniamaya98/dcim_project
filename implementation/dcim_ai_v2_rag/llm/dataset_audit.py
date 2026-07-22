import json
import random
import os
from collections import Counter

def audit_dataset(file_path):
    print(f"\n--- Auditing {os.path.basename(file_path)} ---")
    if not os.path.exists(file_path):
        print("File not found!")
        return None
        
    categories = Counter()
    lengths = []
    unique_prompts = set()
    duplicates = 0
    total = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            try:
                data = json.loads(line)
                
                # Format 1: HuggingFace generic text/instruction format
                prompt = ""
                if "instruction" in data:
                    prompt = data["instruction"]
                # Format 2: OpenAI messages format
                elif "messages" in data and len(data["messages"]) > 0:
                    for m in data["messages"]:
                        if m.get("role") == "user":
                            prompt = m.get("content", "")
                            break
                            
                # Check duplicates
                if prompt in unique_prompts:
                    duplicates += 1
                else:
                    unique_prompts.add(prompt)
                    
                # Track lengths
                response_len = len(data.get("output", "")) if "output" in data else len(str(data))
                lengths.append(response_len)
                
                # Try to guess category based on keywords
                prompt_lower = prompt.lower()
                cat = "General"
                if "cpu" in prompt_lower or "memory" in prompt_lower: cat = "Server Health"
                elif "pue" in prompt_lower or "power" in prompt_lower: cat = "Energy/Power"
                elif "network" in prompt_lower or "interface" in prompt_lower: cat = "Network"
                elif "disk" in prompt_lower or "nas" in prompt_lower: cat = "Storage"
                elif "anomaly" in prompt_lower: cat = "Anomaly"
                
                categories[cat] += 1
                
            except Exception as e:
                print(f"Error parsing line {total}: {e}")
                
    print(f"Total entries: {total}")
    print(f"Exact duplicates found: {duplicates} ({duplicates/total*100:.1f}% if >0 else 0%)")
    print("\nCategory Distribution:")
    for cat, count in categories.most_common():
        print(f"  - {cat}: {count} ({count/total*100:.1f}%)")
        
    if lengths:
        avg_len = sum(lengths)/len(lengths)
        print(f"\nAvg response length: {avg_len:.0f} chars")
        
    return {"total": total, "duplicates": duplicates, "categories": dict(categories)}

if __name__ == "__main__":
    base_dir = "/home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/datasets"
    audit_dataset(f"{base_dir}/dcim_instructions.jsonl")
    audit_dataset(f"{base_dir}/dcim_instructions_enhanced.jsonl")
