"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Square, Play, Target, Palette, BarChart3, RefreshCw, Activity, Brain, LogOut } from "lucide-react";
import { supabase } from "../lib/supabase"; // Root app directory se lib folder ka direct clean path

const API_URL = "https://vaani-fppo.onrender.com";

export default function VaaniApp() {
  const [userId, setUserId] = useState<string | null>(null);
  const [loadingSession, setLoadingSession] = useState(true);
  const [activeTab, setActiveTab] = useState("voice");
  
  // Auth Form State
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authMessage, setAuthMessage] = useState<string | null>(null);

  const tabs = [
    { id: "voice", label: "Voice AI", icon: <Mic size={16} /> },
    { id: "games", label: "Cognitive Modules", icon: <Brain size={16} /> },
    { id: "telemetry", label: "Telemetry", icon: <Activity size={16} /> },
  ];

  // --- Real-time Session Watcher ---
  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        setUserId(session.user.id);
      }
      setLoadingSession(false);
    };

    checkUser();

    // Listen for auth changes dynamically
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setUserId(session.user.id);
      } else {
        setUserId(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // --- Auth Handlers ---
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthMessage(null);

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setAuthError(error.message);
    setAuthLoading(false);
  };

  const handleSignUp = async () => {
    setAuthLoading(true);
    setAuthError(null);
    setAuthMessage(null);

    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setAuthError(error.message);
    } else {
      setAuthMessage("Authorization link sent! Check your email.");
    }
    setAuthLoading(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUserId(null);
  };

  if (loadingSession) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center font-mono text-xs tracking-widest uppercase text-gray-500">
        Initializing Vaani Engine...
      </div>
    );
  }

  // --------------------------------------------------------
  // CONDITION 1: IF NOT LOGGED IN -> SHOW AUTH SCREEN
  // --------------------------------------------------------
  if (!userId) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-4 font-sans text-black">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }} 
          animate={{ opacity: 1, scale: 1 }} 
          className="max-w-md w-full bg-white p-8 rounded-2xl border border-gray-200 shadow-sm"
        >
          <div className="flex flex-col items-center mb-8">
            <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center text-white mb-4 shadow-lg">
              <Brain size={24} />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Vaani Protocol</h1>
            <p className="text-sm text-gray-500 font-medium">Cognitive Diagnostics Authorization</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Subject ID (Email)</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all text-sm"
                placeholder="operator@vaani.ai"
                required
              />
            </div>
            
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Passcode</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all text-sm"
                placeholder="••••••••"
                required
              />
            </div>

            {authError && <p className="text-xs font-bold text-red-500 text-center bg-red-50 p-2 rounded-lg border border-red-100">{authError}</p>}
            {authMessage && <p className="text-xs font-bold text-green-600 text-center bg-green-50 p-2 rounded-lg border border-green-100">{authMessage}</p>}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={handleSignUp}
                disabled={authLoading}
                className="flex-1 py-3 px-4 bg-white border border-gray-200 text-black font-bold rounded-xl hover:bg-gray-50 active:scale-95 transition-all text-sm disabled:opacity-50"
              >
                REGISTER
              </button>
              <button
                type="submit"
                disabled={authLoading}
                className="flex-1 py-3 px-4 bg-black text-white font-bold rounded-xl shadow-md hover:bg-gray-800 active:scale-95 transition-all text-sm disabled:opacity-50"
              >
                {authLoading ? "VERIFYING..." : "ACCESS SYSTEM"}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    );
  }

  // --------------------------------------------------------
  // CONDITION 2: LOGGED IN -> SHOW INTEGRATED DASHBOARD
  // --------------------------------------------------------
  return (
    <div className="w-full text-[#111] font-sans selection:bg-black selection:text-white pb-20">
      
      {/* 🌟 RESPONSIVE NAVIGATION BAR CONTROL */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 bg-white p-2 md:p-3 rounded-2xl border border-gray-200 shadow-sm">
        
        {/* Tab Switcher */}
        <div className="flex w-full sm:w-auto p-1 bg-gray-100/80 rounded-xl overflow-x-auto no-scrollbar">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative flex-1 sm:flex-none whitespace-nowrap px-3 md:px-5 py-2 text-xs md:text-sm font-semibold transition-colors rounded-lg flex items-center justify-center gap-2 z-10 ${
                activeTab === tab.id ? "text-black" : "text-gray-500 hover:text-black"
              }`}
            >
              {activeTab === tab.id && (
                <motion.div
                  layoutId="active-tab"
                  className="absolute inset-0 bg-white rounded-lg shadow-sm border border-gray-200/50"
                  style={{ zIndex: -1 }}
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
        
        {/* Logout Button */}
        <button 
          onClick={handleLogout} 
          className="flex items-center justify-center gap-2 w-full sm:w-auto px-4 py-2 bg-gray-50 hover:bg-red-50 text-gray-500 hover:text-red-500 text-xs font-bold rounded-xl transition-colors border border-gray-100 hover:border-red-100"
        >
          <LogOut size={16} />
          <span>DISCONNECT</span>
        </button>
      </div>

      {/* 🌟 MODULE CONTROLLER RENDER */}
      <AnimatePresence mode="wait">
        {activeTab === "voice" && <VoiceModule key="voice" userId={userId} />}
        {activeTab === "games" && <GamesModule key="games" userId={userId} />}
        {activeTab === "telemetry" && <TelemetryModule key="telemetry" userId={userId} />}
      </AnimatePresence>
    </div>
  );
}

// ========================================================
// 1. VOICE MODULE (Vocal Biomarkers via Groq Whisper)
// ========================================================
function VoiceModule({ userId }: { userId: string }) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [status, setStatus] = useState("Idle");
  const [result, setResult] = useState<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const prompts = [
    "Describe a recent situation where you felt completely overwhelmed.",
    "Count backwards from 100 by 7s for the next 15 seconds.",
    "Explain the steps you take when planning a complex task.",
    "Describe your typical morning routine in detail."
  ];
  const [activePrompt, setActivePrompt] = useState(prompts[0]);

  useEffect(() => {
    setActivePrompt(prompts[Math.floor(Math.random() * prompts.length)]);
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => chunksRef.current.push(e.data);
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        setAudioBlob(blob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setStatus("Recording vocal biomarkers...");
    } catch (err) {
      alert("Microphone permission denied.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    setStatus("Audio captured. Ready for analysis.");
  };

  const analyzeAudio = async () => {
    if (!audioBlob) return;
    setStatus("Analyzing neural and speech patterns...");
    const formData = new FormData();
    formData.append("file", new File([audioBlob], "recording.wav", { type: "audio/wav" }));
    formData.append("user_id", userId); 

    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-audio`, { method: "POST", body: formData });
      const data = await res.json();
      setResult(data);
      setStatus("Diagnostic Complete.");
    } catch (err) {
      setStatus("Error connecting to diagnostic server.");
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">Vocal Analysis</h1>
      <p className="text-sm md:text-base text-gray-500 mb-6 md:mb-8">Analyze speech cadence for cognitive load indicators.</p>

      <div className="mb-6 p-4 md:p-5 bg-gray-50 border border-gray-200 rounded-xl">
        <h3 className="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Subject Prompt</h3>
        <p className="text-sm md:text-base font-medium text-black">"{activePrompt}"</p>
      </div>

      <div className="bg-white p-6 md:p-8 rounded-2xl border border-gray-200 shadow-sm flex flex-col items-center">
        <div className="relative mb-6">
          {isRecording && (
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="absolute inset-0 bg-red-500/20 rounded-full blur-xl"
            />
          )}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`relative z-10 w-16 h-16 md:w-20 md:h-20 rounded-full flex items-center justify-center text-white transition-all shadow-lg ${
              isRecording ? "bg-red-500 hover:bg-red-600" : "bg-black hover:bg-gray-800"
            }`}
          >
            {isRecording ? <Square size={20} fill="currentColor" /> : <Mic size={24} />}
          </button>
        </div>
        <p className="text-xs md:text-sm font-medium text-gray-600 mb-6 text-center">{status}</p>

        {audioBlob && !isRecording && (
          <button
            onClick={analyzeAudio}
            className="w-full md:w-auto px-6 py-3 bg-black text-white text-sm font-bold rounded-xl hover:bg-gray-800 transition-colors shadow-md"
          >
            Run Clinical Analysis
          </button>
        )}
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-6 space-y-4">
          <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-sm">
            <h3 className="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Transcription Log</h3>
            <p className="text-xs md:text-sm italic text-gray-800">"{result.transcription?.text || result.text}"</p>
          </div>
          <div className="p-6 md:p-8 bg-black text-white rounded-2xl shadow-xl relative overflow-hidden">
            <div className="relative z-10">
              <h3 className="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Primary Cognitive Marker</h3>
              <p className="text-lg md:text-xl font-medium mb-4">{result.cognitive_analysis?.primary_marker || "Neurotypical Speech Pattern Detected"}</p>
              
              {result.cognitive_analysis?.clinical_notes && (
                <div className="mt-4 pt-4 border-t border-gray-800">
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Clinical Notes</h3>
                  <p className="text-xs md:text-sm text-gray-300 leading-relaxed">{result.cognitive_analysis.clinical_notes}</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

// ========================================================
// 2. GAMES MODULE (Impulse & Spatial Sub-Modules)
// ========================================================
function GamesModule({ userId }: { userId: string }) {
  const [activeGame, setActiveGame] = useState<"menu" | "tracker" | "stroop">("menu");

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      {activeGame === "menu" && (
        <>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">Diagnostics</h1>
          <p className="text-sm md:text-base text-gray-500 mb-6 md:mb-8">Select a kinematic or impulse control module.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div onClick={() => setActiveGame("tracker")} className="group p-5 md:p-6 bg-white border border-gray-200 rounded-2xl cursor-pointer hover:border-black hover:shadow-md transition-all active:scale-95">
              <Target size={28} className="mb-3 md:mb-4 text-gray-800 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-base md:text-lg mb-1">Spatial Tracker</h3>
              <p className="text-xs md:text-sm text-gray-500">Measure visual-spatial reaction and motor latency.</p>
            </div>
            <div onClick={() => setActiveGame("stroop")} className="group p-5 md:p-6 bg-white border border-gray-200 rounded-2xl cursor-pointer hover:border-black hover:shadow-md transition-all active:scale-95">
              <Palette size={28} className="mb-3 md:mb-4 text-gray-800 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-base md:text-lg mb-1">Impulse Control</h3>
              <p className="text-xs md:text-sm text-gray-500">Test cognitive inhibition and executive functioning.</p>
            </div>
          </div>
        </>
      )}
      {activeGame === "tracker" && <TrackerGame userId={userId} onBack={() => setActiveGame("menu")} />}
      {activeGame === "stroop" && <StroopGame userId={userId} onBack={() => setActiveGame("menu")} />}
    </motion.div>
  );
}

// --- SUB-GAME 1: Spatial Tracker ---
function TrackerGame({ userId, onBack }: { userId: string, onBack: () => void }) {
  const [phase, setPhase] = useState<"idle" | "playing" | "done">("idle");
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [pos, setPos] = useState({ x: 50, y: 50 });
  const [result, setResult] = useState<any>(null);
  
  const startTimeRef = useRef(0);
  const totalRTRef = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const start = () => { setHits(0); setMisses(0); totalRTRef.current = 0; setPhase("playing"); spawn(); };

  const spawn = () => {
    if (hits >= 19) { finish(); return; } 
    if (containerRef.current) {
      const maxX = containerRef.current.clientWidth - 50;
      const maxY = containerRef.current.clientHeight - 50;
      setPos({ x: Math.max(10, Math.random() * maxX), y: Math.max(10, Math.random() * maxY) });
      startTimeRef.current = Date.now();
    }
  };

  const handleHit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (phase !== "playing") return;
    totalRTRef.current += (Date.now() - startTimeRef.current);
    setHits(h => h + 1);
    spawn();
  };

  const handleMiss = () => { if (phase === "playing") setMisses(m => m + 1); };

  const finish = async () => {
    setPhase("done");
    const avgRT = Math.round(totalRTRef.current / 20);
    const payload = { 
      user_id: userId, task_type: "spatial_rotation", age_group: "19-25", 
      action_initiation_time_ms: avgRT, total_response_time_ms: totalRTRef.current, 
      cursor_reversals: misses, is_correct: true 
    };
    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-interaction`, { 
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) 
      });
      setResult(await res.json());
    } catch (e) { alert("API Error"); }
  };

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-xs md:text-sm font-bold text-gray-400 hover:text-black uppercase tracking-wider">← Back</button>
      <div className="flex justify-between items-end">
        <h2 className="text-xl md:text-2xl font-bold">Spatial Tracker</h2>
        <span className="text-xs md:text-sm font-bold bg-gray-100 px-3 py-1 rounded-lg">Iter: {hits}/20</span>
      </div>
      
      <div ref={containerRef} onClick={handleMiss} className="w-full h-80 md:h-96 bg-white border border-gray-200 rounded-2xl relative overflow-hidden shadow-inner cursor-crosshair">
        {phase === "idle" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/5 backdrop-blur-sm z-10 px-4 text-center">
            <button onClick={start} className="w-full md:w-auto px-8 py-4 bg-black text-white font-bold rounded-xl shadow-lg hover:scale-105 active:scale-95 transition-all">Initiate Sequence</button>
          </div>
        )}
        {phase === "playing" && (
          <div onClick={handleHit} style={{ left: pos.x, top: pos.y }} className="absolute w-12 h-12 md:w-10 md:h-10 bg-black rounded-full shadow-lg active:scale-90 transition-transform" />
        )}
        {phase === "done" && result && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/95 backdrop-blur-md z-10 p-6 text-center">
            <p className="text-[10px] md:text-xs font-bold text-gray-400 uppercase mb-2">Complete</p>
            <h3 className="text-lg md:text-2xl font-bold mb-6">{result.analysis?.detected_pattern || 'Pattern Logged'}</h3>
            <div className="flex gap-2 md:gap-4 mb-8 w-full justify-center">
              <div className="bg-gray-50 px-3 py-2 md:px-4 md:py-3 rounded-xl border border-gray-100 flex-1 max-w-[120px]"><span className="block text-[10px] md:text-xs text-gray-500 uppercase">Avg Latency</span><span className="font-bold text-sm md:text-base">{Math.round(totalRTRef.current / 20)}ms</span></div>
              <div className="bg-gray-50 px-3 py-2 md:px-4 md:py-3 rounded-xl border border-gray-100 flex-1 max-w-[120px]"><span className="block text-[10px] md:text-xs text-gray-500 uppercase">Inaccuracies</span><span className="font-bold text-sm md:text-base">{misses}</span></div>
            </div>
            <button onClick={start} className="w-full md:w-auto px-8 py-3 bg-black text-white font-bold rounded-xl shadow-md">Restart Module</button>
          </div>
        )}
      </div>
    </div>
  );
}

// --- SUB-GAME 2: Stroop Test ---
function StroopGame({ userId, onBack }: { userId: string, onBack: () => void }) {
  const colors = ["red", "blue", "green", "yellow"];
  const hexMap: Record<string, string> = { red: "#ff4b4b", blue: "#1cb0f6", green: "#58cc02", yellow: "#ffc800" };
  
  const [phase, setPhase] = useState<"idle" | "playing" | "done">("idle");
  const [round, setRound] = useState(0);
  const [errors, setErrors] = useState(0);
  const [word, setWord] = useState("");
  const [ink, setInk] = useState("");
  const [result, setResult] = useState<any>(null);
  
  const startTimeRef = useRef(0);
  const totalRTRef = useRef(0);

  const start = () => { setRound(0); setErrors(0); totalRTRef.current = 0; setPhase("playing"); nextRound(); };

  const nextRound = () => {
    if (round >= 11) { finish(); return; } 
    const textIdx = Math.floor(Math.random() * colors.length);
    let colorIdx = Math.floor(Math.random() * colors.length);
    if (Math.random() > 0.3) { while (colorIdx === textIdx) colorIdx = Math.floor(Math.random() * colors.length); }
    
    setWord(colors[textIdx]);
    setInk(colors[colorIdx]);
    startTimeRef.current = Date.now();
  };

  const handleAnswer = (color: string) => {
    totalRTRef.current += (Date.now() - startTimeRef.current);
    if (color !== ink) setErrors(e => e + 1);
    setRound(r => r + 1);
    nextRound();
  };

  const finish = async () => {
    setPhase("done");
    const avgRT = Math.round(totalRTRef.current / 12);
    const payload = { 
      user_id: userId, task_type: "stroop_test", age_group: "19-25", 
      action_initiation_time_ms: avgRT, total_response_time_ms: totalRTRef.current, 
      cursor_reversals: errors, is_correct: (errors === 0) 
    };
    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-interaction`, { 
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) 
      });
      setResult(await res.json());
    } catch (e) { alert("API Error"); }
  };

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-xs md:text-sm font-bold text-gray-400 hover:text-black uppercase tracking-wider">← Back</button>
      <div className="flex justify-between items-end">
        <h2 className="text-xl md:text-2xl font-bold">Impulse Control</h2>
        <span className="text-xs md:text-sm font-bold bg-gray-100 px-3 py-1 rounded-lg">Iter: {round}/12</span>
      </div>
      
      <div className="w-full h-80 md:h-96 bg-white border border-gray-200 rounded-2xl flex flex-col items-center justify-center relative shadow-sm">
        {phase === "idle" && (
          <div className="text-center px-4">
            <p className="text-sm md:text-base text-gray-500 mb-6 md:mb-8">Match the <span className="font-bold text-black border-b-2 border-black pb-1">INK COLOR</span>. Ignore text.</p>
            <button onClick={start} className="w-full md:w-auto px-8 py-4 bg-black text-white font-bold rounded-xl shadow-lg hover:scale-105 active:scale-95 transition-all">Initiate Sequence</button>
          </div>
        )}
        
        {phase === "playing" && (
          <div className="w-full max-w-sm px-4">
            <h1 style={{ color: hexMap[ink] }} className="text-4xl md:text-5xl font-black uppercase tracking-widest text-center mb-8 md:mb-12 drop-shadow-sm">{word}</h1>
            <div className="grid grid-cols-2 gap-3 md:gap-4">
              {colors.map(c => (
                <button key={c} onClick={() => handleAnswer(c)} className="py-4 md:py-5 rounded-xl border-2 border-gray-100 bg-gray-50 text-black font-bold text-sm md:text-base uppercase tracking-wider hover:bg-gray-100 hover:border-gray-300 active:bg-gray-200 active:scale-95 transition-all shadow-sm">
                  {c}
                </button>
              ))}
            </div>
          </div>
        )}

        {phase === "done" && result && (
          <div className="text-center p-6 bg-white/95 backdrop-blur-md absolute inset-0 flex flex-col justify-center items-center rounded-2xl z-10">
            <p className="text-[10px] md:text-xs font-bold text-gray-400 uppercase mb-2">Complete</p>
            <h3 className="text-lg md:text-2xl font-bold mb-6">{result.analysis?.detected_pattern || 'Pattern Logged'}</h3>
            <div className="flex justify-center gap-2 md:gap-4 w-full mb-8">
              <div className="bg-gray-50 px-3 py-2 md:px-4 md:py-3 rounded-xl border border-gray-100 flex-1 max-w-[120px]"><span className="block text-[10px] md:text-xs text-gray-500 uppercase">Avg Latency</span><span className="font-bold text-sm md:text-base">{Math.round(totalRTRef.current / 12)}ms</span></div>
              <div className="bg-red-50 px-3 py-2 md:px-4 md:py-3 rounded-xl border border-red-100 flex-1 max-w-[120px]"><span className="block text-[10px] md:text-xs text-red-400 uppercase">Failures</span><span className="font-bold text-sm md:text-base text-red-600">{errors}</span></div>
            </div>
            <button onClick={start} className="w-full md:w-auto px-8 py-3 bg-black text-white font-bold rounded-xl shadow-md">Restart Module</button>
          </div>
        )}
      </div>
    </div>
  );
}

// ========================================================
// 3. TELEMETRY MODULE (LlamaIndex Aggregate Synthesis RAG)
// ========================================================
function TelemetryModule({ userId }: { userId: string }) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<string>("");
  const [generatingReport, setGeneratingReport] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from('game_sessions')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setSessions(data || []);
    } catch (e) { 
      console.error("Telemetry Sync Failed:", e); 
    }
    setLoading(false);
  };

  const runLlamaIndexReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/generate-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId })
      });
      const data = await res.json();
      setReport(data.summary || "No synthesis returned.");
    } catch (e) {
      setReport("Failed to generate clinical synthesis.");
    }
    setGeneratingReport(false);
  };

  useEffect(() => { fetchHistory(); }, [userId]);

  const avgRT = sessions.length > 0 
    ? Math.round(sessions.reduce((acc, curr) => acc + (curr.metrics?.action_initiation_time_ms || 0), 0) / sessions.length) 
    : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-6 md:mb-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1 md:mb-2">Telemetry Logs</h1>
          <p className="text-sm md:text-base text-gray-500">Historical cognitive baseline analysis.</p>
        </div>
        <button onClick={fetchHistory} className="w-full sm:w-auto flex justify-center p-3 border border-gray-200 rounded-xl hover:bg-gray-50 text-gray-600 transition-colors shadow-sm">
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 md:gap-4 mb-6 md:mb-8">
        <div className="p-5 md:p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <p className="text-[10px] md:text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Total Sessions</p>
          <p className="text-3xl md:text-4xl font-black">{sessions.length}</p>
        </div>
        <div className="p-5 md:p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <p className="text-[10px] md:text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Mean Latency</p>
          <p className="text-3xl md:text-4xl font-black">{avgRT} <span className="text-base md:text-xl text-gray-400 font-medium">ms</span></p>
        </div>
      </div>

      <div className="p-6 md:p-8 bg-black text-white rounded-2xl shadow-xl relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <div className="flex items-center gap-2 text-gray-400">
              <BarChart3 size={20} /> <span className="font-bold uppercase tracking-wider text-[10px] md:text-xs">Aggregate Synthesis</span>
            </div>
            {sessions.length > 0 && (
              <button 
                onClick={runLlamaIndexReport} 
                disabled={generatingReport}
                className="w-full sm:w-auto px-4 py-2 bg-white text-black text-xs font-bold rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 shadow-sm"
              >
                {generatingReport ? "COMPILING..." : "GENERATE REPORT"}
              </button>
            )}
          </div>
          
          {report ? (
            <p className="text-sm leading-relaxed text-gray-200 font-mono bg-gray-900/50 p-4 rounded-xl border border-gray-800">{report}</p>
          ) : sessions.length > 0 ? (
            <p className="text-gray-400 italic text-xs md:text-sm">Click 'Generate Report' to execute LlamaIndex RAG analysis across all logged entries.</p>
          ) : (
            <p className="text-gray-400 italic text-xs md:text-sm">Insufficient telemetry data. Please complete a diagnostic module first.</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}