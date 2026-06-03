import os
import json
from groq import Groq

def analyze_telemetry(telemetry_data: dict):
    """
    Analyzes game telemetry for cognitive patterns (impulse control, motor latency).
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=groq_api_key)

    system_prompt = """You are a Clinical Diagnostics AI evaluating cognitive telemetry data.
    The data includes reaction times (ms) and error rates (cursor_reversals) for specific kinematic/impulse-control tasks.
    Correlate this data to clinical markers like ADHD (high errors, high impulsivity), PTSD (hesitation, high latency), or Neurotypical baseline.
    Keep the tone strictly clinical, minimalist, and objective. 
    
    Respond ONLY in valid JSON format with exactly these two keys:
    {
        "detected_pattern": "Short clinical label (e.g., 'Impulse Control Deficit', 'Normative Motor Latency', 'Attentional Drift')",
        "superpower": "1-2 brief clinical notes explaining the observation. (Note: use 'superpower' as the JSON key for legacy compatibility, but output clinical text here)."
    }"""

    user_prompt = f"""
    Task Type: {telemetry_data.get('task_type')}
    Avg Action Initiation (ms): {telemetry_data.get('action_initiation_time_ms')}
    Total Response Time (ms): {telemetry_data.get('total_response_time_ms')}
    Inaccuracies/Reversals: {telemetry_data.get('cursor_reversals')}
    Task Completed Correctly: {telemetry_data.get('is_correct')}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        result = json.loads(response_content)
        
        # Fallbacks in case AI misses the exact keys
        if "detected_pattern" not in result:
            result["detected_pattern"] = "Baseline Validated"
        if "superpower" not in result:
            result["superpower"] = result.get("clinical_notes", "Telemetry logged within standard deviations.")
            
        return result

    except Exception as e:
        print(f"❌ [interaction_svc.py] Groq Analysis Error: {str(e)}")
        return {
            "detected_pattern": "Diagnostic Error",
            "superpower": "System failed to analyze telemetry."
        }