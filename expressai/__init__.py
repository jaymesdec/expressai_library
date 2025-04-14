from .chatbot import Chatbot
from .tts import speak_text
from .vision import analyze_image  # Optional: if you're exposing image analysis separately

def create_chatbot(system_prompt: str, model: str = "gpt-4o", max_tokens: int = 100, voice_id: str = None) -> Chatbot:
    """
    Creates a Chatbot instance with the specified personality and options.

    Args:
        system_prompt (str): Personality or behavior description for the chatbot.
        model (str): OpenAI model name (default: gpt-4o).
        max_tokens (int): Max response length (default: 100).
        voice_id (str): Optional ElevenLabs voice ID for speaking responses.

    Returns:
        Chatbot: A configured Chatbot object.
    """
    return Chatbot(system_prompt=system_prompt, model=model, max_tokens=max_tokens, voice_id=voice_id)
