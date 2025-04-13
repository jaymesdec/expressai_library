# expressai/chatbot.py
import openai
import base64
from PIL import Image
import os

class Chatbot:
    def __init__(self, system_prompt: str, model: str = "gpt-4o", max_tokens: int = 100):
        self.system_prompt = system_prompt
        self.model = model
        self.history = []
        self.default_max_tokens = max_tokens

    def __call__(self, prompt: str = None, image: str = None, verbose: bool = False, max_tokens: int = None) -> str:
        try:
            client = openai.OpenAI(api_key=openai.api_key)
        except Exception as e:
            return f"[OpenAI client error: {e}]"

        if image:
            if not prompt:
                prompt = "What do you see in this image?"

            try:
                image = self._resize_image_if_needed(image)
                with open(image, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            except Exception as e:
                return f"[Image load error: {e}]"

            input_payload = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]

            try:
                response = client.responses.create(
                    model=self.model,
                    input=input_payload
                )
                return response.output_text.strip()
            except Exception as e:
                return f"[Image analysis error: {e}]"

        else:
            if not prompt:
                return "[Error: You must provide a prompt when no image is given.]"

            self.history.append({"role": "user", "content": prompt})
            messages = [{"role": "system", "content": self.system_prompt}] + self.history

            if verbose:
                for msg in messages:
                    print(f"{msg['role'].capitalize()}: {msg['content']}")

            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens if max_tokens is not None else self.default_max_tokens
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                reply = f"[Chat error: {e}]"

            self.history.append({"role": "assistant", "content": reply})
            return reply

    def _resize_image_if_needed(self, image_path: str, max_short_side: int = 768) -> str:
        """
        Resize image if the short side is greater than max_short_side.
        Returns the path to the resized image (or original if no change).
        """
        with Image.open(image_path) as img:
            width, height = img.size
            short_side = min(width, height)

            if short_side <= max_short_side:
                return image_path  # No resize needed

            # Maintain aspect ratio
            if width < height:
                new_width = max_short_side
                new_height = int((max_short_side / width) * height)
            else:
                new_height = max_short_side
                new_width = int((max_short_side / height) * width)

            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save resized image with suffix
            base, ext = os.path.splitext(image_path)
            resized_path = f"{base}_resized{ext}"
            resized_img.save(resized_path)
            return resized_path

    def reset(self):
        self.history = []

    def __str__(self):
        return (
            f"<Chatbot model={self.model} "
            f"prompt={self.system_prompt[:30]}... "
            f"turns={len(self.history) // 2} "
            f"default_max_tokens={self.default_max_tokens}>"
        )
