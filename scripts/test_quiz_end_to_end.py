import os
import json
import time
import requests


BASE = os.getenv("AGENTS_API_BASE", "http://localhost:8088/api/v1")


def main():
    # 1) Generate a small quiz for React
    gen_payload = {
        "topic": "React",
        "question_count": 2,
        "target_audience": "developers",
        "save": True,
    }
    print("[1/3] Generating quiz...", gen_payload)
    r = requests.post(f"{BASE}/quiz/generate", json=gen_payload, timeout=300)
    r.raise_for_status()
    gen = r.json()
    print("Generated: session_id=", gen.get("session_id"), "output_file=", gen.get("output_file"))

    # 2) Validate quiz
    quiz = gen.get("quiz")
    print("[2/3] Validating quiz (keys):", list(quiz.keys()) if isinstance(quiz, dict) else type(quiz))
    r = requests.post(f"{BASE}/quiz/validate", json={"quiz": quiz}, timeout=120)
    r.raise_for_status()
    val = r.json()
    print("Validation:", val)
    if not val.get("ok"):
        raise SystemExit("Validation failed: " + val.get("message", ""))

    # 3) Upload quiz (requires platform API running if you want a real upload)
    # Here we only call the endpoint with a dummy api_url to test code path
    api_url = os.getenv("PLATFORM_API_URL", "http://localhost:3000")
    print("[3/3] Uploading quiz (api_url=", api_url, ") ...")
    r = requests.post(
        f"{BASE}/quiz/upload",
        json={
            "quiz": quiz,
            "api_url": api_url,
            "admin_secret": os.getenv("ADMIN_SECRET", "TBEAdmin"),
        },
        timeout=120,
    )
    if r.status_code >= 400:
        print("Upload failed with", r.status_code, r.text)
    else:
        print("Upload result:", r.json())


if __name__ == "__main__":
    main()

