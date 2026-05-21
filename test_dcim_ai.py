#!/usr/bin/env python3
"""
Quick Test Script untuk DCIM AI Model
Menguji berbagai jenis instruction dengan model yang sudah di-deploy
"""

import requests
import json
import sys

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
LLAMA_SERVER_URL = "http://localhost:8080/v1/chat/completions"

# Test cases dengan berbagai kategori
TEST_CASES = [
    {
        "category": "Anomaly Detection",
        "prompt": "Apakah ada anomali yang terdeteksi? CPU: 8%, Memory: 23%, Disk I/O: 623766, Network RX: 245831, TX: 6487"
    },
    {
        "category": "Drift Analysis",
        "prompt": "Bagaimana kondisi drift pada metrik ini? CPU: 2%, Memory: 23%, Disk I/O: 623756"
    },
    {
        "category": "Root Cause",
        "prompt": "Apa yang menyebabkan masalah pada infrastruktur ini? CPU: 15%, Memory: 80%, Disk I/O tinggi"
    },
    {
        "category": "Recommendation",
        "prompt": "Rekomendasikan tindakan mitigasi untuk memory usage tinggi (85%)"
    },
    {
        "category": "Summary",
        "prompt": "Ringkas kondisi sistem saat ini: CPU normal, Memory tinggi, Disk I/O stabil"
    }
]

def test_ollama(model_name="dcim-ai"):
    """Test dengan Ollama API"""
    print("=" * 70)
    print("Testing with Ollama API")
    print("=" * 70)

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['category']}")
        print(f"Prompt: {test['prompt'][:80]}...")

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model_name,
                    "prompt": test['prompt'],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                output = result.get("response", "")
                print(f"Response: {output[:200]}...")
                print(f"✅ Success")
            else:
                print(f"❌ Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed. Is Ollama running?")
            print(f"   Start with: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")

    return True

def test_llama_server():
    """Test dengan llama-server API (OpenAI compatible)"""
    print("\n" + "=" * 70)
    print("Testing with llama-server API")
    print("=" * 70)

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['category']}")
        print(f"Prompt: {test['prompt'][:80]}...")

        try:
            response = requests.post(
                LLAMA_SERVER_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis infrastruktur data center."
                        },
                        {
                            "role": "user",
                            "content": test['prompt']
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 512
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                output = result["choices"][0]["message"]["content"]
                print(f"Response: {output[:200]}...")
                print(f"✅ Success")
            else:
                print(f"❌ Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed. Is llama-server running?")
            print(f"   Start with: llama-server -m dcim-ai-Q4_K_M.gguf -ngl 99 --port 8080")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")

    return True

def interactive_mode(use_ollama=True):
    """Interactive chat mode"""
    print("\n" + "=" * 70)
    print("Interactive Chat Mode")
    print("=" * 70)
    print("Type 'exit' or 'quit' to stop")
    print("Type 'help' for example prompts")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if user_input.lower() == 'help':
                print("\nContoh pertanyaan:")
                for test in TEST_CASES:
                    print(f"  - {test['prompt'][:70]}...")
                print()
                continue

            if not user_input:
                continue

            if use_ollama:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": "dcim-ai",
                        "prompt": user_input,
                        "stream": False,
                        "options": {"temperature": 0.3}
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    output = response.json().get("response", "")
                    print(f"\nAI: {output}\n")
                else:
                    print(f"Error: {response.status_code}\n")
            else:
                response = requests.post(
                    LLAMA_SERVER_URL,
                    json={
                        "messages": [
                            {"role": "system", "content": "Kamu adalah DCIM AI Assistant."},
                            {"role": "user", "content": user_input}
                        ],
                        "temperature": 0.3
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    output = response.json()["choices"][0]["message"]["content"]
                    print(f"\nAI: {output}\n")
                else:
                    print(f"Error: {response.status_code}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

def main():
    """Main function"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              DCIM AI Model - Quick Test Script                   ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "ollama":
            test_ollama()
        elif mode == "llama":
            test_llama_server()
        elif mode == "interactive":
            use_ollama = input("Use Ollama (o) or llama-server (l)? [o/l]: ").lower() != 'l'
            interactive_mode(use_ollama)
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_dcim_ai.py [ollama|llama|interactive]")
    else:
        print("Select test mode:")
        print("  1. Test with Ollama")
        print("  2. Test with llama-server")
        print("  3. Interactive chat")
        print("  4. Run all tests")

        choice = input("\nChoice [1-4]: ").strip()

        if choice == "1":
            test_ollama()
        elif choice == "2":
            test_llama_server()
        elif choice == "3":
            use_ollama = input("Use Ollama (o) or llama-server (l)? [o/l]: ").lower() != 'l'
            interactive_mode(use_ollama)
        elif choice == "4":
            test_ollama()
            test_llama_server()
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
