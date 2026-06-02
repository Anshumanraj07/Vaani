def render_target_tracker(api_url):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
            body {{ font-family: 'Inter', sans-serif; text-align: center; margin:0; padding:0; background: transparent; color: #111; }}
            
            #game-area {{ width: 100%; height: 380px; background: #ffffff; position: relative; border-radius: 8px; overflow: hidden; border: 1px solid #eaeaea; touch-action: none; box-shadow: inset 0 2px 10px rgba(0,0,0,0.02); }}
            
            #target {{ width: 40px; height: 40px; background: #111111; position: absolute; border-radius: 50%; display: none; cursor: pointer; transition: transform 0.1s; -webkit-tap-highlight-color: transparent; }}
            #target:active {{ transform: scale(0.9); }}
            
            #start-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 12px 28px; font-size: 15px; font-weight: 500; cursor: pointer; border-radius: 6px; background: #111111; border: none; color: white; letter-spacing: 0.5px; transition: 0.2s; }}
            #start-btn:hover {{ background: #333333; }}
            
            #score-badge {{ position: absolute; top: 15px; left: 15px; background: transparent; color: #666; font-weight: 500; font-size: 13px; letter-spacing: 0.5px; }}
            
            /* Minimalist Summary Pop-up */
            .mascot-popup {{ display: none; animation: fadeUp 0.4s ease forwards; background: #ffffff; border: 1px solid #eaeaea; border-radius: 8px; padding: 25px; margin-top: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: left; }}
            @keyframes fadeUp {{ 0% {{ transform: translateY(10px); opacity: 0; }} 100% {{ transform: translateY(0); opacity: 1; }} }}
            
            #status-text {{ color: #666; font-weight: 400; margin-top: 12px; font-size: 14px; letter-spacing: 0.3px; }}
        </style>
    </head>
    <body>
        <div id="game-area">
            <div id="score-badge">ITERATION: <span id="hit-count">0</span>/20</div>
            <button id="start-btn">Initiate Sequence</button>
            <div id="target"></div>
        </div>
        <div id="status-text">Awaiting input...</div>
        
        <div id="mascot-widget" class="mascot-popup">
            <div style="font-size: 12px; font-weight: 600; color: #888; letter-spacing: 1px; margin-bottom: 8px;">DIAGNOSTIC COMPLETE</div>
            <div id="badge-msg" style="font-size: 18px; font-weight: 600; color: #111;"></div>
            <div id="metrics-summary" style="margin-top: 8px; font-size: 14px; color: #555; line-height: 1.5;"></div>
        </div>

        <script>
            let target = document.getElementById('target');
            let startBtn = document.getElementById('start-btn');
            let gameArea = document.getElementById('game-area');
            let hitCountSpan = document.getElementById('hit-count');
            let statusText = document.getElementById('status-text');
            let mascotWidget = document.getElementById('mascot-widget');
            
            let totalHits = 20; let currentHits = 0; let targetAppearTime = 0;
            let totalRT = 0; let misses = 0; let gameActive = false;

            startBtn.onclick = (e) => {{
                e.stopPropagation(); startBtn.style.display = 'none'; mascotWidget.style.display = 'none';
                statusText.innerText = "Tracking active...";
                currentHits = 0; totalRT = 0; misses = 0; hitCountSpan.innerText = "0";
                setTimeout(spawnTarget, 800);
            }};

            gameArea.onclick = () => {{ if (gameActive) misses++; }};

            function spawnTarget() {{
                if (currentHits >= totalHits) {{ finishGame(); return; }}
                gameActive = true;
                let maxX = gameArea.clientWidth - 50; let maxY = gameArea.clientHeight - 50;
                let x = Math.max(10, Math.random() * maxX); let y = Math.max(40, Math.random() * maxY); 
                target.style.left = x + 'px'; target.style.top = y + 'px';
                target.style.display = 'block'; targetAppearTime = Date.now();
            }}

            target.onclick = (e) => {{
                e.stopPropagation(); if (!gameActive) return;
                totalRT += (Date.now() - targetAppearTime);
                currentHits++; hitCountSpan.innerText = currentHits;
                target.style.display = 'none'; gameActive = false;
                spawnTarget();
            }};

            async function finishGame() {{
                gameActive = false; target.style.display = 'none';
                statusText.innerText = "Syncing telemetry...";
                let avgRT = Math.round(totalRT / totalHits);
                
                let payload = {{ "task_type": "spatial_rotation", "age_group": "19-25", "action_initiation_time_ms": avgRT, "total_response_time_ms": totalRT, "cursor_reversals": misses, "is_correct": true }};

                try {{
                    let res = await fetch("{api_url}/api/v1/analyze-interaction", {{ method: "POST", headers: {{ "Content-Type": "application/json" }}, body: JSON.stringify(payload) }});
                    let data = await res.json();
                    
                    statusText.innerText = "";
                    document.getElementById('badge-msg').innerText = data.analysis.detected_pattern;
                    document.getElementById('metrics-summary').innerHTML = `Mean Latency: <b>${{avgRT}}ms</b><br>Inaccuracy Rate: <b>${{misses}}</b> deviations`;
                    mascotWidget.style.display = 'block';
                    
                    setTimeout(() => {{ startBtn.style.display = 'block'; startBtn.innerText = "Restart Module"; }}, 2000);
                }} catch(err) {{
                    statusText.innerText = "Error syncing with server."; startBtn.style.display = 'block';
                }}
            }}
        </script>
    </body>
    </html>
    """