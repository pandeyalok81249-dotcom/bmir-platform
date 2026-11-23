'use client';

import React, { useState } from 'react';
import { CalendarDays, Plus, CheckCircle2, Clock, AlertTriangle, ArrowRight } from 'lucide-react';

export default function RoadmapGeneratorView() {
  const [phases, setPhases] = useState([
    {
      phase: 'Phase 1: Laboratory Analytical Benchmarking',
      duration: 'Months 1-3',
      milestones: ['Sensor spectral calibration', 'Thermal fluidic finite-element simulation'],
      deliverables: 'Sensor PCB schematics and baseline calibration report',
      risks: 'Signal drift under fluctuating humidity',
    },
    {
      phase: 'Phase 2: Scale Pilot Unit Fabrication',
      duration: 'Months 4-7',
      milestones: ['Machining of rotary conditioning chamber', 'Integration of automated airflow louvers'],
      deliverables: 'Operational pilot prototype ready for field trial',
      risks: 'Lead times on precision aluminum/carbon fiber components',
    },
    {
      phase: 'Phase 3: Multi-Centre Agricultural Trials',
      duration: 'Months 8-11',
      milestones: ['Farmer Producer Organization (FPO) batch trials', 'Aflatoxin inhibition quantification'],
      deliverables: 'Validated agronomic report co-signed by partner university',
      risks: 'Seasonal harvesting weather delays',
    },
    {
      phase: 'Phase 4: Technology Transfer & Commercial Licensing',
      duration: 'Month 12',
      milestones: ['Preparation of industrial patent licensing pack', 'Transfer to manufacturing partner'],
      deliverables: 'Commercial blueprint licenses and royalty agreements',
      risks: 'Regulatory BIS standard clearances',
    },
  ]);

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <CalendarDays className="w-3.5 h-3.5" />
          <span>Innovation Roadmap Generator</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Structured Phased Development & Commercialization Plan
        </h2>
        <p className="text-xs text-gray-400">
          Map inventions into milestone-driven engineering stages with risk matrices, required deliverables, and realistic timelines.
        </p>
      </div>

      {/* Roadmap Timeline Display */}
      <div className="space-y-6">
        {phases.map((p, idx) => (
          <div
            key={idx}
            className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] space-y-4 hover:border-cyan-500/40 transition-colors"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#1E3352]">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-xl bg-blue-500/20 text-[#19C7D9] font-bold flex items-center justify-center text-xs">
                  0{idx + 1}
                </div>
                <h3 className="text-base font-bold text-white font-heading">{p.phase}</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#102A43] text-gray-300 border border-[#1E3352]">
                {p.duration}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="space-y-1">
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Key Milestones:</span>
                <ul className="space-y-1 text-gray-300">
                  {p.milestones.map((m, i) => (
                    <li key={i} className="flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{m}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-[#19C7D9] uppercase tracking-wider">Deliverable:</span>
                <p className="text-gray-300">{p.deliverables}</p>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">Risk Mitigation:</span>
                <p className="text-gray-300">{p.risks}</p>
              </div>
            </div>
          </div>
        ))}

        <div className="pt-2 flex justify-end">
          <button
            onClick={() => alert('New roadmap phase added.')}
            className="px-5 py-2.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs font-semibold text-gray-200 border border-[#1E3352] flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Development Phase</span>
          </button>
        </div>
      </div>
    </div>
  );
}

