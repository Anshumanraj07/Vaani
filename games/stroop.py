import json

def render_stroop_test(api_url):
    escaped_url = api_url
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');
            body {{ font-family: 'Nunito', sans-serif; text-align: center; margin:0; padding:0; background: transparent; }}
            #game-container {{ background: #1e1e1e; padding: 20px; border-radius: 20px; border: 3px solid #1cb0f6; height: 390px; position:relative; box-sizing: border-box; }}
            #word-display {{ font-size: 52px; font-weight: 900; margin: 35px 0; text-transform: uppercase; letter-spacing: 2px; }}
            .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 320px; margin: 0 auto; }}
            .color-btn {{ padding: 14px; font-size: 16px; font-weight: 900; cursor: pointer; border: none; border-radius: 16px; color: white; border-bottom: 4px solid rgba(0,0,0,0.4); transition: transform 0.1s; text-transform: uppercase; -webkit-tap-highlight-color: transparent; }}
            .color-btn:active {{ transform: translateY(4px); border-bottom: none; }}
            #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 15px 30px; font-size: 18px; font-weight: 900; cursor: pointer; border-radius: 16px; background: #1cb0f6; border: none; border-bottom: 5px solid #189fd9; color: white; text-transform: uppercase; }}
            #start-btn:active {{ border-bottom: none; transform: translate(-50%, -45%); }}
            #round-badge {{ position: absolute; top: 15px; left: 15px; background: #1cb0f6; color: white; padding: 5px 15px; border-radius: 12px; font-weight: 900; font-size: 14px; }}
            
            /* Duolingo Style Mascot Pop-up Animation */
            .mascot-popup {{ display: none; animation: popUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; background: #252525; border: 3px solid #58cc02; border-radius: 20px; padding: 20px; margin-top: 15px; color: white; }}
            .mascot-avatar {{ font-size: 60px; animation: bounce 0.6s infinite alternate; margin-bottom: 10px; }}
            @keyframes popUp {{ 0% {{ transform: scale(0.5); opacity: 0; }} 100% {{ transform: scale(1); opacity: 1; }} }}
            @keyframes bounce {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(-10px); }} }}
            
            #result-text {{ color: #aaa; font-weight: bold; margin-top: 10px; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div id="game-container">
            <div id="round-badge">Round: <span id="round-count">0</span>/12</div>
            <button id="start-btn">Start Ink Game</button>
            <div id="game-ui" style="display:none;">
                <div id="word-display" style="color: #ffffff;">READY</div>
                <div class="btn-grid">
                    <button class="color-btn" style="background:#ff4b4b;" onclick="checkAnswer('red')">RED</button>
                    <button class="color-btn" style="background:#1cb0f6;" onclick="checkAnswer('blue')">BLUE</button>
                    <button class="color-btn" style="background:#58cc02;" onclick="checkAnswer('green')">GREEN</button>
                    <button class="color-btn" style="background:#ffc800; color:#333;" onclick="checkAnswer('yellow')">YELLOW</button>
                </div>
            </div>
        </div>
        <div id="result-text">Match the INK color, ignore the text!</div>
        
        <div id="mascot-widget" class="mascot-popup">
            <div class="mascot-avatar">Duo 🦉⚡</div>
            <div id="badge-msg" style="font-size: 18px; font-weight: 900; color: #58cc02;"></div>
            <div id="metrics-summary" style="margin-top: 10px; font-size: 14px; color: #eee;"></div>
        </div>

        <script>
            const colors = ['red', 'blue', 'green', 'yellow'];
            const hexColors = {{'red': '#ff4b4b', 'blue': '#1cb0f6', 'green': '#58cc02', 'yellow': '#ffc800'}};
            let currentRound = 0; 
            let maxRounds = 12; // Increased to 12 intervals
            let startTime = 0; let totalRT = 0; let errors = 0;
            let currentColor = "";

            document.getElementById('start-btn').onclick = () => {{
                document.getElementById('start-btn').style.display = 'none';
                document.getElementById('mascot-widget').style.display = 'none';
                document.getElementById('game-ui').style.display = 'block';
                currentRound = 0; totalRT = 0; errors = 0;
                document.getElementById('round-count').innerText = "0";
                document.getElementById('result-text').innerText = "Focus on the INK color!";
                nextRound();
            }};

            function nextRound() {{
                if (currentRound >= maxRounds) {{ finishGame(); return; }}
                document.getElementById('round-count').innerText = currentRound + 1;
                
                let textIndex = Math.floor(Math.random() * colors.length);
                let colorIndex = Math.floor(Math.random() * colors.length);
                
                // 70% chance to force incongruent pair (Confusing mode)
                if (Math.random() > 0.3) {{ 
                    while(colorIndex === textIndex) colorIndex = Math.floor(Math.random() * colors.length);
                }}
                
                currentColor = colors[colorIndex];
                let display = document.getElementById('word-display');
                display.innerText = colors[textIndex];
                display.style.color = hexColors[currentColor];
                
                startTime = Date.now();
            }}

            function checkAnswer(selectedColor) {{
                let rt = Date.now() - startTime;
                totalRT += rt;
                if (selectedColor !== currentColor) errors++;
                
                currentRound++;
                nextRound();
            }}

            async function finishGame() {{
                document.getElementById('game-ui').style.display = 'none';
                document.getElementById('result-text').innerText = "Analyzing impulses...";
                
                let avgRT = Math.round(totalRT / maxRounds);
                let payload = {{
                    "task_type": "stroop_test",
                    "age_group": "19-25",
                    "action_initiation_time_ms": avgRT,
                    "total_response_time_ms": totalRT,
                    "cursor_reversals": errors,
                    "is_correct": (errors === 0)
                }};

                try {{
                    let res = await fetch("{escaped_url}/api/v1/analyze-interaction", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify(payload)
                    }});
                    let data = await res.json();
                    
                    document.getElementById('result-text').innerText = "Analysis Complete!";
                    document.getElementById('badge-msg').innerText = data.analysis.detected_pattern;
                    document.getElementById('metrics-summary').innerHTML = `Focus Delay: <b>${{avgRT}}ms</b> | Slip-ups: <b>${{errors}}/12</b>`;
                    document.getElementById('mascot-widget').style.display = 'block';
                    
                    setTimeout(() => {{ 
                        document.getElementById('start-btn').style.display = 'block'; 
                        document.getElementById('start-btn').innerText = "Play Again"; 
                    }}, 2000);
                }} catch(err) {{
                    document.getElementById('result-text').innerHTML = `<span style="color: red;">API Error.</span>`;
                    document.getElementById('start-btn').style.display = 'block';
                }}
            }}
        </script>
    </body>
    </html>
    """