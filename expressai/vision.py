# expressai/vision.py
import base64
import openai

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_image(image_path: str, prompt: str = "What’s in this image?", model: str = "gpt-4o") -> str:
    if not openai.api_key:
        raise ValueError("Please set openai.api_key = 'your-api-key' before calling analyze_image.")

    try:
        base64_image = encode_image(image_path)
        client = openai.OpenAI(api_key=openai.api_key)  # ✅ Pass key explicitly here
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": prompt },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
        )
        return response.output_text.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"
