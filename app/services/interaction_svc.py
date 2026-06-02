def analyze_telemetry(data: dict) -> dict:
    print(f"🔵 [interaction_svc.py] Analyzing telemetry for task: {data['task_type']}")
    
    # Rule-based logic based on clinical telemetry research
    if data["task_type"] == "go_no_go" and data["total_response_time_ms"] < 300 and not data["is_correct"]:
        condition = "ADHD Trait (High Impulsivity / Motor Disinhibition)"
        superpower = "Dynamic Reasoning (Rapid Crisis Decision-Making) - Your reaction speed is off the charts! You think and act faster than the game can keep up, exactly like an elite emergency responder."
    elif data["task_type"] == "spatial_rotation" and data["cursor_reversals"] > 3:
        condition = "Dyslexia Trait (Directional Hesitation / Mental Rotation)"
        superpower = "Material Reasoning (3D Spatial Thinking) - You are analyzing every angle of this shape like a Master Architect! Your brain builds real 3D models instead of just looking at flat images."
    else:
        condition = "Baseline/Neurotypical Pattern"
        superpower = "Balanced Processor - You have a highly steady and calculated approach to problem-solving!"
        
    print("✅ [interaction_svc.py] Telemetry analysis complete!")
    return {
        "detected_pattern": condition,
        "superpower": superpower,
        "admin_report": f"User completed the {data['task_type']} task in {data['total_response_time_ms']}ms with an Action Initiation Time of {data['action_initiation_time_ms']}ms. Cursor reversals: {data['cursor_reversals']}. Accuracy: {data['is_correct']}."
    }