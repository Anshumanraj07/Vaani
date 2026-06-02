import os
import streamlit as st
import requests
import json
import streamlit.components.v1 as components

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
        .stApp { background-color: #ffffff; font-family: 'Nunito', 'Segoe UI', sans-serif; }
        .stButton>button {
            background-color: #58cc02; color: white; font-size: 18px !important;
            font-weight: bold; border-radius: 16px; border: none;
            border-bottom: 5px solid #58a700; padding: 12px 24px;
            transition: all 0.1s ease; width: 100%;
        }
        .stButton>button:active { border-bottom: 0px; transform: translateY(5px); }
        .stAudio { border-radius: 15px; border: 2px solid #e5e5e5; padding: 10px; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 10px; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 15px; background-color: #f7f7f7; border: 2px solid #e5e5e5;
            padding: 10px 20px; font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ddf4ff; color: #1cb0f6; border: 2px solid #1cb0f6;
            border-bottom: 5px solid #1cb0f6;
        }
        .stAlert { border-radius: 15px; border: 2px solid transparent; }
        /* Make radio buttons look better */
        div[role="radiogroup"] { padding: 10px; background: #f0f2f6; border-radius: 15px; border: 2px solid #e5e5e5; }
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

# --- TAB 2: COGNITIVE GAMES ---
with tab2:
    game_choice = st.radio("Select a Puzzle:", ["🖱️ Target Tracker (Spatial)", "🎨 Stroop Test (Impulse Control)"], horizontal=True)
    
    if "Target Tracker" in game_choice:
        st.write("**Goal:** Track your REAL mouse kinematics. Click the red target as fast as you can!")
        components.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                #game-area {{ width: 100%; height: 350px; background: #1e1e1e; position: relative; border-radius: 10px; overflow: hidden; border: 2px solid #4CAF50;}}
                #target {{ width: 40px; height: 40px; background: #ff4b4b; position: absolute; border-radius: 50%; display: none; cursor: pointer; box-shadow: 0 0 10px #ff4b4b;}}
                #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 12px 24px; font-size: 16px; font-weight: bold; cursor: pointer; border-radius: 15px; background: #58cc02; border: none; border-bottom: 4px solid #58a700; color: white;}}
                #result {{ font-family: sans-serif; margin-top: 15px; padding: 10px; background: #f0f2f6; border-radius: 10px; color: #333; font-weight: bold; text-align: center;}}
            </style>
        </head>
        <body>
            <div id="game-area">
                <button id="start-btn">Start Tracker Game</button>
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
                    if (tracking) {{ mousePath.push({{x: e.clientX, y: e.clientY, time: Date.now()}}); }}
                }};

                target.onclick = async () => {{
                    tracking = false;
                    target.style.display = 'none';
                    let clickTime = Date.now();
                    let totalRT = clickTime - targetAppearTime;

                    let ait = totalRT;
                    if (mousePath.length > 0) {{ ait = mousePath[0].time - targetAppearTime; }}

                    let reversals = 0; let lastDir = 0;
                    for (let i = 1; i < mousePath.length; i++) {{
                        let dx = mousePath[i].x - mousePath[i-1].x;
                        if (dx !== 0) {{
                            let dir = dx > 0 ? 1 : -1;
                            if (lastDir !== 0 && dir !== lastDir) reversals++;
                            lastDir = dir;
                        }}
                    }}

                    resultDiv.innerHTML = `Analyzing data...`;
                    let payload = {{
                        "task_type": "spatial_rotation", "age_group": "19-25",
                        "action_initiation_time_ms": ait, "total_response_time_ms": totalRT,
                        "cursor_reversals": reversals, "is_correct": true
                    }};

                    try {{
                        let res = await fetch("{API_URL}/api/v1/analyze-interaction", {{
                            method: "POST", headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify(payload)
                        }});
                        let data = await res.json();
                        resultDiv.innerHTML = `Reaction Time: ${{totalRT}}ms | Reversals: ${{reversals}}<br><hr style="margin:5px 0;border-top:2px solid #ccc;">
                        <span style="color:#2e7d32;">Pattern: ${{data.analysis.detected_pattern}}</span><br>🦸‍♂️ <b>${{data.analysis.superpower}}</b>`;
                        setTimeout(() => {{ startBtn.style.display = 'block'; }}, 3000);
                    }} catch(err) {{
                        resultDiv.innerHTML = `<span style="color: red;">Error connecting to API.</span>`;
                        setTimeout(() => {{ startBtn.style.display = 'block'; }}, 2000);
                    }}
                }};
            </script>
        </body>
        </html>
        """, height=480)

    else:
        st.write("**Goal:** Click the button that matches the **INK COLOR**, ignoring what the word says!")
        components.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Nunito', sans-serif; text-align: center; margin:0; padding:0;}}
                #game-container {{ background: #f7f7f7; padding: 20px; border-radius: 15px; border: 2px solid #e5e5e5; height: 380px; position:relative;}}
                #word-display {{ font-size: 50px; font-weight: 900; margin: 40px 0; text-transform: uppercase; letter-spacing: 2px;}}
                .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 300px; margin: 0 auto;}}
                .color-btn {{ padding: 15px; font-size: 16px; font-weight: bold; cursor: pointer; border: none; border-radius: 12px; color: white; border-bottom: 4px solid rgba(0,0,0,0.2); transition: transform 0.1s;}}
                .color-btn:active {{ transform: translateY(4px); border-bottom: none;}}
                #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 15px 30px; font-size: 18px; font-weight: bold; cursor: pointer; border-radius: 15px; background: #58cc02; border: none; border-bottom: 4px solid #58a700; color: white;}}
                #result {{ margin-top: 15px; font-weight: bold; color: #333; padding:10px; background:#e0f7fa; border-radius: 10px;}}
            </style>
        </head>
        <body>
            <div id="game-container">
                <button id="start-btn">Start Stroop Test</button>
                <div id="game-ui" style="display:none;">
                    <div id="word-display">READY</div>
                    <div class="btn-grid">
                        <button class="color-btn" style="background:#ff4b4b;" onclick="checkAnswer('red')">RED</button>
                        <button class="color-btn" style="background:#1cb0f6;" onclick="checkAnswer('blue')">BLUE</button>
                        <button class="color-btn" style="background:#58cc02;" onclick="checkAnswer('green')">GREEN</button>
                        <button class="color-btn" style="background:#ffc800; color:#333;" onclick="checkAnswer('yellow')">YELLOW</button>
                    </div>
                </div>
            </div>
            <div id="result">Click Start to begin (5 Rounds)</div>

            <script>
                const colors = ['red', 'blue', 'green', 'yellow'];
                const hexColors = {{'red': '#ff4b4b', 'blue': '#1cb0f6', 'green': '#58cc02', 'yellow': '#ffc800'}};
                let currentRound = 0; let maxRounds = 5;
                let startTime = 0; let totalRT = 0; let errors = 0;
                let currentColor = "";

                document.getElementById('start-btn').onclick = () => {{
                    document.getElementById('start-btn').style.display = 'none';
                    document.getElementById('game-ui').style.display = 'block';
                    currentRound = 0; totalRT = 0; errors = 0;
                    document.getElementById('result').innerText = "Focus on the INK color!";
                    nextRound();
                }};

                function nextRound() {{
                    if (currentRound >= maxRounds) {{ finishGame(); return; }}
                    
                    // Logic to create confusing (incongruent) word/color pairs
                    let textIndex = Math.floor(Math.random() * colors.length);
                    let colorIndex = Math.floor(Math.random() * colors.length);
                    if (Math.random() > 0.3) {{ // 70% chance to be different (hard mode)
                        while(colorIndex === textIndex) colorIndex = Math.floor(Math.random() * colors.length);
                    }}
                    
                    let wordText = colors[textIndex];
                    currentColor = colors[colorIndex];
                    
                    let display = document.getElementById('word-display');
                    display.innerText = wordText;
                    display.style.color = hexColors[currentColor];
                    
                    startTime = Date.now();
                }}

                async function checkAnswer(selectedColor) {{
                    let rt = Date.now() - startTime;
                    totalRT += rt;
                    if (selectedColor !== currentColor) errors++;
                    
                    currentRound++;
                    nextRound();
                }}

                async function finishGame() {{
                    document.getElementById('game-ui').style.display = 'none';
                    document.getElementById('result').innerHTML = `Analyzing results...`;
                    
                    let avgRT = Math.round(totalRT / maxRounds);
                    
                    // We map errors to cursor_reversals so the backend schema accepts it
                    let payload = {{
                        "task_type": "stroop_test", "age_group": "19-25",
                        "action_initiation_time_ms": avgRT, "total_response_time_ms": totalRT,
                        "cursor_reversals": errors, "is_correct": (errors === 0)
                    }};

                    try {{
                        let res = await fetch("{API_URL}/api/v1/analyze-interaction", {{
                            method: "POST", headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify(payload)
                        }});
                        let data = await res.json();
                        document.getElementById('result').innerHTML = `
                            Avg Reaction: ${{avgRT}}ms | Mistakes: ${{errors}}/5<br><hr style="margin:5px 0;">
                            <span style="color:#1cb0f6;">Pattern: ${{data.analysis.detected_pattern}}</span><br>
                            🦸‍♂️ <b>${{data.analysis.superpower}}</b>
                        `;
                        setTimeout(() => {{ document.getElementById('start-btn').style.display = 'block'; document.getElementById('start-btn').innerText = "Play Again"; }}, 3000);
                    }} catch(err) {{
                        document.getElementById('result').innerHTML = `<span style="color: red;">API Error.</span>`;
                        setTimeout(() => {{ document.getElementById('start-btn').style.display = 'block'; }}, 2000);
                    }}
                }}
            </script>
        </body>
        </html>
        """, height=500)

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