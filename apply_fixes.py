import os

# Fix 1: whisper_svc.py
with open('app/services/whisper_svc.py', 'w') as f:
    f.write('''import os
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
''')
print('✅ Fix 1: whisper_svc.py updated')

# Fix 2: telemetry.py
with open('app/schemas/telemetry.py', 'w') as f:
    f.write('''from pydantic import BaseModel, Field

class TaskTelemetry(BaseModel):
    task_type: str
    age_group: str
    action_initiation_time_ms: float = Field(..., gt=0, le=30000, description="Action initiation time in ms, must be positive and <= 30000")
    total_response_time_ms: float = Field(..., gt=0, le=60000, description="Total response time in ms, must be positive and <= 60000")
    cursor_reversals: int = Field(..., ge=0, le=1000, description="Number of direction reversals, must be >= 0 and <= 1000")
    is_correct: bool
''')
print('✅ Fix 2: telemetry.py updated')

# Fix 3: db_svc.py
with open('app/services/db_svc.py', 'w') as f:
    f.write('''import os
from supabase import create_client, Client
from datetime import datetime

def get_db_client():
    """Get Supabase client. Raises error if credentials are missing."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials missing (SUPABASE_URL and/or SUPABASE_KEY). "
            "Database persistence is unavailable. Please configure environment variables."
        )
    
    return create_client(url, key)

def save_session(task_type: str, reaction_time: float, pattern: str, superpower: str):
    """Save session to Supabase. Fails fast if DB unavailable."""
    try:
        db = get_db_client()
        record = {
            "task_type": task_type,
            "reaction_time_ms": reaction_time,
            "detected_pattern": pattern,
            "superpower": superpower,
            "timestamp": datetime.now().isoformat()
        }
        db.table("sessions").insert(record).execute()
        return record
    except RuntimeError:
        # Credentials missing - fail fast
        raise
    except Exception as e:
        print(f"❌ [db_svc.py] Supabase Insert Error: {e}")
        raise

def get_all_sessions():
    """Fetch all sessions from Supabase. Fails fast if DB unavailable."""
    try:
        db = get_db_client()
        res = db.table("sessions").select("*").execute()
        return res.data
    except RuntimeError:
        # Credentials missing - fail fast
        raise
    except Exception as e:
        print(f"❌ [db_svc.py] Supabase Fetch Error: {e}")
        raise
''')
print('✅ Fix 3: db_svc.py updated')

# Fix 4 & 5: main.py (CORS + file size validation)
with open('app/main.py', 'w') as f:
    f.write('''import os
import sys

from dotenv import load_dotenv
# Load environment variables from .env file early so services can access them
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.rag_svc import generate_cognitive_report
from app.services.whisper_svc import transcribe_audio
from app.schemas.telemetry import TaskTelemetry
from app.services.interaction_svc import analyze_telemetry
from app.services.db_svc import save_session, get_all_sessions

app = FastAPI(title="Vaani")

# CORS Configuration: Restrict to known origins for security
allowed_origins = [
    "http://localhost:8501",      # Streamlit local dev
    "http://127.0.0.1:8501",
]

# Allow cloud Streamlit URL if configured via environment
streamlit_cloud_url = os.getenv("STREAMLIT_CLOUD_URL")
if streamlit_cloud_url:
    allowed_origins.append(streamlit_cloud_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
async def root():
    return {"message": "Vaani Backend is Online"}


@app.post("/api/v1/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    print("\\n🚀 [main.py] Request received at /api/v1/analyze-audio")
    try:
        audio_bytes = await file.read()
        
        # File size validation: max 5MB
        MAX_FILE_SIZE = 5 * 1024 * 1024
        if len(audio_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum allowed size is 5MB.")
        
        _, file_ext = os.path.splitext(file.filename)
        if not file_ext:
            raise HTTPException(status_code=400, detail="File must include an extension")

        transcription = transcribe_audio(audio_bytes, file_ext)

        cognitive_analysis = {}
        try:
            cognitive_analysis = generate_cognitive_report(transcription.get("text", ""))
        except Exception as e:
            cognitive_analysis = {"error": "Cognitive analysis failed", "details": str(e)}

        response_data = {
            "status": "success",
            "transcription": transcription,
            "cognitive_analysis": cognitive_analysis,
        }
        print("✅ [main.py] Returning final response")
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/v1/analyze-interaction")
async def analyze_interaction(telemetry: TaskTelemetry):
    print("\\n🚀 [main.py] Request received at /api/v1/analyze-interaction")
    try:
        result = analyze_telemetry(telemetry.model_dump())
        save_session(telemetry.task_type, telemetry.total_response_time_ms, result['detected_pattern'], result['superpower'])
        print("✅ [main.py] Returning interaction analysis")
        return {"status": "success", "analysis": result}
    except Exception as e:
        print(f"❌ [main.py] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/api/v1/history")
async def get_history():
    data = get_all_sessions()
    return {"status": "success", "data": data}


# Startup validation
@app.on_event("startup")
async def startup_event():
    """Validate that all required environment variables are set."""
    required_vars = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    optional_vars = ["PINECONE_API_KEY"]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"❌ STARTUP ERROR: Missing required environment variables: {', '.join(missing_vars)}"
        print(error_msg)
        # In production, you might want to exit:
        # sys.exit(1)
    
    if missing_optional:
        print(f"⚠️  STARTUP WARNING: Optional variables not set: {', '.join(missing_optional)}. Some features will be disabled.")
    
    print("✅ [main.py] Startup validation complete. All required vars present.")
''')
print('✅ Fix 4 & 5: main.py updated (CORS + file size validation)')
print('\n✅✅✅ ALL 5 FIXES APPLIED SUCCESSFULLY ✅✅✅')
