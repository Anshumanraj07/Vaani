from pydantic import BaseModel, Field

class TaskTelemetry(BaseModel):
    user_id: str = Field(..., description="Supabase UUID of the logged-in user")
    task_type: str
    age_group: str
    action_initiation_time_ms: float = Field(..., gt=0, le=30000)
    total_response_time_ms: float = Field(..., gt=0, le=60000)
    cursor_reversals: int = Field(..., ge=0, le=1000)
    is_correct: bool