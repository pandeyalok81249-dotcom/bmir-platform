'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import {
  ShieldAlert,
  ShieldCheck,
  Key,
  Users,
  Lock,
  Cpu,
  Database,
  CheckCircle2,
  Clock,
  Eye,
  Activity,
} from 'lucide-react';

export default function SecuritySettingsView() {
  const { user } = useApp();
  const [providerStatus, setProviderStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bmirApi
      .getProviderStatus()
      .then((data) => {
        setProviderStatus(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <Lock className="w-3.5 h-3.5" />
            <span>Enterprise Security & Architecture</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            Security, Governance & System Settings
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Configure secure AI provider integrations, review RBAC role permissions, and enforce data
            integrity verification protocols for BMIR research assets.
          </p>
        </div>
      </div>

      {/* AI Provider Gateway Architecture */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-[#19C7D9]" />
            <h3 className="text-sm font-bold text-white font-heading">AI Provider Gateway Connectivity</h3>
          </div>
          <span className="text-xs text-emerald-400 font-semibold flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Environment Key Security Active</span>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="bg-[#071426] border border-[#1E3352] rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">Google Gemini</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Primary Active
              </span>
            </div>
            <div className="text-xs text-gray-400">
              Provider: <code className="text-[#19C7D9]">GEMINI_API_KEY</code>
            </div>
            <div className="text-[11px] text-gray-500">
              Powers AI Research Assistant, Patent Prior-Art, and Literature Summarizer.
            </div>
          </div>

          <div className="bg-[#071426] border border-[#1E3352] rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">OpenAI Gateway</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                Multi-Model Peer
              </span>
            </div>
            <div className="text-xs text-gray-400">
              Provider: <code className="text-blue-400">OPENAI_API_KEY</code>
            </div>
            <div className="text-[11px] text-gray-500">
              Used in multi-model consensus evaluation and technical feasibility verification.
            </div>
          </div>

          <div className="bg-[#071426] border border-[#1E3352] rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">Anthropic Claude</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30">
                Reasoning Peer
              </span>
            </div>
            <div className="text-xs text-gray-400">
              Provider: <code className="text-purple-400">ANTHROPIC_API_KEY</code>
            </div>
            <div className="text-[11px] text-gray-500">
              Used for rigorous comparative reasoning and methodological critique.
            </div>
          </div>
        </div>
      </div>

      {/* Data Verification Protocol Policy */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold text-white font-heading">
            Strict BMIR Data Verification Standards
          </h3>
        </div>

        <p className="text-xs text-gray-400 leading-relaxed">
          In adherence to BMIR intellectual property and research integrity guidelines, all data presented
          on public surfaces or certified in technical reports is classified into five strict levels:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-1 text-xs">
          <div className="p-3 rounded-xl bg-[#071426] border border-emerald-500/30 space-y-1">
            <div className="font-bold text-emerald-400">1. Verified</div>
            <div className="text-[11px] text-gray-400">
              Official Gazette published IPO patents or independently documented lab trials.
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-amber-500/30 space-y-1">
            <div className="font-bold text-amber-400">2. Pending Verification</div>
            <div className="text-[11px] text-gray-400">
              Filed provisional patents or ongoing validation studies awaiting third-party review.
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-blue-500/30 space-y-1">
            <div className="font-bold text-blue-400">3. Draft</div>
            <div className="text-[11px] text-gray-400">
              Formulated technical concepts undergoing internal literature analysis and modeling.
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-purple-500/30 space-y-1">
            <div className="font-bold text-purple-400">4. Unpublished</div>
            <div className="text-[11px] text-gray-400">
              Confidential trade secrets, early invention disclosures, and pre-filing claims.
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-gray-500/30 space-y-1">
            <div className="font-bold text-gray-400">5. Archived</div>
            <div className="text-[11px] text-gray-400">
              Superseded prototypes, legacy project branches, or historical research records.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

