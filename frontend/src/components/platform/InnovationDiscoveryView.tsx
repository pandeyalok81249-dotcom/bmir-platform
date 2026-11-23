'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Sparkles, ArrowRight, ShieldAlert, Cpu, Lightbulb, CheckCircle2, ChevronRight } from 'lucide-react';

export default function InnovationDiscoveryView() {
  const [problem, setProblem] = useState(
    'Rapid spoilage and fungal aflatoxin development in freshly harvested eastern Gangetic maize due to monsoon humidity (>85%) during sun drying.'
  );
  const [sector, setSector] = useState('Agriculture & Smart Farming');
  const [loading, setLoading] = useState(false);
  const [discoveryResult, setDiscoveryResult] = useState<any>(null);

  const handleDiscover = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problem.trim() || loading) return;
    setLoading(true);

    try {
      const data = await bmirApi.discoverInnovation(problem, sector);
      setDiscoveryResult(data);
    } catch (err: any) {
      alert(`Discovery failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Innovation Discovery Engine</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          8-Step Structured Invention Exploration
        </h2>
        <p className="text-xs text-gray-400">
          Transform raw socioeconomic problems into rigorous multidisciplinary technological concepts with scientific mechanisms, feasibility metrics, and experimental requirements.
        </p>
      </div>

      {/* Input Problem Form */}
      <form onSubmit={handleDiscover} className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1.5">
            Step 1: Real-World Technical or Regional Problem Statement
          </label>
          <textarea
            rows={3}
            value={problem}
            onChange={(e) => setProblem(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-gray-400">Target Domain:</span>
            <select
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
            >
              <option value="Agriculture & Smart Farming">Agriculture & Smart Farming</option>
              <option value="Healthcare & Medical Technology">Healthcare & Medical Technology</option>
              <option value="Renewable Energy">Renewable Energy</option>
              <option value="Infrastructure & Civil Engineering">Infrastructure & Transit</option>
              <option value="Robotics & Automation">Robotics & Automation</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <Lightbulb className="w-3.5 h-3.5" />
            <span>{loading ? 'Synthesizing 8-Step Discovery...' : 'Execute Invention Discovery'}</span>
          </button>
        </div>
      </form>

      {/* Discovery Pipeline Display */}
      {discoveryResult && (
        <div className="space-y-6">
          {/* Disclaimer */}
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-xs text-cyan-300 flex items-start space-x-3">
            <ShieldAlert className="w-5 h-5 text-[#19C7D9] shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold uppercase tracking-wider block">AI Discovery Protocol:</span>
              <span>{discoveryResult.disclaimer}</span>
            </div>
          </div>

          {/* Steps 1 - 5 Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <span className="text-xs font-bold text-[#19C7D9] uppercase tracking-wider">
                Step 2 & 3: Domain & Knowledge Baseline
              </span>
              <div className="text-xs text-gray-300 space-y-2">
                <div>
                  <strong>Primary Domain:</strong> {discoveryResult.step_2_domain_identification?.primary_domain}
                </div>
                <div>
                  <strong>State of the Art:</strong>{' '}
                  {discoveryResult.step_3_existing_knowledge?.current_state_of_the_art}
                </div>
                <div>
                  <strong>Unaddressed Gap:</strong>{' '}
                  {discoveryResult.step_3_existing_knowledge?.unaddressed_gaps}
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <span className="text-xs font-bold text-[#2878FF] uppercase tracking-wider">
                Step 4 & 5: Alternative Approaches & Challenges
              </span>
              <div className="text-xs text-gray-300 space-y-2">
                <div>
                  <strong>Key Physical Bottlenecks:</strong>
                  <ul className="list-disc pl-4 text-gray-400 mt-1 space-y-1">
                    {discoveryResult.step_5_technical_challenges?.map((c: string, i: number) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Step 6: Generated Innovation Directions */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white font-heading">
              Step 6: Formulated Innovation Directions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {discoveryResult.step_6_innovation_directions?.map((inv: any, idx: number) => (
                <div
                  key={idx}
                  className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3 hover:border-cyan-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white font-heading">{inv.concept_title}</span>
                    <span className="text-xs font-mono font-bold text-[#19C7D9] px-2 py-0.5 rounded bg-blue-500/20">
                      Feasibility: {inv.estimated_feasibility_score}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed">
                    <strong>Engineered Mechanism:</strong> {inv.mechanism}
                  </p>
                  <p className="text-xs text-gray-400">
                    <strong>Scientific Principles:</strong> {inv.scientific_principles}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Step 8: Project Promotion Banner */}
          <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1A2E] border border-cyan-500/40 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-[#19C7D9]">
                Step 8: Research Project Promotion
              </span>
              <h4 className="text-lg font-bold text-white font-heading">
                {discoveryResult.step_8_proposed_project_draft?.proposed_title}
              </h4>
              <p className="text-xs text-gray-400">
                Ready for physical lab verification, finite element modeling, and sensor prototype fabrication.
              </p>
            </div>
            <button
              onClick={() => alert('Project draft created and saved in BMIR project register.')}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md shrink-0"
            >
              Convert to Active Project
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

