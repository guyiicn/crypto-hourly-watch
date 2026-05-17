import requests

from . import config

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def interpret(prompt: str) -> str:
    if not config.GEMINI_API_KEY:
        return ""
    url = GEMINI_URL.format(model=config.GEMINI_MODEL) + f"?key={config.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 400},
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"(LLM 调用失败: {e})"
