'use client';

import React, { useState } from 'react';
import { bmirApi } from '@/lib/api';
import { FileCheck, Sparkles, AlertTriangle, ShieldCheck, Search, BookOpen } from 'lucide-react';

export default function PatentAssistantView() {
  const [inventionTitle, setInventionTitle] = useState('High-Efficiency Rotary Dehumidified Grain Conditioning System');
  const [techField, setTechField] = useState('Agricultural Drying & Post-Harvest Processing');
  const [novelty, setNovelty] = useState(
    'Counter-flow warm air conditioning loop coupled with multi-frequency capacitive moisture monitoring and automated exhaust louvers.'
  );
  const [loading, setLoading] = useState(false);
  const [patentAnalysis, setPatentAnalysis] = useState<any>(null);

  const handleSearchPriorArt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inventionTitle.trim() || loading) return;
    setLoading(true);

    try {
      const data = await bmirApi.patentPriorArtAssistant(inventionTitle, techField, novelty);
      setPatentAnalysis(data);
    } catch (err: any) {
      alert(`Patent assistant error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <FileCheck className="w-3.5 h-3.5" />
          <span>Patent Research Assistant</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Prior-Art Investigation, Classification & Claim Synthesis
        </h2>
        <p className="text-xs text-gray-400">
          Formulate structured patent queries, map international patent classifications (IPC / CPC), evaluate potential prior art overlaps, and synthesize independent and dependent claim structures.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSearchPriorArt} className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1">Invention Title</label>
          <input
            type="text"
            value={inventionTitle}
            onChange={(e) => setInventionTitle(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1">Technical Field</label>
          <input
            type="text"
            value={techField}
            onChange={(e) => setTechField(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1">Core Novelty Elements</label>
          <textarea
            rows={3}
            value={novelty}
            onChange={(e) => setNovelty(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md disabled:opacity-50 flex items-center space-x-2"
        >
          <Search className="w-3.5 h-3.5" />
          <span>{loading ? 'Evaluating Patent Landscape...' : 'Run Prior-Art Investigation'}</span>
        </button>
      </form>

      {/* Output */}
      {patentAnalysis && (
        <div className="space-y-6">
          {/* Legal Notice */}
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold uppercase tracking-wider block">Statutory Patent Disclaimer:</span>
              <span>{patentAnalysis.legal_disclaimer}</span>
            </div>
          </div>

          {/* IPC / CPC Classifications */}
          <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
            <span className="text-xs font-bold text-[#19C7D9] uppercase tracking-wider">
              Recommended International Classifications (IPC / CPC)
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {patentAnalysis.recommended_ipc_cpc_classifications?.map((c: any, i: number) => (
                <div key={i} className="p-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs space-y-1">
                  <div className="font-mono font-bold text-white text-sm">{c.code}</div>
                  <div className="text-[11px] text-gray-400">{c.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Prior-Art Pointers */}
          <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-4">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Prior Art Citations & Distinguishing Features
            </span>
            <div className="space-y-3">
              {patentAnalysis.prior_art_similarity_analysis?.map((art: any, i: number) => (
                <div key={i} className="p-4 rounded-xl bg-[#071426] border border-[#1E3352] space-y-1.5 text-xs">
                  <div className="flex justify-between font-semibold text-white">
                    <span>{art.patent_citation}</span>
                    <span className="text-[#19C7D9] font-mono">{art.similarity_score}</span>
                  </div>
                  <p className="text-gray-300">
                    <strong>Distinguishing Innovation:</strong> {art.key_distinguishing_feature}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Claim Structure */}
          <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              Draft Claim Structure Framework
            </span>
            <div className="space-y-2 text-xs text-gray-300 font-mono bg-[#071426] p-4 rounded-xl border border-[#1E3352]">
              <div>1. {patentAnalysis.suggested_claim_structure?.independent_claim_1}</div>
              <div className="pt-2">2. {patentAnalysis.suggested_claim_structure?.dependent_claim_2}</div>
              <div className="pt-2">3. {patentAnalysis.suggested_claim_structure?.dependent_claim_3}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

