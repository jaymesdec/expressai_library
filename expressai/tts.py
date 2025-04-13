# expressai/tts.py

import elevenlabs
from elevenlabs import play
import signal
import sys

# Detect if running inside Google Colab
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    from IPython.display import Audio, display

# Global variable to track if we should stop playback
should_stop_playback = False

def signal_handler(sig, frame):
    global should_stop_playback
    should_stop_playback = True
    print("\nStopping audio playback...")
    sys.exit(0)

# Register the signal handler for graceful interruption
signal.signal(signal.SIGINT, signal_handler)

def speak_text(
    text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
    autoplay=True
):
    """
    Converts text to speech using ElevenLabs and plays it.

    Args:
        text (str): The input text to convert.
        voice_id (str): The ElevenLabs voice ID.
        model_id (str): The ElevenLabs model ID.
        output_format (str): Audio format (e.g., mp3_44100_128).
        autoplay (bool): Whether to play the audio automatically.
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
                from io import BytesIO
                display(Audio(BytesIO(audio), autoplay=True))
            else:
                play(audio)
        except KeyboardInterrupt:
            print("\nAudio playback interrupted by user.")
        except Exception as e:
            print(f"[Audio Play Error] {e}")