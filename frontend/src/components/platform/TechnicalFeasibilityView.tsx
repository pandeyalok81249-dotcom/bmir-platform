'use client';

import React, { useState } from 'react';
import { Radar, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RechartsRadar,
  ResponsiveContainer,
} from 'recharts';

export default function TechnicalFeasibilityView() {
  const [scores, setScores] = useState({
    scientific: 86,
    engineering: 82,
    materials: 88,
    manufacturing: 78,
    complexity: 72,
    energy: 85,
    economic: 90,
    environmental: 88,
    safety: 84,
  });

  const radarData = [
    { subject: 'Scientific', value: scores.scientific, fullMark: 100 },
    { subject: 'Engineering', value: scores.engineering, fullMark: 100 },
    { subject: 'Materials', value: scores.materials, fullMark: 100 },
    { subject: 'Manufacturing', value: scores.manufacturing, fullMark: 100 },
    { subject: 'Low Complexity', value: 100 - scores.complexity + 50, fullMark: 100 },
    { subject: 'Energy Eff.', value: scores.energy, fullMark: 100 },
    { subject: 'Economic ROI', value: scores.economic, fullMark: 100 },
    { subject: 'Environmental', value: scores.environmental, fullMark: 100 },
    { subject: 'Safety Compliance', value: scores.safety, fullMark: 100 },
  ];

  const overallScore = Math.round(
    (scores.scientific +
      scores.engineering +
      scores.materials +
      scores.manufacturing +
      (100 - scores.complexity) +
      scores.energy +
      scores.economic +
      scores.environmental +
      scores.safety) /
      9
  );

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <Radar className="w-3.5 h-3.5" />
          <span>Technical Feasibility Engine</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Multi-Vector Feasibility Assessment & Radar Scoring
        </h2>
        <p className="text-xs text-gray-400">
          Evaluate proposals across physical, mechanical, material, environmental, and financial constraints with transparent uncertainty boundaries.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Radar Chart Display */}
        <div className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-heading">Feasibility Vector Radar</h3>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/20 text-[#19C7D9]">
              Overall Score: {overallScore}/100
            </span>
          </div>

          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#1E3352" />
                <PolarAngleAxis dataKey="subject" stroke="#94A3B8" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#1E3352" />
                <RechartsRadar
                  name="Feasibility"
                  dataKey="value"
                  stroke="#19C7D9"
                  fill="#2878FF"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="p-4 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 space-y-1">
            <div className="font-bold text-white">Confidence Limitation Notice:</div>
            <div>
              Assessment reflects analytical modeling based on standard material tables and regional Bihar cost indices. Physical verification required.
            </div>
          </div>
        </div>

        {/* Sliders / Score Adjusters */}
        <div className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] space-y-4">
          <h3 className="text-base font-bold text-white font-heading">Vector Score Matrix</h3>

          <div className="space-y-3 text-xs">
            {Object.entries(scores).map(([key, val]) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between font-semibold">
                  <span className="capitalize text-gray-300">{key.replace(/([A-Z])/g, ' $1')} Feasibility</span>
                  <span className="text-[#19C7D9] font-mono">{val}%</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={val}
                  onChange={(e) => setScores({ ...scores, [key]: Number(e.target.value) })}
                  className="w-full accent-[#19C7D9] bg-[#071426]"
                />
              </div>
            ))}
          </div>

          <button
            onClick={() => alert('Feasibility evaluation locked and signed in research register.')}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md mt-4"
          >
            Save Feasibility Evaluation to Project Register
          </button>
        </div>
      </div>
    </div>
  );
}

