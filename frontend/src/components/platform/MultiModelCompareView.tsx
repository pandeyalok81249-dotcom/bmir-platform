'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Layers, Sparkles, AlertTriangle, CheckCircle2, XCircle, HelpCircle, ArrowRight } from 'lucide-react';

export default function MultiModelCompareView() {
  const [query, setQuery] = useState(
    'What are the primary thermodynamic limits and structural failure modes of a 200-bar carbon-composite green hydrogen storage cylinder?'
  );
  const [domain, setDomain] = useState('Renewable Energy');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunComparison = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);

    try {
      const data = await bmirApi.multiModelCompare(query, domain);
      setResult(data);
    } catch (err: any) {
      alert(`Comparison failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <Layers className="w-3.5 h-3.5" />
          <span>Multi-Model Intelligence Engine</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Comparative Reasoning & Consensus Extraction
        </h2>
        <p className="text-xs text-gray-400">
          Submit the same research hypothesis simultaneously across OpenAI GPT-4o, Google Gemini 1.5 Pro, and Anthropic Claude 3.5 Sonnet to identify agreements, contradictions, and empirical gaps.
        </p>
      </div>

      {/* Query Form */}
      <form onSubmit={handleRunComparison} className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1.5">
            Research Question / Technical Hypothesis
          </label>
          <textarea
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-gray-400">Target Domain:</span>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
            >
              <option value="Renewable Energy">Renewable Energy (Hydrogen)</option>
              <option value="Agriculture & Smart Farming">Agriculture & Smart Farming</option>
              <option value="Healthcare & Medical Technology">Healthcare & Medical Technology</option>
              <option value="Infrastructure & Civil Engineering">Infrastructure & Transit</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{loading ? 'Evaluating Across 3 Models...' : 'Execute Multi-Model Analysis'}</span>
          </button>
        </div>
      </form>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Scientific Disclaimer */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold uppercase tracking-wider block">Empirical Truth Rule:</span>
              <span>{result.disclaimer}</span>
            </div>
          </div>

          {/* Individual Model Output Columns */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(result.individual_responses || {}).map(([key, item]: [string, any]) => (
              <div key={key} className="p-5 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-[#1E3352]">
                  <span className="text-xs font-bold text-white font-heading">{item.model}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-[#19C7D9]">
                    Conf: {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-[11px] text-[#19C7D9] font-semibold">{item.perspective}</div>
                <div className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">{item.response}</div>
              </div>
            ))}
          </div>

          {/* Comparative Consensus & Disagreement Matrix */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Agreements */}
            <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                <span>Key Points of Agreement (Consensus)</span>
              </div>
              <ul className="space-y-2 text-xs text-gray-300">
                {result.key_agreements?.map((ag: string, idx: number) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-emerald-400">•</span>
                    <span>{ag}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Disagreements */}
            <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
                <XCircle className="w-4 h-4" />
                <span>Key Contradictions & Divergences</span>
              </div>
              <ul className="space-y-2 text-xs text-gray-300">
                {result.key_disagreements?.map((dis: string, idx: number) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-rose-400">•</span>
                    <span>{dis}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Missing Empirical Evidence & Synthesis */}
          <div className="p-6 rounded-2xl bg-[#071426] border border-[#1E3352] space-y-4">
            <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
              <HelpCircle className="w-4 h-4" />
              <span>Identified Missing Empirical Evidence</span>
            </div>
            <ul className="space-y-1.5 text-xs text-gray-300">
              {result.missing_evidence?.map((me: string, idx: number) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-amber-400">→</span>
                  <span>{me}</span>
                </li>
              ))}
            </ul>

            <div className="pt-4 border-t border-[#1E3352] space-y-1">
              <div className="text-xs font-bold text-white uppercase tracking-wider">
                Consolidated Synthesis:
              </div>
              <p className="text-xs text-gray-300 leading-relaxed italic">{result.consolidated_synthesis}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

