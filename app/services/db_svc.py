import os
from supabase import create_client, Client
from datetime import datetime

# Fallback in-memory DB if Supabase keys are not set yet
_mock_db = []

def get_db_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

def save_session(task_type: str, reaction_time: float, pattern: str, superpower: str):
    db = get_db_client()
    record = {
        "task_type": task_type,
        "reaction_time_ms": reaction_time,
        "detected_pattern": pattern,
        "superpower": superpower,
        "timestamp": datetime.now().isoformat()
    }
    if db:
        try:
            db.table("sessions").insert(record).execute()
        except Exception as e:
            print(f"Supabase Insert Error: {e}")
    else:
        _mock_db.append(record) # Fallback
    return record

def get_all_sessions():
    db = get_db_client()
    if db:
        try:
            res = db.table("sessions").select("*").execute()
            return res.data
        except Exception as e:
            print(f"Supabase Fetch Error: {e}")
            return []
    return _mock_db
