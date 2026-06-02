import os
import streamlit as st
import requests
import time
import random

# Default to localhost for local dev, but allow cloud URL via environment variable
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Page setup
st.set_page_config(page_title="Project Vaani", page_icon="🧠", layout="centered")

st.title("🧠 Project Vaani: Multi-Modal AI")
st.markdown("### Discover your hidden superpowers through Voice & Action!")
st.divider()

# Create Tabs for different features
tab1, tab2, tab3 = st.tabs(["🎙️ Voice Analysis", "🖱️ Interactive Puzzle (New!)", "📊 Clinical Dashboard"])

# --- TAB 1: VOICE AI ---
with tab1:
    st.write("Bina kisi dar ke bolo! Hum tumhari aawaz mein chhipi tumhari taaqat dhoondhenge.")
    audio_value = st.audio_input("Record your voice here...")

    if audio_value is not None:
        st.success("Audio recorded successfully!")
        
        if st.button("🧠 Analyze My Voice", type="primary", use_container_width=True):
            with st.spinner("Analyzing your voice... finding superpowers..."):
                files = {"file": ("recording.wav", audio_value, "audio/wav")}
                try:
                    response = requests.post(f"{API_URL}/api/v1/analyze-audio", files=files, timeout=120)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.subheader("📝 What Vaani Heard:")
                        st.write(f"*{data['transcription']['text']}*")
                        st.subheader("🦸‍♂️ Your Superpower:")
                        st.success(data['cognitive_analysis']['superpower'])
                        with st.expander("📊 Clinical Admin Report"):
                            st.info(data['cognitive_analysis']['admin_report'])
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection Failed: {e}")

# --- TAB 2: INTERACTIVE PUZZLE (PHASE 1.2) ---
with tab2:
    st.write("Let's track your REAL mouse kinematics. Click Start, wait for the red target, and click it as fast as you can!")
    import streamlit.components.v1 as components
    
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            #game-area {{ width: 100%; height: 350px; background: #1e1e1e; position: relative; border-radius: 10px; overflow: hidden; border: 2px solid #4CAF50;}}
            #target {{ width: 40px; height: 40px; background: #ff4b4b; position: absolute; border-radius: 50%; display: none; cursor: pointer; box-shadow: 0 0 10px #ff4b4b;}}
            #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 12px 24px; font-size: 16px; font-weight: bold; cursor: pointer; border-radius: 5px; background: #4CAF50; border: none; color: white;}}
            #result {{ font-family: sans-serif; margin-top: 15px; padding: 10px; background: #f0f2f6; border-radius: 5px; color: #333;}}
        </style>
    </head>
    <body>
        <div id="game-area">
            <button id="start-btn">Start Real Tracker Game</button>
            <div id="target"></div>
        </div>
        <div id="result">Waiting for interaction data...</div>

        <script>
            let target = document.getElementById('target');
            let startBtn = document.getElementById('start-btn');
            let gameArea = document.getElementById('game-area');
            let resultDiv = document.getElementById('result');

            let targetAppearTime = 0;
            let mousePath = [];
            let tracking = false;

            startBtn.onclick = () => {{
                startBtn.style.display = 'none';
                resultDiv.innerHTML = "Wait for the red target to appear...";
                setTimeout(() => {{
                    let maxX = gameArea.clientWidth - 50;
                    let maxY = gameArea.clientHeight - 50;
                    target.style.left = (Math.random() * maxX) + 'px';
                    target.style.top = (Math.random() * maxY) + 'px';
                    target.style.display = 'block';
                    targetAppearTime = Date.now();
                    tracking = true;
                    mousePath = [];
                }}, 1000 + Math.random() * 2000);
            }};

            gameArea.onmousemove = (e) => {{
                if (tracking) {{
                    mousePath.push({{x: e.clientX, y: e.clientY, time: Date.now()}});
                }}
            }};

            target.onclick = async () => {{
                tracking = false;
                target.style.display = 'none';
                let clickTime = Date.now();
                let totalRT = clickTime - targetAppearTime;

                // Kinematics: Action Initiation Time (AIT)
                let ait = totalRT;
                if (mousePath.length > 0) {{
                    ait = mousePath[0].time - targetAppearTime;
                }}

                // Kinematics: Cursor Reversals (Direction hesitations)
                let reversals = 0;
                let lastDirection = 0;
                for (let i = 1; i < mousePath.length; i++) {{
                    let dx = mousePath[i].x - mousePath[i-1].x;
                    if (dx !== 0) {{
                        let dir = dx > 0 ? 1 : -1;
                        if (lastDirection !== 0 && dir !== lastDirection) {{
                            reversals++;
                        }}
                        lastDirection = dir;
                    }}
                }}

                resultDiv.innerHTML = `Analyzing ${{mousePath.length}} coordinate points...`;

                let payload = {{
                    "task_type": "spatial_rotation", 
                    "age_group": "19-25",
                    "action_initiation_time_ms": ait,
                    "total_response_time_ms": totalRT,
                    "cursor_reversals": reversals,
                    "is_correct": true
                }};

                try {{
                    let res = await fetch("{API_URL}/api/v1/analyze-interaction", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify(payload)
                    }});
                    let data = await res.json();
                    resultDiv.innerHTML = `
                        <b>Reaction Time:</b> ${{totalRT}}ms | <b>Cursor Reversals:</b> ${{reversals}}<br>
                        <hr style="margin:5px 0;">
                        <span style="color: #2e7d32; font-size: 16px;"><b>Pattern Detected:</b> ${{data.analysis.detected_pattern}}</span><br>
                        <b>Superpower:</b> ${{data.analysis.superpower}}
                    `;
                    setTimeout(() => {{ startBtn.style.display = 'block'; }}, 3000);
                }} catch(err) {{
                    resultDiv.innerHTML = `<span style="color: red;">Error connecting to API. Is CORS middleware added in main.py?</span>`;
                    setTimeout(() => {{ startBtn.style.display = 'block'; }}, 2000);
                }}
            }};
        </script>
    </body>
    </html>
    """, height=450)

# --- TAB 3: CLINICAL DASHBOARD ---
with tab3:
    st.subheader("📊 Clinical Admin Dashboard")
    st.write("Overview of patient telemetry and historical data.")
    
    if st.button("🔄 Refresh Data", type="secondary"):
        try:
            res = requests.get(f"{API_URL}/api/v1/history")
            if res.status_code == 200:
                history_data = res.json()["data"]
                if history_data:
                    import pandas as pd
                    df = pd.DataFrame(history_data)
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    col1.metric("Total Sessions", len(df))
                    col2.metric("Avg Reaction Time", f"{int(df['reaction_time_ms'].mean())} ms")
                    
                    st.divider()
                    st.write("**Reaction Time Trend (ms)**")
                    st.line_chart(df['reaction_time_ms'])
                    
                    st.write("**Session History Log**")
                    st.dataframe(df[['timestamp', 'task_type', 'detected_pattern', 'reaction_time_ms']], use_container_width=True)
                else:
                    st.info("No session data found yet. Play the interactive puzzle first!")
        except Exception as e:
            st.error(f"Could not fetch history: {e}")
