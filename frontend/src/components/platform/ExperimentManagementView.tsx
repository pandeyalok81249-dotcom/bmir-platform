'use client';

import React, { useState, useEffect } from 'react';
import { bmirApi } from '@/lib/api';
import { Experiment } from '@/types/bmir';
import { FlaskConical, Plus, CheckCircle2, Clock, Activity, FileText } from 'lucide-react';

export default function ExperimentManagementView() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);

  useEffect(() => {
    bmirApi.getExperiments().then((data) => {
      setExperiments(data);
      setLoading(false);
      if (data.length > 0) setSelectedExp(data[0]);
    });
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <FlaskConical className="w-3.5 h-3.5" />
          <span>Research Experiment Management</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Empirical Laboratory Logging, Hypotheses & Traceability
        </h2>
        <p className="text-xs text-gray-400">
          Document experimental hypotheses, materials, measurements, sensor observations, and quantitative error margins with immutable version history.
        </p>
      </div>

      {loading ? (
        <div className="py-12 text-center text-gray-400">Loading experimental records...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* List Column */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
              Recorded Experiments ({experiments.length})
            </h3>
            {experiments.map((exp) => (
              <div
                key={exp.id}
                onClick={() => setSelectedExp(exp)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                  selectedExp?.id === exp.id
                    ? 'bg-[#102A43] border-[#19C7D9] shadow-lg'
                    : 'bg-[#0D1829] border-[#1E3352] hover:border-blue-500/40'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] text-gray-400 mb-1">
                  <span>{exp.domain}</span>
                  <span className="font-mono">v{exp.version}</span>
                </div>
                <h4 className="text-xs font-bold text-white line-clamp-2">{exp.title}</h4>
                <div className="flex items-center justify-between pt-2 mt-2 border-t border-[#1E3352] text-[10px]">
                  <span
                    className={`px-2 py-0.5 rounded font-semibold ${
                      exp.status === 'Concluded'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-blue-500/20 text-blue-400'
                    }`}
                  >
                    {exp.status}
                  </span>
                  <span className="text-gray-400">{new Date(exp.created_at || '').toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Details Column */}
          <div className="lg:col-span-2">
            {selectedExp ? (
              <div className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-[#1E3352]">
                  <div>
                    <span className="text-[11px] font-mono text-[#19C7D9] font-bold">
                      {selectedExp.project_code || 'BMIR-PRJ-01'} · Version {selectedExp.version}
                    </span>
                    <h3 className="text-xl font-bold text-white font-heading mt-0.5">{selectedExp.title}</h3>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400">
                    {selectedExp.status}
                  </span>
                </div>

                <div className="space-y-4 text-xs">
                  <div>
                    <span className="font-bold text-[#19C7D9] uppercase text-[10px] tracking-wider block mb-1">
                      Objective
                    </span>
                    <p className="text-gray-300 leading-relaxed">{selectedExp.objective}</p>
                  </div>

                  <div>
                    <span className="font-bold text-[#2878FF] uppercase text-[10px] tracking-wider block mb-1">
                      Scientific Hypothesis
                    </span>
                    <p className="text-gray-300 italic leading-relaxed bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                      "{selectedExp.hypothesis}"
                    </p>
                  </div>

                  <div>
                    <span className="font-bold text-white uppercase text-[10px] tracking-wider block mb-1">
                      Methodology & Materials
                    </span>
                    <p className="text-gray-300 leading-relaxed">{selectedExp.methodology}</p>
                    {selectedExp.materials_used && (
                      <div className="mt-1 text-gray-400">
                        <strong>Materials:</strong> {selectedExp.materials_used}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                    <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1">
                      <span className="font-bold text-gray-400 uppercase text-[10px]">Measurements Recorded</span>
                      <p className="text-gray-300 text-[11px]">{selectedExp.measurements}</p>
                    </div>

                    <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1">
                      <span className="font-bold text-gray-400 uppercase text-[10px]">Sensor Observations</span>
                      <p className="text-gray-300 text-[11px]">{selectedExp.observations}</p>
                    </div>
                  </div>

                  {selectedExp.data_metrics && (
                    <div className="bg-[#102A43]/40 p-4 rounded-xl border border-[#1E3352] space-y-2">
                      <span className="font-bold text-[#19C7D9] uppercase text-[10px]">Quantitative Data Metrics</span>
                      <pre className="text-xs font-mono text-cyan-300">
                        {JSON.stringify(selectedExp.data_metrics, null, 2)}
                      </pre>
                    </div>
                  )}

                  <div className="pt-2 border-t border-[#1E3352] text-gray-400 text-[11px]">
                    <strong>Results Summary:</strong> {selectedExp.results_summary}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-20 text-center text-gray-500">Select an experiment to view full logs</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

