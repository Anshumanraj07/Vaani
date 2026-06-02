import os
import json
from app.utils.backoff import retry_with_backoff
from app.services.pinecone_svc import get_clinical_guidelines

_groq_client = None

def get_groq_client():
    """Lazily initialize Groq client only when needed."""
    global _groq_client
    
    if _groq_client is not None:
        return _groq_client
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable not set. Cannot generate cognitive reports.")
    
    try:
        from groq import Groq
        _groq_client = Groq(api_key=api_key)
        print("✅ [rag_svc.py] Groq client initialized successfully")
        return _groq_client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq client: {e}")

@retry_with_backoff
def generate_cognitive_report(transcribed_text: str) -> dict:
    client = get_groq_client()  # Will raise if GROQ_API_KEY is missing
    context = get_clinical_guidelines(transcribed_text)
    
    system_prompt = f"""You are a child psychology expert AI.
    Here are the clinical guidelines from the database:
    {context}
    
    Analyze the user's speech and return a JSON object with exactly these two keys:
    1. "superpower": A short empowering trait (1 sentence).
    2. "admin_report": A short clinical observation (2-3 sentences).
    
    You MUST output valid JSON format. Do not include any other text.
    """
    
    try:
        print("\n🔵 [rag_svc.py] Calling Groq LLM API with Llama 3.3...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcribed_text}
            ],
            temperature=0.3,
            timeout=15,
            response_format={"type": "json_object"} 
        )
        print("✅ [rag_svc.py] Groq response received!")
        
        result = response.choices[0].message.content
        return json.loads(result)
        
    except Exception as e:
        print(f"\n❌ [rag_svc.py] Groq LLM Error: {type(e).__name__} - {str(e)}")
        raise e