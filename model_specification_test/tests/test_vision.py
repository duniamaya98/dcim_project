"""
Test: Vision / Image Analysis

Mengukur kemampuan model untuk:
1. Menganalisis gambar (screenshot, diagram, chart)
2. Extract informasi dari gambar
3. Memberikan insight berdasarkan visual data

Catatan: Test ini hanya untuk model multimodal (Qwen3-VL-4B-Instruct, Gemma-4-E4B)
"""

import base64
import os
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont


# Create test images
def create_test_images(output_dir: str):
    """Create test images for vision testing."""
    os.makedirs(output_dir, exist_ok=True)

    # Image 1: Simple dashboard mockup
    img1 = Image.new('RGB', (800, 600), color='white')
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([50, 50, 750, 150], fill='lightblue', outline='black')
    draw1.text((100, 80), "Server Dashboard - CPU: 85%, Memory: 72%", fill='black')
    draw1.rectangle([50, 200, 400, 400], fill='lightgreen', outline='black')
    draw1.text((100, 280), "srv-web-01: OK", fill='black')
    draw1.rectangle([450, 200, 750, 400], fill='lightcoral', outline='black')
    draw1.text((500, 280), "srv-db-01: WARNING", fill='black')
    img1.save(os.path.join(output_dir, "dashboard_mockup.png"))

    # Image 2: Alert notification
    img2 = Image.new('RGB', (600, 400), color='white')
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([50, 50, 550, 350], fill='lightyellow', outline='red', width=3)
    draw2.text((100, 100), "CRITICAL ALERT", fill='red')
    draw2.text((100, 150), "Server: srv-app-05", fill='black')
    draw2.text((100, 200), "CPU: 95%", fill='black')
    draw2.text((100, 250), "Memory: 88%", fill='black')
    draw2.text((100, 300), "Action Required", fill='red')
    img2.save(os.path.join(output_dir, "alert_notification.png"))

    return {
        "dashboard": os.path.join(output_dir, "dashboard_mockup.png"),
        "alert": os.path.join(output_dir, "alert_notification.png"),
    }


TEST_CASES = [
    {
        "name": "dashboard_analysis",
        "image": "dashboard_mockup.png",
        "question": "Analisis dashboard ini. Server mana yang bermasalah? Apa metrik yang ditampilkan?",
        "expected_keywords": ["server", "cpu", "memory", "warning", "srv-db-01", "dashboard"],
    },
    {
        "name": "alert_interpretation",
        "image": "alert_notification.png",
        "question": "Apa yang ditampilkan di gambar ini? Apa severity alert-nya? Server mana yang terpengaruh?",
        "expected_keywords": ["alert", "critical", "server", "cpu", "memory", "srv-app-05"],
    },
    {
        "name": "visual_data_extraction",
        "image": "dashboard_mockup.png",
        "question": "Extract semua informasi yang terlihat di gambar ini dalam format terstruktur.",
        "expected_keywords": ["server", "cpu", "memory", "srv-web-01", "srv-db-01", "ok", "warning"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all vision tests and return results."""
    # Create test images
    image_dir = os.path.join(os.path.dirname(__file__), "..", "test_images")
    images = create_test_images(image_dir)

    results = []
    total_score = 0
    max_score = len(TEST_CASES)

    for tc in TEST_CASES:
        try:
            image_path = images.get(tc["image"])
            if not image_path or not os.path.exists(image_path):
                results.append({
                    "test": tc["name"],
                    "score": 0.0,
                    "error": f"Image not found: {tc['image']}",
                })
                continue

            # Encode image
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()

            # Send to multimodal model
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": tc["question"]
                            }
                        ]
                    }
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_vision(tc, content)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "response_preview": content[:200] if content else "",
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "vision",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_vision(test_case: dict, content: str) -> float:
    """Evaluate vision analysis quality."""
    score = 0.0
    content_lower = content.lower()

    # Check if answer contains expected keywords
    expected_keywords = test_case.get("expected_keywords", [])
    if expected_keywords:
        matched = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
        keyword_score = matched / len(expected_keywords)
        score += keyword_score * 0.7  # 70% weight for keyword coverage

    # Check if response is substantial
    if len(content) > 50:
        score += 0.3  # 30% weight for response substance

    return min(score, 1.0)
