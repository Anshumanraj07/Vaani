import os
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
