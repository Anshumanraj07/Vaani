def render_stroop_test(api_url):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
            body {{ font-family: 'Inter', sans-serif; text-align: center; margin:0; padding:0; background: transparent; color: #111; }}
            
            #game-container {{ background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #eaeaea; height: 390px; position:relative; box-sizing: border-box; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }}
            
            #word-display {{ font-size: 42px; font-weight: 600; margin: 45px 0; text-transform: uppercase; letter-spacing: 4px; }}
            
            .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 320px; margin: 0 auto; }}
            
            .color-btn {{ padding: 14px; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid #eaeaea; border-radius: 6px; background: #fafafa; color: #111; transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; -webkit-tap-highlight-color: transparent; }}
            .color-btn:hover {{ background: #f0f0f0; }}
            .color-btn:active {{ transform: scale(0.98); }}
            
            #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 12px 28px; font-size: 15px; font-weight: 500; cursor: pointer; border-radius: 6px; background: #111111; border: none; color: white; letter-spacing: 0.5px; transition: 0.2s; }}
            #start-btn:hover {{ background: #333333; }}
            
            #round-badge {{ position: absolute; top: 15px; left: 15px; background: transparent; color: #666; font-weight: 500; font-size: 13px; letter-spacing: 0.5px; }}
            
            /* Minimalist Summary Pop-up */
            .mascot-popup {{ display: none; animation: fadeUp 0.4s ease forwards; background: #ffffff; border: 1px solid #eaeaea; border-radius: 8px; padding: 25px; margin-top: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: left; }}
            @keyframes fadeUp {{ 0% {{ transform: translateY(10px); opacity: 0; }} 100% {{ transform: translateY(0); opacity: 1; }} }}
            
            #result-text {{ color: #666; font-weight: 400; margin-top: 12px; font-size: 14px; letter-spacing: 0.3px; }}
        </style>
    </head>
    <body>
        <div id="game-container">
            <div id="round-badge">ITERATION: <span id="round-count">0</span>/12</div>
            <button id="start-btn">Initiate Sequence</button>
            <div id="game-ui" style="display:none;">
                <div id="word-display" style="color: #111;">READY</div>
                <div class="btn-grid">
                    <button class="color-btn" onclick="checkAnswer('red')">RED</button>
                    <button class="color-btn" onclick="checkAnswer('blue')">BLUE</button>
                    <button class="color-btn" onclick="checkAnswer('green')">GREEN</button>
                    <button class="color-btn" onclick="checkAnswer('yellow')">YELLOW</button>
                </div>
            </div>
        </div>
        <div id="result-text">Inhibit text reading. Match ink color only.</div>
        
        <div id="mascot-widget" class="mascot-popup">
            <div style="font-size: 12px; font-weight: 600; color: #888; letter-spacing: 1px; margin-bottom: 8px;">DIAGNOSTIC COMPLETE</div>
            <div id="badge-msg" style="font-size: 18px; font-weight: 600; color: #111;"></div>
            <div id="metrics-summary" style="margin-top: 8px; font-size: 14px; color: #555; line-height: 1.5;"></div>
        </div>

        <script>
            const colors = ['red', 'blue', 'green', 'yellow'];
            const hexColors = {{'red': '#ff4b4b', 'blue': '#1cb0f6', 'green': '#58cc02', 'yellow': '#ffc800'}};
            let currentRound = 0; let maxRounds = 12; 
            let startTime = 0; let totalRT = 0; let errors = 0; let currentColor = "";

            document.getElementById('start-btn').onclick = () => {{
                document.getElementById('start-btn').style.display = 'none'; document.getElementById('mascot-widget').style.display = 'none'; document.getElementById('game-ui').style.display = 'block';
                currentRound = 0; totalRT = 0; errors = 0; document.getElementById('round-count').innerText = "0";
                document.getElementById('result-text').innerText = "Test active...";
                nextRound();
            }};

            function nextRound() {{
                if (currentRound >= maxRounds) {{ finishGame(); return; }}
                document.getElementById('round-count').innerText = currentRound + 1;
                
                let textIndex = Math.floor(Math.random() * colors.length);
                let colorIndex = Math.floor(Math.random() * colors.length);
                if (Math.random() > 0.3) {{ while(colorIndex === textIndex) colorIndex = Math.floor(Math.random() * colors.length); }}
                
                currentColor = colors[colorIndex];
                let display = document.getElementById('word-display');
                display.innerText = colors[textIndex];
                display.style.color = hexColors[currentColor];
                startTime = Date.now();
            }}

            function checkAnswer(selectedColor) {{
                totalRT += (Date.now() - startTime);
                if (selectedColor !== currentColor) errors++;
                currentRound++; nextRound();
            }}

            async function finishGame() {{
                document.getElementById('game-ui').style.display = 'none'; document.getElementById('result-text').innerText = "Syncing telemetry...";
                
                let avgRT = Math.round(totalRT / maxRounds);
                let payload = {{ "task_type": "stroop_test", "age_group": "19-25", "action_initiation_time_ms": avgRT, "total_response_time_ms": totalRT, "cursor_reversals": errors, "is_correct": (errors === 0) }};

                try {{
                    let res = await fetch("{api_url}/api/v1/analyze-interaction", {{ method: "POST", headers: {{ "Content-Type": "application/json" }}, body: JSON.stringify(payload) }});
                    let data = await res.json();
                    
                    document.getElementById('result-text').innerText = "";
                    document.getElementById('badge-msg').innerText = data.analysis.detected_pattern;
                    document.getElementById('metrics-summary').innerHTML = `Cognitive Latency: <b>${{avgRT}}ms</b><br>Inhibition Failures: <b>${{errors}}</b>`;
                    document.getElementById('mascot-widget').style.display = 'block';
                    
                    setTimeout(() => {{ document.getElementById('start-btn').style.display = 'block'; document.getElementById('start-btn').innerText = "Restart Module"; }}, 2000);
                }} catch(err) {{
                    document.getElementById('result-text').innerHTML = "Error syncing with server."; document.getElementById('start-btn').style.display = 'block';
                }}
            }}
        </script>
    </body>
    </html>
    """