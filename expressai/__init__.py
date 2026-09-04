from .chatbot import Chatbot, ChatBot
from .tts import speak_text
from .vision import analyze_image  # Optional: if you're exposing image analysis separately


def create_chatbot(
    system_prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 100,
    voice_id: str = None,
    api_key: str = None,
    base_url: str = None,
    classroom_token: str = None,
    student_id: str = None,
) -> Chatbot:
    """
    Creates a Chatbot instance with the specified personality and options.

    Adults can use OpenAI directly by passing ``api_key`` (or setting
    ``openai.api_key`` / the ``OPENAI_API_KEY`` env var). Students can route
    through a classroom proxy by passing ``base_url`` and ``classroom_token``,
    with no personal API key required.

    Args:
        system_prompt (str): Personality or behavior description for the chatbot.
        model (str): Model name (default: gpt-4o-mini).
        max_tokens (int): Max response length (default: 100).
        voice_id (str): Optional ElevenLabs voice ID for speaking responses.
        api_key (str): Optional OpenAI API key (adult / direct use).
        base_url (str): Optional classroom proxy endpoint (student use).
        classroom_token (str): Optional shared classroom token for the proxy.
        student_id (str): Optional student identifier for per-student rate limiting.

    Returns:
        Chatbot: A configured Chatbot object.
    """
    return Chatbot(
        system_prompt=system_prompt,
        model=model,
        max_tokens=max_tokens,
        voice_id=voice_id,
        api_key=api_key,
        base_url=base_url,
        classroom_token=classroom_token,
        student_id=student_id,
    )
