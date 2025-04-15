# expressai/chatbot.py

import openai
import base64
import os
from PIL import Image
from io import BytesIO

# ✅ Detect Colab for inline image/audio support
try:
    import google.colab
    from IPython.display import display, HTML, Image as ColabImage
    from IPython import get_ipython
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# ✅ Inject custom CSS to wrap outputs in Colab
if IN_COLAB:
    def _set_output_wrapping():
        display(HTML("""
        <style>
            pre {
                white-space: pre-wrap;
                word-break: break-word;
            }
        </style>
        """))
    get_ipython().events.register("pre_run_cell", _set_output_wrapping)

# ✅ Import TTS
from .tts import speak_text

class Chatbot:
    def __init__(self, system_prompt: str, model: str = "gpt-4o", max_tokens: int = 100, voice_id: str = None):
        self.system_prompt = system_prompt
        self.model = model
        self.history = []
        self.default_max_tokens = max_tokens
        self.voice_id = voice_id

    def __call__(
        self,
        prompt: str = None,
        image: str = None,
        generate_image: bool = False,
        language: str = None,
        speak: bool = False,
        verbose: bool = False,
        max_tokens: int = None
    ) -> str:
        client = openai.OpenAI(api_key=openai.api_key)

        if language:
            prompt = f"Please respond in {language}.\n{prompt}"

        if generate_image:
            result = self._generate_image(prompt)
        elif image:
            result = self._analyze_image(client, prompt, image)
        else:
            result = self._chat(client, prompt, verbose, max_tokens)

        if speak and isinstance(result, str) and self.voice_id:
            speak_text(result, voice_id=self.voice_id)

        return result

    def _chat(self, client, prompt, verbose, max_tokens):
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

    def _analyze_image(self, client, prompt, image_path):
        if not prompt:
            prompt = "What do you see in this image?"

        try:
            with open(image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        except Exception as e:
            return f"[Image load error: {e}]"

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ]
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Image analysis error: {e}]"

    def _generate_image(self, prompt):
        try:
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
        except Exception as e:
            return f"[Image generation error: {e}]"

        # Save image locally and display in Colab
        try:
            import requests
            os.makedirs("output_images", exist_ok=True)
            filename = f"output_images/{prompt[:40].replace(' ', '_').replace('.', '')}.png"
            img_data = requests.get(image_url).content
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            if IN_COLAB:
                display(ColabImage(filename))
            return filename
        except Exception as e:
            return f"[Error saving or displaying image: {e}]"

    def reset(self):
        self.history = []

    def __str__(self):
        return (
            f"<Chatbot model={self.model} "
            f"prompt={self.system_prompt[:30]}... "
            f"turns={len(self.history) // 2} "
            f"default_max_tokens={self.default_max_tokens} "
            f"voice_id={self.voice_id}>"
        )
