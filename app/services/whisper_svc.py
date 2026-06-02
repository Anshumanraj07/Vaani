import os
import tempfile

_whisper_client = None

def get_whisper_client():
    """Lazily initialize Groq client for Whisper only when needed."""
    global _whisper_client
    
    if _whisper_client is not None:
        return _whisper_client
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable not set. Cannot transcribe audio.")
    
    try:
        from groq import Groq
        _whisper_client = Groq(api_key=api_key)
        print("✅ [whisper_svc.py] Groq Whisper client initialized successfully")
        return _whisper_client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq Whisper client: {e}")

def transcribe_audio(file_bytes: bytes, file_ext: str) -> dict:
    """Processes audio using Groq's fast Whisper API and deletes the temp file immediately."""
    client = get_whisper_client()  # Lazy init
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
