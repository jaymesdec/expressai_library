# expressai/tts.py

import elevenlabs
from elevenlabs import play
import signal
import sys

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
    output_format="pcm_44100",  # ✅ Raw format for Colab compatibility
    autoplay=True
):
    """
    Converts text to speech using ElevenLabs and plays it.

    Args:
        text (str): Text to convert.
        voice_id (str): ElevenLabs voice ID.
        model_id (str): ElevenLabs model ID.
        output_format (str): Format of audio output.
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

    if autoplay:
        try:
            if IN_COLAB:
                # ✅ Convert generator to raw audio bytes
                audio_bytes = b"".join(audio)
                display(Audio(data=audio_bytes, autoplay=True, rate=44100))
            else:
                play(audio)
        except KeyboardInterrupt:
            print("\nAudio playback interrupted by user.")
        except Exception as e:
            print(f"[Audio Play Error] {e}")
    else:
        print("✅ Audio generated (not played automatically).")
