# expressai/chatbot.py
import openai
import base64
import os
from expressai.tts import speak_text

class Chatbot:
    def __init__(self, system_prompt: str, model: str = "gpt-4o", max_tokens: int = 100, voice_id: str = None):
        """
        Initialize the chatbot with a system prompt, model, default max_tokens, and optional voice_id.
        """
        self.system_prompt = system_prompt
        self.model = model
        self.history = []
        self.default_max_tokens = max_tokens
        self.voice_id = voice_id

    def __call__(self, prompt: str = None, image: str = None, verbose: bool = False, max_tokens: int = None, speak: bool = False) -> str:
        """
        Send a message to the chatbot and receive a response.

        Args:
            prompt (str): User prompt or question.
            image (str): Optional image file path (for GPT-4o vision input).
            verbose (bool): Whether to print the prompt being sent.
            max_tokens (int): Optional override of default max_tokens.
            speak (bool): If True and voice_id is set, plays the response using TTS.

        Returns:
            str: The assistant's response.
        """
        try:
            client = openai.OpenAI(api_key=openai.api_key)
        except Exception as e:
            return f"[OpenAI client error: {e}]"

        # Vision mode
        if image:
            if not prompt:
                prompt = "What do you see in this image?"

            try:
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
                reply = response.output_text.strip()
            except Exception as e:
                return f"[Image analysis error: {e}]"

            if speak and self.voice_id:
                speak_text(reply, voice_id=self.voice_id)
            return reply

        # Regular chat mode
        if not prompt:
            return "[Error: You must provide a prompt when no image is given.]"

        self.history.append({"role": "user", "content": prompt})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        if verbose:
            print("🧠 Prompt sent to model:")
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

        if speak and self.voice_id:
            speak_text(reply, voice_id=self.voice_id)

        return reply

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
