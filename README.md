<div align="center">

![Vaani Logo](public/logo.png)

<h1>Vaani</h1>
<p><strong>Cognitive Diagnostic & Biomarker Dashboard (MVP v1.0)</strong></p>
</div>

## 1. Project Overview
Vaani is a lightweight, cloud-native cognitive diagnostic dashboard. It functions as a digital biomarker tracking system, analyzing kinematic interactions and speech patterns to establish a clinical baseline for cognitive load and executive function.

## 2. Architecture & Tech Stack
Designed for zero-cost deployment and rapid execution.
* **Frontend:** Next.js, Tailwind CSS, Framer Motion (Deployed via Vercel).
* **Backend:** Python, FastAPI, Dockerized container (Deployed via Render).
* **Database & Auth:** Supabase (PostgreSQL) secured with strict Row Level Security (RLS) and JWT authentication.
* **AI & Inference:** Groq API (Llama 3.3) for lightning-fast text processing, Groq Whisper for audio transcription.
* **Data Orchestration:** LlamaIndex (SummaryIndex) for lightweight Retrieval-Augmented Generation (RAG).

## 3. Core Modules
* **Kinematic Telemetry (Game Sessions):** Tracks user motor latency (ms), action initiation time, and impulse control errors (cursor reversals) via tasks like the Stroop Test and Spatial Tracker.
* **Vocal Biomarker Analysis:** Captures real-time audio prompts, transcribes via Whisper, and analyzes speech cadence for hesitation and structural patterns.
* **Diagnostic Synthesizer (RAG):** Aggregates historical telemetry logs stored in Supabase to generate a minimalist, objective 3-sentence clinical summary.

## 4. Strategic Engineering Constraints (v1.0)
* **Lean Deployment:** Bypassed heavy Vector Databases (like Pinecone) in favor of LlamaIndex Summary RAG to keep infrastructure costs at $0 while proving the architectural concept.
* **Synchronous Processing:** Utilized direct API endpoints over asynchronous queues (Redis/Celery) to maintain a simplistic, easy-to-debug monolithic backend suitable for early-stage prototype demonstration.

## 5. Current Status
**100% Operational.** The system successfully authenticates users, captures multimodal data (audio/kinematics), processes diagnostics via LLM, and securely writes to a protected database. Ready for portfolio integration and technical capability demonstration.
