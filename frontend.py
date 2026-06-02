import os
import streamlit as st
import requests
import json
import streamlit.components.v1 as components

# Import modular games from the games directory
from games.tracker import render_target_tracker
from games.stroop import render_stroop_test

# Default to localhost for local dev, but allow cloud URL via environment variable
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Page setup
st.set_page_config(page_title="Project Vaani", page_icon="🧠", layout="centered")

# --- DUOLINGO STYLE CSS INJECTION ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { font-family: 'Nunito', 'Segoe UI', sans-serif; }
        .stButton>button {
            background-color: #58cc02; color: white !important; font-size: 18px !important;
            font-weight: bold; border-radius: 16px; border: none;
            border-bottom: 5px solid #58a700; padding: 12px 24px;
            transition: all 0.1s ease; width: 100%;
        }
        .stButton>button:active { border-bottom: 0px; transform: translateY(5px); }
        .stAudio { border-radius: 15px; border: 2px solid #58cc02; padding: 10px; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 10px; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 15px; background-color: transparent; border: 2px solid #888888;
            padding: 10px 20px; font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(28, 176, 246, 0.1); color: #1cb0f6; border: 2px solid #1cb0f6;
            border-bottom: 5px solid #1cb0f6;
        }
        .stAlert { border-radius: 15px; border: 2px solid transparent; }
        div[role="radiogroup"] { padding: 10px; border-radius: 15px; border: 2px solid #888888; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Project Vaani")
st.markdown("### 🏆 Discover your hidden superpowers!")
st.divider()

# Create Tabs for different features
tab1, tab2, tab3 = st.tabs(["🎙️ Voice Analysis", "🎮 Cognitive Games", "📊 Clinical Dashboard"])

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
                        superpower_text = data['cognitive_analysis']['superpower']
                        st.success(superpower_text)
                        with st.expander("📊 Clinical Admin Report"):
                            st.info(data['cognitive_analysis']['admin_report'])
                        
                        # Text-to-Speech
                        escaped_superpower = json.dumps(superpower_text)
                        components.html(f"""
                        <div style="text-align: center; margin-top: 10px;">
                            <button id="tts-btn" style="padding: 8px 16px; font-size: 14px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 5px; font-weight:bold;">
                                🔊 Hear Your Superpower
                            </button>
                        </div>
                        <script>
                            document.getElementById('tts-btn').addEventListener('click', function() {{
                                let utterance = new SpeechSynthesisUtterance({escaped_superpower});
                                window.speechSynthesis.speak(utterance);
                                this.style.background = '#45a049';
                                setTimeout(() => {{ this.style.background = '#4CAF50'; }}, 200);
                            }});
                        </script>
                        """, height=50)
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection Failed: {e}")

# --- TAB 2: COGNITIVE GAMES (MODULAR) ---
with tab2:
    game_choice = st.radio("Select a Puzzle:", ["🖱️ Target Tracker (Spatial)", "🎨 Stroop Test (Impulse Control)"], horizontal=True)
    
    if "Target Tracker" in game_choice:
        st.write("**Goal:** Track your focus speed. Hit the red dot **20 times** as fast as you can!")
        # Inject from games/tracker.py
        html_code = render_target_tracker(API_URL)
        components.html(html_code, height=520)

    else:
        st.write("**Goal:** Tap the button matching the **INK COLOR**, ignore the text! (**12 Rounds**)")
        # Inject from games/stroop.py
        html_code = render_stroop_test(API_URL)
        components.html(html_code, height=520)

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