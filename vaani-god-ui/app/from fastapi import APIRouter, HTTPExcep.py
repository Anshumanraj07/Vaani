from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

# Router setup (apne main app mein isko include kar lena)
router = APIRouter()

# 1. The Pydantic Model (Ab user_id ke sath)
class TaskTelemetry(BaseModel):
    user_id: str = Field(..., description="Supabase UUID of the logged-in user")
    task_type: str = Field(..., description="E.g., Stroop, Spatial_Tracker")
    age_group: str
    action_initiation_time_ms: float = Field(..., gt=0, le=30000)
    total_response_time_ms: float = Field(..., gt=0, le=60000)
    cursor_reversals: int = Field(..., ge=0, le=1000)
    is_correct: bool

# 2. The API Endpoint
@router.post("/log-session")
async def log_telemetry_session(data: TaskTelemetry, supabase_client: Any):
    """
    Frontend se data aayega aur seedha game_sessions table mein jayega.
    """
    try:
        # JSONB format ready karna (game_sessions table ke metrics column ke liye)
        session_payload = {
            "user_id": data.user_id,
            "game_type": data.task_type,
            "metrics": {
                "age_group": data.age_group,
                "action_initiation_time_ms": data.action_initiation_time_ms,
                "total_response_time_ms": data.total_response_time_ms,
                "cursor_reversals": data.cursor_reversals,
                "is_correct": data.is_correct
            }
        }
        
        # Supabase mein Insert
        response = supabase_client.table("game_sessions").insert(session_payload).execute()
        
        return {"status": "success", "message": "Telemetry logged for user", "data": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log telemetry: {str(e)}")