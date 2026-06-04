"use client";

import React, { useState } from "react";
import { supabase } from '@/lib/supabase'; // Extra '../' lagaya hai kyunki yeh 'auth' folder ke andar hai
import { useRouter } from "next/navigation";
import { Brain } from "lucide-react";

export default function AuthPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError(error.message);
    } else {
      router.push("/"); // Login success par bahar wale page.tsx (Dashboard) par bhej dega
    }
    setLoading(false);
  };

  const handleSignUp = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);

    const { error } = await supabase.auth.signUp({ email, password });

    if (error) {
      setError(error.message);
    } else {
      setMessage("Check your email for the confirmation link!");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4 font-sans text-black">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
        
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
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all"
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
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className="text-xs font-bold text-red-500 text-center">{error}</p>}
          {message && <p className="text-xs font-bold text-green-600 text-center">{message}</p>}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleSignUp}
              disabled={loading}
              className="flex-1 py-3 px-4 bg-white border border-gray-200 text-black font-bold rounded-xl hover:bg-gray-50 active:scale-95 transition-all text-sm disabled:opacity-50"
            >
              REGISTER
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 px-4 bg-black text-white font-bold rounded-xl shadow-md hover:bg-gray-800 active:scale-95 transition-all text-sm disabled:opacity-50"
            >
              {loading ? "VERIFYING..." : "ACCESS SYSTEM"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}