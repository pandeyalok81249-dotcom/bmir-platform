'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { X, Lock, Mail, User, Shield, Sparkles } from 'lucide-react';

export default function AuthModal() {
  const { isAuthModalOpen, setIsAuthModalOpen, setUser, setActiveView, lang } = useApp();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [organization, setOrganization] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isAuthModalOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      if (isRegister) {
        const res = await bmirApi.register({
          email,
          password,
          full_name: fullName,
          organization: organization || 'Independent Researcher',
        });
        setUser(res.user);
      } else {
        const res = await bmirApi.login(email, password);
        setUser(res.user);
      }
      setIsAuthModalOpen(false);
      setActiveView('dashboard');
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-6 shadow-2xl text-white">
        {/* Close Button */}
        <button
          onClick={() => setIsAuthModalOpen(false)}
          className="absolute top-6 right-6 p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[11px] font-bold uppercase bg-blue-500/10 text-[#19C7D9] border border-blue-500/20">
            <Lock className="w-3 h-3" />
            <span>Secure Enterprise Workspace</span>
          </div>
          <h2 className="text-2xl font-bold font-heading text-white">
            {isRegister ? 'Register Researcher Account' : 'Sign in to BMIR Workspace'}
          </h2>
          <p className="text-xs text-gray-400">
            {isRegister
              ? 'Request access for academic collaboration, document analysis, and innovation research.'
              : 'Authorized access for researchers, engineers, scientists, and administrators.'}
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400">
            {errorMsg}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {isRegister && (
            <>
              <div>
                <label className="block text-gray-300 font-semibold mb-1">Full Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. Dr. Aditi Rao"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Institution / Organization</label>
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                  placeholder="e.g. IIT Patna / Regional Engineering College"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-gray-300 font-semibold mb-1">Institutional Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                placeholder="email@bmirresearch.in"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-300 font-semibold mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] hover:opacity-95 text-white font-bold text-xs tracking-wide shadow-md transition-all disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : isRegister ? 'Create Researcher Account' : 'Sign In to AI Research Lab'}
          </button>
        </form>

        {/* Toggle between Login and Register */}
        <div className="text-center pt-2 text-xs text-gray-400">
          {isRegister ? (
            <div>
              Already have an account?{' '}
              <button onClick={() => setIsRegister(false)} className="text-[#19C7D9] font-semibold hover:underline">
                Sign In
              </button>
            </div>
          ) : (
            <div>
              New collaborator or researcher?{' '}
              <button onClick={() => setIsRegister(true)} className="text-[#19C7D9] font-semibold hover:underline">
                Register Workspace Account
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

