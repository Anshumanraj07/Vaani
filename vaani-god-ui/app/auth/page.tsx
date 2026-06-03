'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      if (isSignUp) {
        // Sign Up Flow
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
          },
        });
        if (error) throw error;
        setMessage('Registration successful! Check your email for confirmation.');
      } else {
        // Login Flow
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        
        // Login hone ke baad seedha onboarding check par bhejenge
        router.push('/onboarding');
      }
    } catch (error: any) {
      setMessage(error.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-gray-100 flex flex-col justify-center items-center px-4 font-sans">
      <div className="w-full max-w-md bg-[#151D30] border border-gray-800 rounded-2xl p-8 shadow-2xl backdrop-blur-md">
        
        {/* Brand Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold tracking-wider bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            VAANI
          </h1>
          <p className="text-sm text-gray-400 mt-2">
            {isSignUp ? 'Initialize your Cognitive Profile' : 'Access your Cognitive Dashboard'}
          </p>
        </div>

        {/* Auth Form */}
        <form onSubmit={handleAuth} className="space-y-5">
          {isSignUp && (
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Full Name</label>
              <input
                type="text"
                placeholder="Anshuman Raj"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-[#0B0F19] border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#0B0F19] border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#0B0F19] border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-xl transition-all duration-200 transform hover:scale-[1.01] text-sm mt-4 shadow-lg disabled:opacity-50"
          >
            {loading ? 'Processing Matrix...' : isSignUp ? 'Create System Account' : 'Authenticate'}
          </button>
        </form>

        {/* Feedback Message */}
        {message && (
          <div className="mt-4 text-center text-xs p-3 rounded-lg bg-[#0B0F19] border border-gray-800 text-indigo-400">
            {message}
          </div>
        )}

        {/* Toggle View Link */}
        <div className="mt-6 text-center text-xs text-gray-400">
          {isSignUp ? 'Already mapped?' : 'New instance?'} {' '}
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-indigo-400 hover:underline font-semibold ml-1"
          >
            {isSignUp ? 'Sign In' : 'Register Profile'}
          </button>
        </div>

      </div>
    </div>
  );
}