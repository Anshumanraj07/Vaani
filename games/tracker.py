import json

def render_target_tracker(api_url):
    escaped_url = api_url
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');
            body {{ font-family: 'Nunito', sans-serif; text-align: center; margin:0; padding:0; background: transparent; }}
            #game-area {{ width: 100%; height: 380px; background: #1e1e1e; position: relative; border-radius: 20px; overflow: hidden; border: 3px solid #58cc02; touch-action: none; }}
            #target {{ width: 50px; height: 50px; background: #ff4b4b; position: absolute; border-radius: 50%; display: none; cursor: pointer; box-shadow: 0 0 15px #ff4b4b; -webkit-tap-highlight-color: transparent; }}
            #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 15px 30px; font-size: 18px; font-weight: 900; cursor: pointer; border-radius: 16px; background: #58cc02; border: none; border-bottom: 5px solid #58a700; color: white; text-transform: uppercase; }}
            #start-btn:active {{ border-bottom: none; transform: translate(-50%, -45%); }}
            #score-badge {{ position: absolute; top: 15px; left: 15px; background: #58cc02; color: white; padding: 5px 15px; border-radius: 12px; font-weight: 900; font-size: 16px; }}
            
            /* Duolingo Style Mascot Pop-up Animation */
            .mascot-popup {{ display: none; animation: popUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; background: #252525; border: 3px solid #1cb0f6; border-radius: 20px; padding: 20px; margin-top: 15px; color: white; }}
            .mascot-avatar {{ font-size: 60px; animation: bounce 0.6s infinite alternate; margin-bottom: 10px; }}
            @keyframes popUp {{ 0% {{ transform: scale(0.5); opacity: 0; }} 100% {{ transform: scale(1); opacity: 1; }} }}
            @keyframes bounce {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(-10px); }} }}
            
            #status-text {{ color: #aaa; font-weight: bold; margin-top: 10px; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div id="game-area">
            <div id="score-badge">Hits: <span id="hit-count">0</span>/20</div>
            <button id="start-btn">Start Challenge</button>
            <div id="target"></div>
        </div>
        <div id="status-text">Tap Start to begin</div>
        
        <div id="mascot-widget" class="mascot-popup">
            <div class="mascot-avatar">🦉✨</div>
            <div id="badge-msg" style="font-size: 18px; font-weight: 900; color: #1cb0f6;"></div>
            <div id="metrics-summary" style="margin-top: 10px; font-size: 14px; color: #eee;"></div>
        </div>

        <script>
            let target = document.getElementById('target');
            let startBtn = document.getElementById('start-btn');
            let gameArea = document.getElementById('game-area');
            let hitCountSpan = document.getElementById('hit-count');
            let statusText = document.getElementById('status-text');
            let mascotWidget = document.getElementById('mascot-widget');
            
            let totalHits = 20;
            let currentHits = 0;
            let targetAppearTime = 0;
            let totalRT = 0;
            let misses = 0;
            let gameActive = false;

            startBtn.onclick = (e) => {{
                e.stopPropagation();
                startBtn.style.display = 'none';
                mascotWidget.style.display = 'none';
                statusText.innerText = "Get Ready...";
                currentHits = 0;
                totalRT = 0;
                misses = 0;
                hitCountSpan.innerText = "0";
                
                setTimeout(spawnTarget, 1000);
            }};

            gameArea.onclick = () => {{
                if (gameActive) {{
                    misses++; // Track screen misses/rebounds for touch optimization
                }}
            }};

            function spawnTarget() {{
                if (currentHits >= totalHits) {{
                    finishGame();
                    return;
                }}
                gameActive = true;
                let maxX = gameArea.clientWidth - 60;
                let maxY = gameArea.clientHeight - 60;
                
                // Keep coordinates bounds inside container
                let x = Math.max(10, Math.random() * maxX);
                let y = Math.max(60, Math.random() * maxY); 
                
                target.style.left = x + 'px';
                target.style.top = y + 'px';
                target.style.display = 'block';
                targetAppearTime = Date.now();
                statusText.innerText = "Tap it!";
            }}

            target.onclick = (e) => {{
                e.stopPropagation(); // Prevent counting as a miss on gameArea
                if (!gameActive) return;
                
                let rt = Date.now() - targetAppearTime;
                totalRT += rt;
                currentHits++;
                hitCountSpan.innerText = currentHits;
                target.style.display = 'none';
                gameActive = false;
                
                spawnTarget();
            }};

            async function finishGame() {{
                gameActive = false;
                target.style.display = 'none';
                statusText.innerText = "Processing Telemetry...";
                
                let avgRT = Math.round(totalRT / totalHits);
                let payload = {{
                    "task_type": "spatial_rotation",
                    "age_group": "19-25",
                    "action_initiation_time_ms": avgRT,
                    "total_response_time_ms": totalRT,
                    "cursor_reversals": misses,
                    "is_correct": true
                }};

                try {{
                    let res = await fetch("{escaped_url}/api/v1/analyze-interaction", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify(payload)
                    }});
                    let data = await res.json();
                    
                    statusText.innerText = "Challenge Complete!";
                    document.getElementById('badge-msg').innerText = data.analysis.detected_pattern;
                    document.getElementById('metrics-summary').innerHTML = `Avg Speed: <b>${{avgRT}}ms</b> | Inaccuracies: <b>${{misses}}</b>`;
                    mascotWidget.style.display = 'block';
                    
                    setTimeout(() => {{ startBtn.style.display = 'block'; startBtn.innerText = "Play Again"; }}, 2000);
                }} catch(err) {{
                    statusText.innerText = "API Error connecting to backend.";
                    startBtn.style.display = 'block';
                }}
            }}
        </script>
    </body>
    </html>
    """