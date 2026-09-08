# expressai/vision.py
import base64
import os
import openai


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image(
    image_path: str,
    prompt: str = "What's in this image?",
    model: str = "gpt-4o-mini",
    api_key: str = None,
    base_url: str = None,
    classroom_token: str = None,
) -> str:
    """
    Describe or analyze an image with a vision-capable model.

    Works directly against OpenAI (set ``openai.api_key`` / ``OPENAI_API_KEY`` /
    pass ``api_key``) or through a classroom proxy (pass ``base_url`` and
    ``classroom_token``).
    """
    if base_url:
        key = api_key or classroom_token or "classroom-student-auth"
        client = openai.OpenAI(api_key=key, base_url=base_url)
    else:
        key = api_key or os.getenv("OPENAI_API_KEY") or getattr(openai, "api_key", None)
        if not key:
            raise ValueError(
                "No API key found. Set openai.api_key = 'your-api-key', or pass "
                "base_url= and classroom_token= to use a classroom proxy."
            )
        client = openai.OpenAI(api_key=key)

    try:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"
