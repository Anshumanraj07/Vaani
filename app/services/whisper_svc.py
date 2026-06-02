import os
import tempfile
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_bytes: bytes, file_ext: str) -> dict:
    """Processes audio using Groq's fast Whisper API and deletes the temp file immediately."""
    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name

    try:
        print("🟠 [whisper_svc.py] Sending audio to Groq Whisper API...")
        with open(temp_audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_audio_path, file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
        print("✅ [whisper_svc.py] Transcription successful!")
        return {"text": transcription.text, "language": "en"}
    except Exception as e:
        print(f"❌ [whisper_svc.py] Error during transcription: {type(e).__name__} - {str(e)}")
        raise
    finally:
        # STRICT PROCESS & DELETE RULE
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
