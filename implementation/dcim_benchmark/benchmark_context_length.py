import requests

for size in [512, 1024, 2048, 4096, 8192]:
    prompt = "A" * size
    
    payload = {
        "model": "mistral:7b",
        "prompt": prompt,
        "stream": False
    }

    res = requests.post("http://localhost:11434/api/generate", json=payload)
    
    print(size, res.status_code)