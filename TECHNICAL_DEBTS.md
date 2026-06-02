# Technical Debts & Known Issues: Project Vaani v1.0

**Last Updated:** June 2, 2026  
**Priority for v2.0:** Critical fixes required before scaling

---

## Critical Issues (Fix Before Production)

### 1. ⚠️ CORS Policy is Too Permissive
**File:** `app/main.py`, Line 17-22  
**Severity:** HIGH  
**Issue:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Allows ANY origin
    allow_credentials=True,  # ❌ Combined with ["*"] = insecure
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem:**
- Allows Cross-Origin requests from any website
- Combined with `allow_credentials=True`, violates CORS security model
- Exposes API to CSRF attacks
- In production, this enables malicious websites to call your API on behalf of users

**Recommended Fix:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Local Streamlit dev
        "https://vaani.streamlit.app",  # Production Streamlit URL
        os.getenv("FRONTEND_URL"),  # Configurable
    ],
    allow_credentials=False,  # Disable if not needed
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

**Priority:** Fix before ANY cloud deployment

---

### 2. ⚠️ Audio File Upload: No Size Validation
**File:** `app/main.py`, Line 34-60  
**Severity:** MEDIUM  
**Issue:**
```python
@app.post("/api/v1/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()  # ❌ No size check
```

**Problem:**
- User can upload 1GB+ audio file, consuming all memory
- No timeout protection
- Groq Whisper has duration limits (usually 25MB)

**Recommended Fix:**
```python
@app.post("/api/v1/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 25MB)")
    # ... rest of function
```

**Priority:** Fix before public deployment

---

### 3. ⚠️ Whisper Service: Module-Level Groq Client (Not Lazy)
**File:** `app/services/whisper_svc.py`, Line 4  
**Severity:** MEDIUM  
**Issue:**
```python
# Initialize Groq client at import time
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # ❌ NOT lazy-loaded
```

**Problem:**
- Same issue we fixed for Pinecone/RAG
- If `GROQ_API_KEY` is invalid/missing, crashes at startup
- Different from the lazy pattern we applied to `rag_svc.py`

**Recommended Fix:**
Same lazy pattern as `rag_svc.py`:
```python
_whisper_client = None

def get_whisper_client():
    global _whisper_client
    if _whisper_client is not None:
        return _whisper_client
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    
    _whisper_client = Groq(api_key=api_key)
    return _whisper_client

def transcribe_audio(file_bytes, file_ext):
    client = get_whisper_client()  # Lazy init
    # ... rest
```

**Priority:** HIGH (consistency & reliability)

---

## High-Priority Issues (Before v2.0 Features)

### 4. ⚠️ Error Handling: Audio Analysis Swallows Errors
**File:** `app/main.py`, Line 43-47  
**Severity:** MEDIUM  
**Issue:**
```python
cognitive_analysis = {}
try:
    cognitive_analysis = generate_cognitive_report(transcription.get("text", ""))
except Exception as e:
    cognitive_analysis = {"error": "Cognitive analysis failed", "details": str(e)}
```

**Problem:**
- Frontend expects `data['cognitive_analysis']['superpower']` 
- If error occurs, the key doesn't exist → UI crash
- Error is "handled" but silently corrupts response structure

**Recommended Fix:**
```python
try:
    cognitive_analysis = generate_cognitive_report(transcription.get("text", ""))
except Exception as e:
    # Return HTTP error instead of 200 with error payload
    raise HTTPException(
        status_code=500,
        detail=f"Cognitive analysis failed: {str(e)}"
    )
```

**Priority:** MEDIUM (affects reliability)

---

### 5. ⚠️ No Input Validation: TaskTelemetry Schema
**File:** `app/schemas/telemetry.py`  
**Severity:** MEDIUM  
**Issue:**
```python
class TaskTelemetry(BaseModel):
    task_type: str  # ❌ Any string accepted
    age_group: str  # ❌ No validation
    action_initiation_time_ms: float  # ❌ Can be negative
    total_response_time_ms: float  # ❌ Can be 0 or negative
    cursor_reversals: int  # ❌ Can be negative
    is_correct: bool
```

**Problem:**
- Accepts negative reaction times
- Accepts invalid task types
- No range validation
- Malformed data passes through to database

**Recommended Fix:**
```python
from pydantic import BaseModel, Field, validator

class TaskTelemetry(BaseModel):
    task_type: str = Field(..., regex="^(spatial_rotation|go_no_go|other_task)$")
    age_group: str = Field(..., regex="^(13-18|19-25|26-35|35+)$")
    action_initiation_time_ms: float = Field(..., gt=0, le=10000)
    total_response_time_ms: float = Field(..., gt=0, le=30000)
    cursor_reversals: int = Field(..., ge=0, le=1000)
    is_correct: bool
    
    @validator('task_type')
    def validate_task_type(cls, v):
        valid_tasks = {"spatial_rotation", "go_no_go"}
        if v not in valid_tasks:
            raise ValueError(f"task_type must be one of {valid_tasks}")
        return v
```

**Priority:** MEDIUM (data quality)

---

### 6. ⚠️ Hardcoded Pinecone Index Name
**File:** `app/services/pinecone_svc.py`, Line 22  
**Severity:** LOW  
**Issue:**
```python
_index = _pc.Index("vaani-knowledge")  # ❌ Hardcoded
```

**Problem:**
- Index name not configurable
- If you want to test with different indexes, must change code
- Not environment-aware

**Recommended Fix:**
```python
index_name = os.getenv("PINECONE_INDEX_NAME", "vaani-knowledge")
_index = _pc.Index(index_name)
```

**Priority:** LOW (cosmetic, low impact)

---

## Medium-Priority Issues (Technical Debt)

### 7. ⚠️ No Structured Logging
**Files:** Multiple  
**Severity:** MEDIUM  
**Issue:**
```python
print("✅ [main.py] Startup validation complete...")  # ❌ Basic print
print(f"❌ [pinecone_svc.py] Failed to initialize Pinecone: {e}")
```

**Problem:**
- Print statements don't go to logs
- No structured format (timestamp, level, context)
- Hard to debug in production
- No log aggregation
- Emoji output not suitable for production logs

**Recommended Fix:**
```python
import logging

logger = logging.getLogger(__name__)

# Instead of:
print("✅ [main.py] Startup validation complete...")

# Use:
logger.info("Startup validation complete", extra={"module": "main"})
logger.error(f"Failed to initialize Pinecone", exc_info=True)
```

**Priority:** MEDIUM (improves observability)

---

### 8. ⚠️ No Request Rate Limiting
**File:** `app/main.py`  
**Severity:** MEDIUM  
**Issue:**
- No rate limit middleware
- Can be abused: infinite voice submissions, telemetry spam
- No throttling mechanism

**Recommended Fix:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/analyze-audio")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def analyze_audio(...):
    ...
```

**Priority:** MEDIUM (production readiness)

---

### 9. ⚠️ No Authentication/Authorization
**File:** `app/main.py`  
**Severity:** HIGH (if multi-user)  
**Issue:**
- No user authentication
- No session isolation
- Anyone can see anyone's history

**Problem:**
- All `/api/v1/history` requests return ALL sessions globally
- No privacy/isolation
- Suitable for testing, NOT for production with real users

**Recommended Fix (Future):**
```python
from fastapi.security import HTTPBearer, HTTPAuthCredential

security = HTTPBearer()

@app.post("/api/v1/analyze-audio")
async def analyze_audio(
    file: UploadFile,
    credentials: HTTPAuthCredential = Depends(security)
):
    user_id = verify_token(credentials.credentials)  # Validate JWT
    # ... rest of function
```

**Priority:** HIGH (critical for multi-user deployment)

---

### 10. ⚠️ No Input Sanitization
**File:** Multiple  
**Severity:** MEDIUM  
**Issue:**
- User audio/text passed directly to LLM
- No sanitization for injection attacks
- Metadata stored without validation

**Recommended Fix:**
```python
import bleach
from html import escape

def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize user input text."""
    if len(text) > max_length:
        raise ValueError(f"Text exceeds {max_length} characters")
    return escape(text.strip())
```

**Priority:** MEDIUM (security)

---

### 11. ⚠️ Supabase Fallback is Risky
**File:** `app/services/db_svc.py`  
**Severity:** MEDIUM  
**Issue:**
```python
_mock_db = []  # In-memory list

def save_session(...):
    if db:
        # Try Supabase
    else:
        _mock_db.append(record)  # ❌ Data lost on restart
```

**Problem:**
- In-memory fallback loses all data on app restart
- Production won't know data was lost
- Misleading: looks like it's working, but data is ephemeral

**Recommended Fix:**
```python
def save_session(...):
    if not db:
        logger.error("Supabase unavailable, data will be lost on restart")
        raise RuntimeError("Cannot save session: database unavailable")
    # ... save to Supabase only
```

**Priority:** MEDIUM (data safety)

---

## Low-Priority Issues (Code Quality)

### 12. ⚠️ Inline HTML/JS in Streamlit
**File:** `frontend.py`, Lines 85-180  
**Severity:** LOW  
**Issue:**
- Large HTML/JS block embedded in Python
- Hard to maintain, no syntax highlighting
- Hard to test independently

**Recommended Fix (Future):**
Extract to separate file `app/static/game.js` and `app/static/game.html`, then load:
```python
with open("app/static/game.html") as f:
    game_html = f.read()
components.html(game_html)
```

**Priority:** LOW (maintenance, not functional)

---

### 13. ⚠️ Hardcoded Test Values in Frontend
**File:** `frontend.py` (JavaScript)  
**Severity:** LOW  
**Issue:**
```javascript
let payload = {
    "task_type": "spatial_rotation",  // ❌ Hardcoded
    "age_group": "19-25",  // ❌ Hardcoded
    ...
};
```

**Problem:**
- No ability to configure from UI
- Same task type for all users
- Age group not collected from user

**Recommended Fix (Future):**
Allow user to select task type and age group from Streamlit UI
```python
task_type = st.selectbox("Task Type", ["spatial_rotation", "go_no_go"])
age_group = st.selectbox("Age Group", ["13-18", "19-25", ...])
```

**Priority:** LOW (feature enhancement)

---

### 14. ⚠️ No Error Boundary in Streamlit
**File:** `frontend.py`  
**Severity:** LOW  
**Issue:**
- If backend crashes, frontend shows generic error
- No retry mechanism
- No user guidance

**Recommended Fix (Future):**
```python
st.error("❌ Backend Error. Please:")
st.write("1. Check your internet connection")
st.write("2. Verify backend is running at: " + API_URL)
st.write("3. Try again in 30 seconds")

if st.button("🔄 Retry"):
    st.rerun()
```

**Priority:** LOW (UX improvement)

---

### 15. ⚠️ Missing Environment Validation for `whisper_svc.py`
**File:** `app/services/whisper_svc.py`  
**Severity:** MEDIUM  
**Issue:**
- Uses same `GROQ_API_KEY` as RAG
- Module-level init means startup fails if key is missing
- No lazy loading pattern

**Recommended Fix:**
Apply same lazy-init pattern as `rag_svc.py`

**Priority:** MEDIUM

---

## Dependencies & Versions

**Current Stack:**
- FastAPI 0.109.0
- Streamlit (version unknown, check requirements.txt)
- Supabase Python client
- Groq Python client (0.4.2)
- Pinecone (latest from requirements)
- Tenacity (retry library, 8.2.3)

**Known Version Issues:**
- ✅ All packages support lazy imports
- ✅ Groq 0.4.2 supports JSON response format
- ✅ Pinecone recent versions support inference API
- ✅ Supabase Python client is stable

---

## Testing Gaps

### Missing Tests
1. **Unit Tests**
   - `analyze_telemetry()` rule logic
   - `get_clinical_guidelines()` with mock Pinecone
   - `generate_cognitive_report()` with mock Groq

2. **Integration Tests**
   - Full audio → transcription → cognitive analysis flow
   - Supabase write + read (e2e)
   - Pinecone embedding + query (e2e)

3. **Load Tests**
   - Concurrent audio uploads
   - Rate limiting behavior
   - Memory usage with large session history

---

## Deployment Checklist for Production

- [ ] Update CORS `allow_origins` from `["*"]` to specific domains
- [ ] Add file size validation to `/api/v1/analyze-audio`
- [ ] Apply lazy-init pattern to `whisper_svc.py`
- [ ] Add structured logging throughout
- [ ] Implement rate limiting on all endpoints
- [ ] Add input validation to `TaskTelemetry` schema
- [ ] Remove or make configurable: Pinecone index name
- [ ] Add authentication/authorization layer
- [ ] Set up log aggregation (e.g., Sentry, DataDog)
- [ ] Remove in-memory `_mock_db` fallback; fail fast instead
- [ ] Extract inline HTML/JS to separate files
- [ ] Add API documentation (FastAPI auto-docs: `/docs`)
- [ ] Set up monitoring/alerting on backend

---

## Version 2.0 Roadmap

**Priority 1 (Critical for Multi-User):**
- [ ] User authentication + per-user data isolation
- [ ] CORS security hardening
- [ ] Input validation & sanitization
- [ ] Structured logging

**Priority 2 (Scaling & Reliability):**
- [ ] Rate limiting + throttling
- [ ] Database connection pooling
- [ ] Async task queue (e.g., Celery) for long-running jobs
- [ ] Caching layer (Redis) for RAG results

**Priority 3 (Features):**
- [ ] New game types (go-no-go, n-back, stroop)
- [ ] Multi-language support
- [ ] Detailed clinical reports PDF export
- [ ] Admin dashboard for clinicians

**Priority 4 (Polish):**
- [ ] Mobile-responsive frontend
- [ ] Dark mode UI
- [ ] Offline mode
- [ ] Analytics & user engagement tracking

---

## References

- [OWASP CORS Misconfiguration](https://owasp.org/www-community/CORS_policy_bypassing)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [FastAPI Rate Limiting (Slowapi)](https://github.com/laurentS/slowapi)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)

