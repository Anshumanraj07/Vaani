'use client';

import { useState } from 'react';
import { supabase } from '../../lib/supabase';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [step, setStep] = useState(1); // For multi-step signup

  // Account States
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');

  // Cognitive Profile States (The AI Context)
  const [age, setAge] = useState('');
  const [philosophy, setPhilosophy] = useState('Stoicism');
  const [wellnessRules, setWellnessRules] = useState('');

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Step 1 validation
  const handleNextStep = (e: React.FormEvent) => {
    e.preventDefault();
    setStep(2);
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      if (isSignUp) {
        // 1. Sign Up the User
        const { data: authData, error: authError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
          },
        });
        if (authError) throw authError;

        if (authData?.user) {
          // 2. Directly update the profile table with cognitive details (No email activation barrier)
          const { error: profileError } = await supabase
            .from('profiles')
            .update({
              age: parseInt(age),
              philosophical_baseline: philosophy,
              wellness_rules: wellnessRules,
            })
            .eq('id', authData.user.id);

          if (profileError) throw profileError;
          
          setMessage('Identity initialized successfully! Redirecting...');
          setTimeout(() => router.push('/'), 1500);
        }
      } else {
        // Login Flow
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        
        router.push('/');
      }
    } catch (error: any) {
      setMessage(error.message || 'Matrix synchronization failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#E5E5E5] flex flex-col justify-center items-center px-4 font-mono select-none">
      <div className="w-full max-w-md bg-[#121212] border border-[#262626] rounded-xl p-8 shadow-sm">
        
        {/* Minimalist Header */}
        <div className="mb-8 text-left">
          <h1 className="text-2xl font-bold tracking-tighter text-white">
            VAANI / {isSignUp ? `INITIALIZE_0${step}` : 'AUTHENTICATE'}
          </h1>
          <p className="text-xs text-[#737373] mt-1">
            {isSignUp ? 'Constructing user cognitive baseline matrix.' : 'Enter credentials to access core environment.'}
          </p>
        </div>

        {/* LOGIN FORM */}
        {!isSignUp && (
          <form onSubmit={handleAuth} className="space-y-4">
            <div>
              <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Email</label>
              <input
                type="email"
                placeholder="name@domain.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                required
              />
            </div>

            <div>
              <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white hover:bg-[#E5E5E5] text-black font-semibold py-2.5 rounded-md text-xs tracking-wider transition-colors disabled:opacity-50 mt-2"
            >
              {loading ? 'SYNCHRONIZING...' : 'ENTER SYSTEM'}
            </button>
          </form>
        )}

        {/* SIGNUP FORM (MULTI-STEP) */}
        {isSignUp && (
          <form onSubmit={step === 1 ? handleNextStep : handleAuth} className="space-y-4">
            {step === 1 ? (
              <>
                {/* Step 1: Credentials */}
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Full Name</label>
                  <input
                    type="text"
                    placeholder="Anshuman Raj"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Email</label>
                  <input
                    type="email"
                    placeholder="name@domain.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Password</label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-white hover:bg-[#E5E5E5] text-black font-semibold py-2.5 rounded-md text-xs tracking-wider transition-colors mt-2"
                >
                  NEXT: COGNITIVE DETAILS →
                </button>
              </>
            ) : (
              <>
                {/* Step 2: Cognitive & AI Context Fields */}
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Exact Age</label>
                  <input
                    type="number"
                    placeholder="19"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Philosophical Baseline</label>
                  <select
                    value={philosophy}
                    onChange={(e) => setPhilosophy(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans"
                  >
                    <option value="Stoicism">Stoicism</option>
                    <option value="Existentialism">Existentialism</option>
                    <option value="Nihilism">Nihilism</option>
                    <option value="Zorba the Buddha">Zorba the Buddha</option>
                    <option value="Materialism">Materialism</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[#737373] mb-1">Wellness & Bio Rules (AI Context)</label>
                  <textarea
                    placeholder="E.g., No sugar/oily food, Fasting windows, Circadian alignment based on body heat."
                    value={wellnessRules}
                    onChange={(e) => setWellnessRules(e.target.value)}
                    rows={3}
                    className="w-full bg-[#1A1A1A] border border-[#262626] rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors font-sans resize-none text-xs leading-relaxed"
                  />
                </div>

                <div className="flex gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="w-1/3 border border-[#262626] hover:bg-[#1A1A1A] text-white py-2.5 rounded-md text-xs transition-colors"
                  >
                    BACK
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-2/3 bg-white hover:bg-[#E5E5E5] text-black font-semibold py-2.5 rounded-md text-xs tracking-wider transition-colors disabled:opacity-50"
                  >
                    {loading ? 'INITIALIZING...' : 'BUILD MATRIX'}
                  </button>
                </div>
              </>
            )}
          </form>
        )}

        {/* Feedback Messages */}
        {message && (
          <div className="mt-4 text-center text-xs p-2 rounded border border-[#262626] bg-[#161616] text-[#A3A3A3]">
            {message}
          </div>
        )}

        {/* Toggle Mode Footer */}
        <div className="mt-6 text-center text-xs text-[#737373]">
          {isSignUp ? 'Existing instance?' : 'New subject entry?'} {' '}
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setStep(1);
              setMessage('');
            }}
            className="text-white hover:underline ml-1 font-semibold"
          >
            {isSignUp ? 'Sign In' : 'Register Profile'}
          </button>
        </div>

      </div>
    </div>
  );
}