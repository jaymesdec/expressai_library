from .chatbot import Chatbot
from .tts import speak_text
from .vision import analyze_image

def create_chatbot(system_prompt: str, model: str = "gpt-4o", max_tokens: int = 100) -> Chatbot:
    return Chatbot(system_prompt=system_prompt, model=model, max_tokens=max_tokens)
