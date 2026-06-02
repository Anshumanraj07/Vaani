from pydantic import BaseModel

class TaskTelemetry(BaseModel):
    task_type: str
    age_group: str
    action_initiation_time_ms: float
    total_response_time_ms: float
    cursor_reversals: int
    is_correct: bool
