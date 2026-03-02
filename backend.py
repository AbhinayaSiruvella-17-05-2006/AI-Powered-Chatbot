import requests
import json
from PIL import Image
import base64
import io
import os

# 🔐 Get API key from environment (Render)
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment variables.")

MODEL_NAME = "models/gemini-2.5-flash"

URL = f"https://generativelanguage.googleapis.com/v1/{MODEL_NAME}:generateContent?key={API_KEY}"


def GenerateResponse(input_text=None, image=None):
    try:
        parts = []

        if input_text:
            parts.append({"text": input_text})

        if image and isinstance(image, Image.Image):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": img_base64
                }
            })

        if not parts:
            return "Please provide text or image input."

        payload = {
            "contents": [{"parts": parts}]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        result = response.json()

        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"