# Project Vaani: System Architecture Report

**Version:** 1.0 MVP  
**Date:** June 2, 2026  
**Status:** Deployment-Ready with Known Technical Debts

---

## Executive Summary

Project Vaani is a **Multi-Modal AI Cognitive Assessment Platform** that combines voice analysis, interactive motor kinematics tracking, and clinical psychology insights to detect neurodevelopmental traits (ADHD, Dyslexia) and provide empowering "Superpower" reframing. The system integrates FastAPI, Streamlit, Supabase, Pinecone, and Groq's Llama 3.3 to deliver real-time cognitive pattern analysis.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  Streamlit Frontend (streamlit run frontend.py)                 │
│  - Tab 1: Voice Recording → Audio Upload                        │
│  - Tab 2: Interactive Puzzle → Mouse Kinematics Tracking        │
│  - Tab 3: Clinical Dashboard → Session History & Trends         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
         (API_URL from env, default: http://127.0.0.1:8000)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  FastAPI (app/main.py) - uvicorn                               │
│                                                                  │
│  Endpoints:                                                     │
│  • POST /api/v1/analyze-audio                                  │
│  • POST /api/v1/analyze-interaction                            │
│  • GET  /api/v1/history                                        │
│  • GET  / (health check)                                       │
│                                                                  │
│  Middleware: CORS (allow_origins=["*"])                        │
│  Startup: Environment variable validation                      │
└─────────────────────────────────────────────────────────────────┘
         ↓                          ↓                      ↓
    [Audio Path]             [Telemetry Path]      [History Path]
         ↓                          ↓                      ↓
┌──────────────────┐      ┌─────────────────────┐  ┌──────────────┐
│   AUDIO PIPELINE │      │  TELEMETRY PIPELINE │  │ DATA RETRIEVAL
│                  │      │                      │  │                
│ whisper_svc.py   │      │ interaction_svc.py   │  │ db_svc.py    
│                  │      │                      │  │              
│ 1. Groq Whisper  │      │ 1. Parse telemetry   │  │ get_all_    
│    (Speech→Text) │      │    (mouse kinematics)│  │ sessions()   
│                  │      │                      │  │              
│ 2. Return:       │      │ 2. Rule-based        │  │ Supabase:    
│    {text,        │      │    pattern detect:   │  │ SELECT *     
│     language}    │      │    - ADHD (RT<300ms) │  │ FROM         
│                  │      │    - Dyslexia       │  │ sessions     
└──────────────────┘      │      (reversals>3)   │  │              
         ↓                │    - Baseline        │  │ or _mock_db  
         └────────────────┤                      │  │              
                          │ 3. Return:           │  │              
          ┌───────────────┤    {detected_pattern,└──┘              
          │               │     superpower,                        
          │               │     admin_report}                      
          ↓               └─────────────────────┘                  
┌──────────────────────────────────────────────────────────────┐  
│              COGNITIVE ANALYSIS LAYER (RAG)                  │  
│                   rag_svc.py                                │  
│                                                              │  
│  generate_cognitive_report(transcribed_text):              │  
│                                                              │  
│  1. Retrieve Clinical Context:                             │  
│     ├→ get_clinical_guidelines(text)                       │  
│     │  ├→ get_pinecone_index() [Lazy Init]                │  
│     │  ├→ Generate embedding: multilingual-e5-large        │  
│     │  ├→ Query Pinecone: top_k=2                          │  
│     │  └→ Extract metadata.text from matches               │  
│     └→ context = "clinical guidelines..."                  │  
│                                                              │  
│  2. Build Prompt with RAG Context:                         │  
│     system_prompt = f"""                                    │  
│       You are a child psychology expert.                    │  
│       Clinical Guidelines: {context}                        │  
│       Analyze user speech...                                │  
│       Return JSON: {superpower, admin_report}             │  
│     """                                                      │  
│                                                              │  
│  3. Call Groq LLM:                                          │  
│     ├→ get_groq_client() [Lazy Init]                       │  
│     ├→ client.chat.completions.create()                    │  
│     │   model="llama-3.3-70b-versatile"                    │  
│     │   response_format={"type": "json_object"}            │  
│     │   temperature=0.3                                     │  
│     └→ Parse JSON response                                  │  
│                                                              │  
│  4. Return: {superpower, admin_report}                     │  
│     @retry_with_backoff (exponential backoff, 4 attempts)  │  
│                                                              │  
└──────────────────────────────────────────────────────────────┘  
         ↓ Inject Results Back
         │
         ↓
┌──────────────────────────────────────────────────────────────┐
│           PERSISTENCE & DATA LAYER                            │
│                                                                │
│  db_svc.py:                                                   │
│  • save_session() → Supabase OR _mock_db fallback            │
│  • get_all_sessions() → Supabase OR _mock_db                │
│                                                                │
│  Table: "sessions" (Supabase)                                │
│  ├─ task_type: string                                        │
│  ├─ reaction_time_ms: float                                  │
│  ├─ detected_pattern: string                                 │
│  ├─ superpower: string                                       │
│  └─ timestamp: ISO8601                                       │
│                                                                │
│  RAG Vector DB: Pinecone                                      │
│  ├─ Index: "vaani-knowledge"                                │
│  ├─ Model: multilingual-e5-large                            │
│  ├─ Metadata: {text, source, ...}                           │
│  └─ Top-K: 2 results per query                              │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. Frontend Layer (Streamlit)
**File:** `frontend.py`

**Responsibilities:**
- Record audio input
- Render interactive game (mouse tracking)
- Display session history with Pandas dataframe
- Call backend APIs

**Key Features:**
- `API_URL` environment variable support (default: `http://127.0.0.1:8000`)
- Embedded HTML/JS for real-time mouse kinematics
- Tab-based UI (Voice, Interactive, Dashboard)

**Data Flows:**
1. **Voice Tab:** Audio bytes → POST `/api/v1/analyze-audio`
2. **Interactive Tab:** Mouse telemetry JSON → POST `/api/v1/analyze-interaction`
3. **Dashboard Tab:** GET `/api/v1/history` → Pandas display

---

### 2. API Gateway (FastAPI)
**File:** `app/main.py`

**Endpoints:**

| Method | Path | Input | Output | Notes |
|--------|------|-------|--------|-------|
| GET | `/` | - | `{message}` | Health check |
| POST | `/api/v1/analyze-audio` | WAV audio file | `{transcription, cognitive_analysis}` | Streams to Whisper → RAG |
| POST | `/api/v1/analyze-interaction` | `TaskTelemetry` JSON | `{analysis}` | Rule-based + DB save |
| GET | `/api/v1/history` | - | `{data: [sessions]}` | Supabase OR in-memory |

**Startup Validation:**
```python
@app.on_event("startup")
async def startup_event():
    # Checks required: GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
    # Checks optional: PINECONE_API_KEY
    # Logs missing variables
```

**CORS Policy:**
- `allow_origins=["*"]` ⚠️ **Insecure for production** (see Technical Debts)
- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

---

### 3. Audio Processing
**File:** `app/services/whisper_svc.py`

**Function:** `transcribe_audio(file_bytes, file_ext) → dict`

**Flow:**
1. Write bytes to temporary file (temp directory)
2. Open file and send to Groq Whisper API (`whisper-large-v3`)
3. Return `{text, language}`
4. **Cleanup:** Delete temp file in `finally` block

**Current Issue:** ⚠️ Module-level Groq initialization (not lazy)

---

### 4. Motor Kinematics Analysis
**File:** `app/services/interaction_svc.py`

**Function:** `analyze_telemetry(data: dict) → dict`

**Input Schema:** `TaskTelemetry`
```python
{
    task_type: str,           # e.g., "spatial_rotation", "go_no_go"
    age_group: str,           # e.g., "19-25"
    action_initiation_time_ms: float,
    total_response_time_ms: float,
    cursor_reversals: int,
    is_correct: bool
}
```

**Logic:**
```
IF task_type == "go_no_go" AND rt < 300ms AND NOT is_correct:
    pattern = "ADHD Trait (Impulsivity)"
ELIF task_type == "spatial_rotation" AND reversals > 3:
    pattern = "Dyslexia Trait (Hesitation)"
ELSE:
    pattern = "Baseline/Neurotypical"
```

**Output:**
```python
{
    detected_pattern: str,      # Clinical trait or baseline
    superpower: str,            # Empowering reframe
    admin_report: str           # Detailed metrics
}
```

---

### 5. Retrieval-Augmented Generation (RAG)
**Files:** `app/services/rag_svc.py`, `app/services/pinecone_svc.py`

#### Pinecone Integration
**Function:** `get_clinical_guidelines(query_text: str) → str`

**Flow:**
1. Lazy-init Pinecone via `get_pinecone_index()`
2. Generate embedding: `multilingual-e5-large` model
3. Query index "vaani-knowledge" with `top_k=2`
4. Extract `match.metadata.get("text", "")`
5. Join results with `\n`
6. Return context string (or empty if unavailable)

**Graceful Degradation:**
- If `PINECONE_API_KEY` is missing → logs warning, returns empty context
- If query fails → catches exception, returns empty string
- RAG is optional; system works without it

#### Groq LLM Integration
**Function:** `generate_cognitive_report(transcribed_text: str) → dict`

**Flow:**
1. Lazy-init Groq via `get_groq_client()`
2. Fetch RAG context
3. Build system prompt with injected context
4. Call Groq Llama 3.3 with:
   - `temperature=0.3` (low temperature for consistency)
   - `response_format={"type": "json_object"}` (enforces JSON)
   - `timeout=15` seconds
5. Parse JSON response
6. Return `{superpower, admin_report}`
7. Retry on failure (exponential backoff, 4 attempts max)

**Error Handling:**
- If `GROQ_API_KEY` missing → raises RuntimeError (fatal)
- If LLM call fails → retries with backoff, then raises

---

### 6. Data Persistence
**File:** `app/services/db_svc.py`

#### Supabase Integration
**Function:** `save_session(task_type, reaction_time, pattern, superpower) → dict`

**Behavior:**
- If Supabase keys present: INSERT record into "sessions" table
- If Supabase keys missing: Append to in-memory `_mock_db` list
- Catches Supabase errors, continues silently (logs warning)

**Function:** `get_all_sessions() → list`

**Behavior:**
- If Supabase keys present: SELECT * from "sessions"
- If Supabase keys missing: Return `_mock_db`
- Catches errors, returns empty list on failure

**Database Schema (Supabase):**
| Column | Type | Notes |
|--------|------|-------|
| task_type | string | e.g., "spatial_rotation" |
| reaction_time_ms | float | Response time in milliseconds |
| detected_pattern | string | Clinical trait or baseline |
| superpower | string | Empowering reframe |
| timestamp | ISO8601 | ISO format datetime |

---

## Environment Variables

**Required:**
- `GROQ_API_KEY` - Groq API key for Whisper + Llama 3.3
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anonymous/service key

**Optional:**
- `PINECONE_API_KEY` - Pinecone API key (RAG feature)
- `API_URL` - Backend URL for Streamlit (default: `http://127.0.0.1:8000`)

**Loaded via:** `python-dotenv` in `main.py` with `load_dotenv()`

---

## Deployment Topology

```
Render Deployment:
┌─────────────────────────────────────┐
│  Render Web Service (FastAPI)      │
│  Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
│  Environment: {GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, PINECONE_API_KEY}
└─────────────────────────────────────┘

Streamlit Community Cloud Deployment:
┌─────────────────────────────────────┐
│  Streamlit App                      │
│  Start Command: streamlit run frontend.py
│  Environment: {API_URL=<render-url>}
└─────────────────────────────────────┘

External Services:
├─ Groq Cloud (Whisper + Llama 3.3)
├─ Supabase (PostgreSQL + Auth)
└─ Pinecone (Vector DB)
```

---

## Known Limitations & Technical Debts

See separate "Technical Debts" section below.

