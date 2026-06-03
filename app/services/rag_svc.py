import os
import json
from groq import Groq

def generate_cognitive_report(transcription_text: str):
    """
    Analyzes transcribed text for clinical cognitive markers (ADHD, PTSD, Executive Load).
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return {"primary_marker": "API Error", "clinical_notes": "Groq API key not configured."}

    client = Groq(api_key=groq_api_key)

    system_prompt = """You are a strict, objective Clinical Cognitive Analyst AI. 
    Analyze the provided speech transcription for potential behavioral markers such as ADHD (impulsivity, tangential thoughts), PTSD (avoidance, hyperarousal), Anxiety, or Executive Dysfunction.
    Do NOT use philosophical terms, fluff, or words like 'superpower'. Maintain a highly professional, medical, and minimalist tone.
    
    Respond ONLY in valid JSON format with exactly these two keys:
    {
        "primary_marker": "A short, clinical label (e.g., 'Elevated Cognitive Load', 'Hyperactive Speech Pattern', 'Baseline / Neurotypical')",
        "clinical_notes": "1-2 brief, objective sentences explaining the observation based strictly on the speech input."
    }"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcription to analyze: {transcription_text}"}
            ],
            temperature=0.2, # Keep it low for analytical consistency
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        return json.loads(response_content)
        
    except Exception as e:
        print(f"❌ [rag_svc.py] Groq Analysis Error: {str(e)}")
        return {
            "primary_marker": "Analysis Incomplete",
            "clinical_notes": "Insufficient data to form a clinical baseline."
        }