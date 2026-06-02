"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Square, Play, Target, Palette, BarChart3, RefreshCw, Activity, Brain } from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

export default function VaaniApp() {
  const [activeTab, setActiveTab] = useState("voice");
  const tabs = [
    { id: "voice", label: "Voice AI", icon: <Mic size={16} /> },
    { id: "games", label: "Cognitive Module", icon: <Brain size={16} /> },
    { id: "telemetry", label: "Telemetry", icon: <Activity size={16} /> },
  ];

  return (
    <div className="min-h-screen bg-[#fafafa] text-[#111] font-sans selection:bg-black selection:text-white">
      {/* Sleek Navbar */}
      <header className="border-b border-gray-200 bg-white/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold tracking-tight text-lg">
            <span className="w-6 h-6 bg-black rounded-md flex items-center justify-center text-white text-xs">V</span>
            VAANI.
          </div>
          
          {/* Vercel Style Animated Tab Switcher */}
          <div className="flex p-1 bg-gray-100/80 rounded-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-4 py-1.5 text-sm font-medium transition-colors rounded-md flex items-center gap-2 z-10 ${
                  activeTab === tab.id ? "text-black" : "text-gray-500 hover:text-black"
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="active-tab"
                    className="absolute inset-0 bg-white rounded-md shadow-sm border border-gray-200/50"
                    style={{ zIndex: -1 }}
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {activeTab === "voice" && <VoiceModule key="voice" />}
          {activeTab === "games" && <GamesModule key="games" />}
          {activeTab === "telemetry" && <TelemetryModule key="telemetry" />}
        </AnimatePresence>
      </main>
    </div>
  );
}

// --------------------------------------------------------
// 1. VOICE MODULE (Native Web Audio API)
// --------------------------------------------------------
function VoiceModule() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [status, setStatus] = useState("Idle");
  const [result, setResult] = useState<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

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
      setStatus("Recording... Speak naturally.");
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
    setStatus("Analyzing neural patterns...");
    const formData = new FormData();
    formData.append("file", new File([audioBlob], "recording.wav", { type: "audio/wav" }));

    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-audio`, { method: "POST", body: formData });
      const data = await res.json();
      setResult(data);
      setStatus("Analysis Complete.");
    } catch (err) {
      setStatus("Error connecting to server.");
    }
  };

  const playTTS = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      <h1 className="text-3xl font-bold tracking-tight mb-2">Vocal Telemetry</h1>
      <p className="text-gray-500 mb-8">Record your baseline audio to detect cognitive markers and speech patterns.</p>

      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm flex flex-col items-center">
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
            className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center text-white transition-all shadow-lg ${
              isRecording ? "bg-red-500 hover:bg-red-600" : "bg-black hover:bg-gray-800"
            }`}
          >
            {isRecording ? <Square size={24} fill="currentColor" /> : <Mic size={28} />}
          </button>
        </div>
        <p className="text-sm font-medium text-gray-600 mb-6">{status}</p>

        {audioBlob && !isRecording && (
          <button
            onClick={analyzeAudio}
            className="px-6 py-2.5 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors"
          >
            Process Audio Baseline
          </button>
        )}
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-6 space-y-4">
          <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Transcription</h3>
            <p className="text-lg italic text-gray-800">"{result.transcription.text}"</p>
          </div>
          <div className="p-6 bg-black text-white rounded-2xl shadow-lg relative overflow-hidden">
            <div className="relative z-10">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Detected Superpower</h3>
              <p className="text-xl font-medium mb-4">{result.cognitive_analysis.superpower}</p>
              <button
                onClick={() => playTTS(result.cognitive_analysis.superpower)}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Play size={16} /> Hear Insight
              </button>
            </div>
            {/* Minimalist background decoration */}
            <div className="absolute -bottom-10 -right-10 opacity-10">
              <Brain size={150} />
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

// --------------------------------------------------------
// 2. GAMES MODULE (React Native Logic)
// --------------------------------------------------------
function GamesModule() {
  const [activeGame, setActiveGame] = useState<"menu" | "tracker" | "stroop">("menu");

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      {activeGame === "menu" && (
        <>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Cognitive Diagnostics</h1>
          <p className="text-gray-500 mb-8">Select a kinematic or impulse control module.</p>
          <div className="grid md:grid-cols-2 gap-4">
            <div onClick={() => setActiveGame("tracker")} className="group p-6 bg-white border border-gray-200 rounded-2xl cursor-pointer hover:border-black hover:shadow-md transition-all">
              <Target size={32} className="mb-4 text-gray-800 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-1">Spatial Tracker</h3>
              <p className="text-sm text-gray-500">Measure visual-spatial reaction and motor latency (20 Iterations).</p>
            </div>
            <div onClick={() => setActiveGame("stroop")} className="group p-6 bg-white border border-gray-200 rounded-2xl cursor-pointer hover:border-black hover:shadow-md transition-all">
              <Palette size={32} className="mb-4 text-gray-800 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-1">Impulse Control (Stroop)</h3>
              <p className="text-sm text-gray-500">Test cognitive inhibition and executive functioning (12 Iterations).</p>
            </div>
          </div>
        </>
      )}
      {activeGame === "tracker" && <TrackerGame onBack={() => setActiveGame("menu")} />}
      {activeGame === "stroop" && <StroopGame onBack={() => setActiveGame("menu")} />}
    </motion.div>
  );
}

// --- SUB-GAME: Tracker ---
function TrackerGame({ onBack }: { onBack: () => void }) {
  const [phase, setPhase] = useState<"idle" | "playing" | "done">("idle");
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [pos, setPos] = useState({ x: 50, y: 50 });
  const [result, setResult] = useState<any>(null);
  
  const startTimeRef = useRef(0);
  const totalRTRef = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const start = () => {
    setHits(0); setMisses(0); totalRTRef.current = 0; setPhase("playing"); spawn();
  };

  const spawn = () => {
    if (hits >= 19) { finish(); return; } // Ends at 20
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
    const payload = { task_type: "spatial_rotation", age_group: "19-25", action_initiation_time_ms: avgRT, total_response_time_ms: totalRTRef.current, cursor_reversals: misses, is_correct: true };
    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-interaction`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      setResult(await res.json());
    } catch (e) { alert("API Error"); }
  };

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-sm font-medium text-gray-500 hover:text-black">← Back to Modules</button>
      <div className="flex justify-between items-end">
        <h2 className="text-2xl font-bold">Spatial Tracker</h2>
        <span className="text-sm font-bold bg-gray-100 px-3 py-1 rounded-full">Iteration: {hits}/20</span>
      </div>
      
      <div ref={containerRef} onClick={handleMiss} className="w-full h-96 bg-white border border-gray-200 rounded-2xl relative overflow-hidden shadow-inner cursor-crosshair">
        {phase === "idle" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/5 backdrop-blur-sm z-10">
            <button onClick={start} className="px-8 py-3 bg-black text-white font-bold rounded-lg hover:scale-105 transition-transform">Initiate Sequence</button>
          </div>
        )}
        {phase === "playing" && (
          <div onClick={handleHit} style={{ left: pos.x, top: pos.y }} className="absolute w-10 h-10 bg-black rounded-full shadow-lg hover:scale-95 transition-transform" />
        )}
        {phase === "done" && result && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-white z-10 p-8 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase mb-2">Diagnostic Complete</p>
            <h3 className="text-2xl font-bold mb-4">{result.analysis.detected_pattern}</h3>
            <div className="flex gap-4 mb-6">
              <div className="bg-gray-50 px-4 py-2 rounded-lg border border-gray-100"><span className="block text-xs text-gray-500">Avg Latency</span><span className="font-bold">{Math.round(totalRTRef.current / 20)}ms</span></div>
              <div className="bg-gray-50 px-4 py-2 rounded-lg border border-gray-100"><span className="block text-xs text-gray-500">Inaccuracies</span><span className="font-bold">{misses}</span></div>
            </div>
            <button onClick={start} className="px-6 py-2 bg-black text-white rounded-lg text-sm">Restart Module</button>
          </div>
        )}
      </div>
    </div>
  );
}

// --- SUB-GAME: Stroop ---
function StroopGame({ onBack }: { onBack: () => void }) {
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
    if (round >= 11) { finish(); return; } // Ends at 12
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
    const payload = { task_type: "stroop_test", age_group: "19-25", action_initiation_time_ms: avgRT, total_response_time_ms: totalRTRef.current, cursor_reversals: errors, is_correct: (errors === 0) };
    try {
      const res = await fetch(`${API_URL}/api/v1/analyze-interaction`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      setResult(await res.json());
    } catch (e) { alert("API Error"); }
  };

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-sm font-medium text-gray-500 hover:text-black">← Back to Modules</button>
      <div className="flex justify-between items-end">
        <h2 className="text-2xl font-bold">Impulse Control</h2>
        <span className="text-sm font-bold bg-gray-100 px-3 py-1 rounded-full">Iteration: {round}/12</span>
      </div>
      
      <div className="w-full h-96 bg-white border border-gray-200 rounded-2xl flex flex-col items-center justify-center relative shadow-sm">
        {phase === "idle" && (
          <div className="text-center">
            <p className="text-gray-500 mb-6">Match the <span className="font-bold text-black">INK COLOR</span>. Ignore the text.</p>
            <button onClick={start} className="px-8 py-3 bg-black text-white font-bold rounded-lg hover:scale-105 transition-transform">Initiate Sequence</button>
          </div>
        )}
        
        {phase === "playing" && (
          <div className="w-full max-w-sm px-6">
            <h1 style={{ color: hexMap[ink] }} className="text-5xl font-black uppercase tracking-widest text-center mb-12 drop-shadow-sm">{word}</h1>
            <div className="grid grid-cols-2 gap-4">
              {colors.map(c => (
                <button key={c} onClick={() => handleAnswer(c)} className="py-4 rounded-xl border border-gray-200 bg-gray-50 text-black font-bold uppercase tracking-wider hover:bg-gray-100 hover:border-gray-300 active:scale-95 transition-all">
                  {c}
                </button>
              ))}
            </div>
          </div>
        )}

        {phase === "done" && result && (
          <div className="text-center p-8">
            <p className="text-xs font-bold text-gray-400 uppercase mb-2">Analysis Complete</p>
            <h3 className="text-2xl font-bold mb-4">{result.analysis.detected_pattern}</h3>
            <div className="flex justify-center gap-4 mb-6">
              <div className="bg-gray-50 px-4 py-2 rounded-lg border border-gray-100"><span className="block text-xs text-gray-500">Avg Latency</span><span className="font-bold">{Math.round(totalRTRef.current / 12)}ms</span></div>
              <div className="bg-gray-50 px-4 py-2 rounded-lg border border-gray-100"><span className="block text-xs text-gray-500">Inhibition Failures</span><span className="font-bold text-red-500">{errors}</span></div>
            </div>
            <button onClick={start} className="px-6 py-2 bg-black text-white rounded-lg text-sm">Restart Module</button>
          </div>
        )}
      </div>
    </div>
  );
}

// --------------------------------------------------------
// 3. TELEMETRY DASHBOARD (Minimalist API Fetch)
// --------------------------------------------------------
function TelemetryModule() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/history`);
      const json = await res.json();
      setData(json.data || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchHistory(); }, []);

  const avgRT = data.length > 0 ? Math.round(data.reduce((acc, curr) => acc + curr.reaction_time_ms, 0) / data.length) : 0;
  const latestPattern = data.length > 0 ? data[data.length - 1].detected_pattern : "N/A";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Session Telemetry</h1>
          <p className="text-gray-500">Historical logs and cognitive baseline analysis.</p>
        </div>
        <button onClick={fetchHistory} className="p-2 border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600 transition-colors">
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Sessions</p>
          <p className="text-4xl font-black">{data.length}</p>
        </div>
        <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Mean Latency</p>
          <p className="text-4xl font-black">{avgRT} <span className="text-xl text-gray-400 font-medium">ms</span></p>
        </div>
      </div>

      <div className="p-8 bg-black text-white rounded-2xl shadow-lg relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4 text-gray-400">
            <BarChart3 size={20} /> <span className="font-semibold uppercase tracking-wider text-sm">Executive Summary</span>
          </div>
          {data.length > 0 ? (
            <p className="text-lg leading-relaxed text-gray-200">
              Analysis of <b className="text-white">{data.length}</b> logged interactions indicates a stable motor-cognitive mean latency of <b className="text-white">{avgRT}ms</b>. The latest diagnostic highlights a pattern consistent with <b className="text-white">"{latestPattern}"</b>, forming the current cognitive baseline.
            </p>
          ) : (
            <p className="text-gray-400 italic">Insufficient telemetry data. Please complete a diagnostic module first.</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}