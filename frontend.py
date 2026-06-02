import os
import streamlit as st
import requests
import json
import streamlit.components.v1 as components

from games.tracker import render_target_tracker
from games.stroop import render_stroop_test

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Vaani", page_icon="⚡", layout="centered")

# --- MINIMALIST PREMIUM CSS INJECTION ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Global Minimalist Theme */
        .stApp { font-family: 'Inter', sans-serif; background-color: #fafafa; color: #111111; }
        
        /* Typography adjustments */
        h1, h2, h3 { font-weight: 600 !important; letter-spacing: -0.5px; color: #111; }
        
        /* Sleek Flat Buttons */
        .stButton>button {
            background-color: #111111; color: #ffffff !important; 
            font-size: 15px !important; font-weight: 500; letter-spacing: 0.3px;
            border-radius: 6px; border: 1px solid #111111;
            padding: 10px 24px; transition: all 0.2s ease; width: 100%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .stButton>button:hover { background-color: #333333; border-color: #333333; transform: translateY(-1px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
        .stButton>button:active { transform: translateY(0px); }
        
        /* Minimal Audio Input */
        .stAudio { border-radius: 8px; border: 1px solid #eaeaea; padding: 8px; background: #ffffff; }
        
        /* Elegant Floating Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 1px solid #eaeaea; padding-bottom: 0px; }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent; border: none;
            padding: 10px 5px; font-weight: 500; color: #888888; font-size: 15px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent; color: #111111; 
            border-bottom: 2px solid #111111;
        }
        
        /* Clean Alerts and Expanders */
        .stAlert { border-radius: 8px; border: 1px solid #eaeaea; background-color: #ffffff; color: #333; }
        div[data-testid="stExpander"] { border: 1px solid #eaeaea; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
        div[role="radiogroup"] { padding: 15px; border-radius: 8px; border: 1px solid #eaeaea; background: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("Vaani")
st.markdown("### Cognitive Telemetry Platform")
st.divider()

tab1, tab2, tab3 = st.tabs(["Voice Analysis", "Kinematics", "Telemetry"])

# --- TAB 1: VOICE AI ---
with tab1:
    st.write("Speak naturally. The system will analyze your vocal and cognitive markers.")
    audio_value = st.audio_input("Record audio baseline")

    if audio_value is not None:
        if st.button("Process Audio", type="primary", use_container_width=True):
            with st.spinner("Analyzing neural patterns..."):
                files = {"file": ("recording.wav", audio_value, "audio/wav")}
                try:
                    response = requests.post(f"{API_URL}/api/v1/analyze-audio", files=files, timeout=120)
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown(f"**Transcription:** *{data['transcription']['text']}*")
                        
                        superpower_text = data['cognitive_analysis']['superpower']
                        st.success(f"**Insight:** {superpower_text}")
                        
                        with st.expander("View Clinical Output"):
                            st.write(data['cognitive_analysis']['admin_report'])
                        
                        escaped_superpower = json.dumps(superpower_text)
                        components.html(f"""
                        <div style="text-align: left; margin-top: 10px;">
                            <button id="tts-btn" style="padding: 10px 20px; font-size: 13px; font-family: 'Inter', sans-serif; cursor: pointer; background: #ffffff; color: #111; border: 1px solid #eaeaea; border-radius: 6px; font-weight:500; transition: 0.2s;">
                                ▶ Play Synthesis
                            </button>
                        </div>
                        <script>
                            let btn = document.getElementById('tts-btn');
                            btn.addEventListener('click', function() {{
                                let utterance = new SpeechSynthesisUtterance({escaped_superpower});
                                window.speechSynthesis.speak(utterance);
                                this.style.background = '#f5f5f5';
                                setTimeout(() => {{ this.style.background = '#ffffff'; }}, 300);
                            }});
                        </script>
                        """, height=50)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

# --- TAB 2: COGNITIVE GAMES ---
with tab2:
    game_choice = st.radio("Select Diagnostic:", ["Spatial Tracker", "Impulse Control (Stroop)"], horizontal=True)
    
    if "Spatial Tracker" in game_choice:
        st.write("Track the target. Minimal latency required (20 iterations).")
        components.html(render_target_tracker(API_URL), height=520)
    else:
        st.write("Select the INK color. Inhibit the lexical response (12 iterations).")
        components.html(render_stroop_test(API_URL), height=520)

# --- TAB 3: CLINICAL DASHBOARD ---
with tab3:
    st.subheader("Session Telemetry")
    if st.button("Sync Data", type="secondary"):
        try:
            res = requests.get(f"{API_URL}/api/v1/history")
            if res.status_code == 200:
                history_data = res.json()["data"]
                if history_data:
                    import pandas as pd
                    df = pd.DataFrame(history_data)
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    col1.metric("Logged Sessions", len(df))
                    avg_rt = int(df['reaction_time_ms'].mean())
                    col2.metric("Mean Response (ms)", avg_rt)
                    
                    st.divider()
                    st.write("**Latency Trajectory**")
                    st.line_chart(df['reaction_time_ms'])
                    
                    latest_pattern = df.iloc[-1]['detected_pattern'] if 'detected_pattern' in df.columns else "Pending"
                    
                    st.markdown("### 📋 Executive Summary")
                    st.info(f"Analysis of **{len(df)}** sessions indicates a mean response latency of **{avg_rt}ms**. The latest kinematic diagnostic highlights a pattern consistent with **'{latest_pattern}'**, providing a baseline for executive function and motor-cognitive coordination.")
                else:
                    st.info("Insufficient telemetry. Execute a diagnostic module first.")
        except Exception as e:
            st.error(f"Sync failed: {e}")