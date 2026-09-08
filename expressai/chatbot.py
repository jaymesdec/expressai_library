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

# A harmless placeholder used as the api_key when a student routes through the
# classroom proxy without their own key. The OpenAI client refuses to initialize
# with an empty key, and the proxy ignores/validates it separately.
DUMMY_CLASSROOM_KEY = "classroom-student-auth"


class Chatbot:
    def __init__(
        self,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 100,
        voice_id: str = None,
        api_key: str = None,
        base_url: str = None,
        classroom_token: str = None,
        student_id: str = None,
    ):
        """
        A chatbot with a personality that can chat, see images, generate images,
        and speak.

        Adults can pass an OpenAI ``api_key`` (or set ``openai.api_key`` /
        ``OPENAI_API_KEY``) for direct OpenAI access. Students can instead point
        ``base_url`` at a classroom proxy and authenticate with a
        ``classroom_token`` — no personal API key required.

        Args:
            system_prompt (str): Personality or behavior description for the bot.
            model (str): Model name (default: gpt-4o-mini). When routing through a
                classroom proxy, the proxy may override this with a cheaper model.
            max_tokens (int): Default max response length (default: 100).
            voice_id (str): Optional ElevenLabs voice ID for speaking responses.
            api_key (str): Optional OpenAI API key. Falls back to OPENAI_API_KEY
                and then openai.api_key when no base_url is set.
            base_url (str): Optional proxy endpoint (e.g. "https://my-proxy.com/v1").
            classroom_token (str): Optional shared classroom password/token, sent to
                the proxy for authentication.
            student_id (str): Optional student identifier, forwarded to the proxy for
                per-student rate limiting.
        """
        self.system_prompt = system_prompt
        self.model = model
        self.history = []
        self.default_max_tokens = max_tokens
        self.voice_id = voice_id

        # Routing / auth configuration
        self.api_key = api_key
        self.base_url = base_url
        self.classroom_token = classroom_token
        self.student_id = student_id

        # The OpenAI client is built lazily on first use so that a key set *after*
        # construction (e.g. openai.api_key = "...") is still picked up.
        self._client = None

    # ------------------------------------------------------------------ #
    # Client resolution
    # ------------------------------------------------------------------ #
    def _ensure_client(self):
        """Build (once) and return the configured OpenAI client, or None if no
        credentials are available for direct OpenAI access."""
        if self._client is not None:
            return self._client

        if self.base_url:
            # Proxy mode: students never need a real OpenAI key.
            key = self.api_key or self.classroom_token or DUMMY_CLASSROOM_KEY
            headers = {}
            if self.classroom_token:
                headers["X-Classroom-Token"] = self.classroom_token
            if self.student_id:
                headers["X-Student-ID"] = self.student_id
            self._client = openai.OpenAI(
                api_key=key,
                base_url=self.base_url,
                default_headers=headers or None,
            )
        else:
            # Direct OpenAI mode: resolve a real key.
            key = (
                self.api_key
                or os.getenv("OPENAI_API_KEY")
                or getattr(openai, "api_key", None)
            )
            if not key:
                return None  # Handled with a friendly message at call time.
            self._client = openai.OpenAI(api_key=key)

        return self._client

    def _missing_key_message(self):
        return (
            "[Setup error: No API key found. Adults: set your key with "
            "openai.api_key = 'sk-...' or pass api_key=... . Students: pass "
            "base_url=... and classroom_token=... to route through your class proxy.]"
        )

    def _friendly_error(self, context, exc):
        """Turn an OpenAI/network exception into a beginner-friendly message."""
        if isinstance(exc, openai.APIConnectionError):
            return (
                "[Connection error: Could not reach the AI server. Check your "
                "internet connection or verify your proxy URL (base_url).]"
            )
        if isinstance(exc, openai.AuthenticationError):
            return (
                "[Login error: Your API key or classroom token was rejected. "
                "Double-check it with your teacher.]"
            )
        if isinstance(exc, openai.RateLimitError):
            return (
                "[Slow down! Too many requests were sent too quickly. "
                "Wait a few seconds and try again.]"
            )
        return f"[{context}: {exc}]"

    # ------------------------------------------------------------------ #
    # Callable interface
    # ------------------------------------------------------------------ #
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
        client = self._ensure_client()
        if client is None:
            return self._missing_key_message()

        if language:
            prompt = f"Please respond in {language}.\n{prompt}"

        if generate_image:
            result = self._generate_image(client, prompt)
        elif image:
            result = self._analyze_image(client, prompt, image)
        else:
            result = self._chat(client, prompt, verbose, max_tokens)

        if speak and isinstance(result, str) and self.voice_id:
            speak_text(result, voice_id=self.voice_id)

        return result

    # Friendly aliases for the callable interface (pedagogical / spec-compatible).
    def ask(self, message: str = None, **kwargs) -> str:
        """Ask the bot a question. Same as calling the bot directly: bot(message)."""
        return self.__call__(message, **kwargs)

    def chat(self, message: str = None, **kwargs) -> str:
        """Have a conversation turn with the bot. Alias for ask()."""
        return self.__call__(message, **kwargs)

    # ------------------------------------------------------------------ #
    # Capabilities
    # ------------------------------------------------------------------ #
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
            reply = self._friendly_error("Chat error", e)
            # Don't leave a dangling user turn with no assistant reply in history.
            self.history.pop()
            return reply

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
            return self._friendly_error("Image analysis error", e)

    def _generate_image(self, client, prompt):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
        except Exception as e:
            return self._friendly_error("Image generation error", e)

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
        route = self.base_url if self.base_url else "OpenAI (direct)"
        return (
            f"<Chatbot model={self.model} "
            f"prompt={self.system_prompt[:30]}... "
            f"turns={len(self.history) // 2} "
            f"default_max_tokens={self.default_max_tokens} "
            f"voice_id={self.voice_id} "
            f"route={route}>"
        )


# Spec-compatible alias so `expressai.ChatBot(...)` also works.
ChatBot = Chatbot
