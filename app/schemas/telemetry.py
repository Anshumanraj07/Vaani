from pydantic import BaseModel, Field

class TaskTelemetry(BaseModel):
    task_type: str
    age_group: str
    action_initiation_time_ms: float = Field(..., gt=0, le=30000, description="Action initiation time in ms, must be positive and <= 30000")
    total_response_time_ms: float = Field(..., gt=0, le=60000, description="Total response time in ms, must be positive and <= 60000")
    cursor_reversals: int = Field(..., ge=0, le=1000, description="Number of direction reversals, must be >= 0 and <= 1000")
    is_correct: bool
