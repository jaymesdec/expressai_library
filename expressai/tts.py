# expressai/tts.py

import elevenlabs
from elevenlabs import play
import signal
import sys
import os

# ✅ Detect if running in Google Colab
try:
    import google.colab
    IN_COLAB = True
    from IPython.display import Audio, display
except ImportError:
    IN_COLAB = False

# Graceful interrupt handler
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

def speak_text(
    text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",  # ✅ MP3 works for all tiers
    filename="output.mp3",          # ✅ Default save filename
    autoplay=True
):
    """
    Converts text to speech using ElevenLabs and plays it.

    Args:
        text (str): Text to convert.
        voice_id (str): ElevenLabs voice ID.
        model_id (str): ElevenLabs model ID.
        output_format (str): Format of audio output.
        filename (str): Path to save audio file.
        autoplay (bool): Whether to auto-play the result.
    """
    if not elevenlabs.api_key:
        raise ValueError("Please set elevenlabs.api_key = 'your-api-key' before using speak_text.")

    try:
        client = elevenlabs.ElevenLabs(api_key=elevenlabs.api_key)
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format
        )
    except Exception as e:
        print(f"[TTS Error] {e}")
        return

    try:
        # ✅ Save audio to file
        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)
    except Exception as e:
        print(f"[File Save Error] {e}")
        return

    if autoplay:
        try:
            if IN_COLAB:
                display(Audio(filename, autoplay=True))
            else:
                play(filename)
        except Exception as e:
            print(f"[Audio Play Error] {e}")
    else:
        print(f"✅ Audio saved to {filename} (not played automatically).")
