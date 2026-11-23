'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { ResearchProject, VerificationStatus } from '@/types/bmir';
import {
  FolderGit2,
  CheckCircle2,
  Clock,
  User,
  Users,
  Target,
  FileQuestion,
  FlaskConical,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export default function ResearchProjectsView() {
  const { setActiveView } = useApp();
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<ResearchProject | null>(null);

  useEffect(() => {
    bmirApi
      .getResearchProjects()
      .then((data) => {
        setProjects(data);
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
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>Active Initiatives</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            BMIR Research Projects
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Multidisciplinary R&D programmes undergoing laboratory characterization, field trials, and
            collaborative engineering investigation under the direction of Binod Pandey and research team.
          </p>
        </div>

        <button
          onClick={() => setActiveView('experiments')}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-md hover:opacity-95"
        >
          Experiment Manager
        </button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-xs">Loading research projects...</div>
      ) : projects.length === 0 ? (
        <div className="py-16 text-center bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-2">
          <ShieldAlert className="w-8 h-8 text-gray-500 mx-auto" />
          <h4 className="text-sm font-bold text-white">No Active Projects Recorded</h4>
          <p className="text-xs text-gray-400">
            There are currently no verified active research projects initialized in the database.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projects.map((p) => (
            <div
              key={p.id}
              className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-3xl p-6 space-y-5 transition-all shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-[#102A43] text-[#19C7D9] border border-blue-500/20">
                    {p.project_code}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>{p.status}</span>
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-xs text-[#19C7D9] font-medium mb-1">{p.domain}</div>
                  <h3 className="text-base font-bold text-white font-heading">{p.title}</h3>
                </div>

                <div className="space-y-2 text-xs text-gray-400">
                  <div className="flex items-start space-x-2">
                    <Target className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-gray-300">Objective:</span> {p.objective}
                    </div>
                  </div>

                  {p.research_questions && (
                    <div className="flex items-start space-x-2">
                      <FileQuestion className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-gray-300">Core Question:</span> {p.research_questions}
                      </div>
                    </div>
                  )}
                </div>

                {/* Progress bar */}
                <div className="space-y-1.5 pt-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400 font-medium">Research Milestone Progress</span>
                    <span className="font-bold text-white font-mono">{p.progress_pct}%</span>
                  </div>
                  <div className="w-full bg-[#071426] h-2 rounded-full overflow-hidden border border-[#1E3352]">
                    <div
                      className="bg-gradient-to-r from-[#2878FF] to-[#19C7D9] h-full rounded-full transition-all duration-500"
                      style={{ width: `${p.progress_pct}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Footer team details */}
              <div className="pt-4 border-t border-[#1E3352] flex items-center justify-between text-xs text-gray-400">
                <div className="flex items-center space-x-1.5">
                  <User className="w-3.5 h-3.5 text-gray-300" />
                  <span>Lead: <strong className="text-white">{p.lead_researcher}</strong></span>
                </div>
                {p.team_members && (
                  <div className="flex items-center space-x-1 text-[11px] text-gray-400">
                    <Users className="w-3.5 h-3.5" />
                    <span className="truncate max-w-[150px]">{p.team_members}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

