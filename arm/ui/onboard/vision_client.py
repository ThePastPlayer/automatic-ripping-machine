import base64
import json
import mimetypes

import requests


def _encode_image_as_data_url(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = 'image/jpeg'
    with open(path, 'rb') as f:
        b = f.read()
    return f"data:{mime};base64,{base64.b64encode(b).decode('utf-8')}"


def identify_from_images(api_key: str, user_text: str, image_paths: list[str]) -> str:
    # Compose messages per OpenAI Vision (gpt-4o-mini)
    content = [
        {"type": "text", "text": user_text}
    ]
    for p in image_paths:
        content.append({"type": "image_url", "image_url": {"url": _encode_image_as_data_url(p)}})

    payload = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": "You are an expert that extracts canonical metadata from disc cover images and notes. Return only JSON."},
            {"role": "user", "content": content}
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Use the standardized OpenAI responses endpoint if available
    url = "https://api.openai.com/v1/chat/completions"
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    text = data['choices'][0]['message']['content']
    return text


