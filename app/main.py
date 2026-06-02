import os

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Vaani Backend is Online"}


@app.post("/api/v1/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    print("\n🚀 [main.py] Request received at /api/v1/analyze-audio")
    try:
        audio_bytes = await file.read()
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
    print("\n🚀 [main.py] Request received at /api/v1/analyze-interaction")
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
import sys

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
