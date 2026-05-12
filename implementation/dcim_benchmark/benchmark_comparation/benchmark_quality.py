import requests

tests = [
    ("What is CPU spike?", "cpu"),
    ("What is anomaly detection?", "anomaly"),
]

models = ["qwen3.5:4b", "gemma4:latest"]

URL = "http://localhost:11434/api/generate"

for model in models:
    score = 0

    for prompt, keyword in tests:
        res = requests.post(URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 100}
        }).json()["response"]

        if keyword in res.lower():
            score += 1

    print(model, "Quality Score:", score / len(tests))