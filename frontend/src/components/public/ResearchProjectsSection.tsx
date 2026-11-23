'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { ResearchProject } from '@/types/bmir';
import { FolderGit2, Users, Target, Activity, CheckCircle, ArrowRight } from 'lucide-react';

export default function ResearchProjectsSection() {
  const { t, lang } = useApp();
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bmirApi.getResearchProjects().then((data) => {
      setProjects(data);
      setLoading(false);
    });
  }, []);

  return (
    <section id="projects" className="py-20 bg-[#080F1C] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>{t.nav.projects}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {lang === 'hi' ? 'सक्रिय बहुविषयक अनुसंधान परियोजनाएं' : 'Active Multidisciplinary Research Projects'}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? 'प्रायोगिक पद्धतियों, शोध प्रश्नों और सत्यापन प्रोटोकॉल के साथ संरचित परियोजनाएं।'
              : 'Structured research investigations with verified methodologies, objective hypotheses, and field trials.'}
          </p>
        </div>

        {/* Projects Cards */}
        {loading ? (
          <div className="py-12 text-center text-gray-400">Loading research projects...</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {projects.map((prj) => (
              <div
                key={prj.id}
                className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 sm:p-8 space-y-6 hover:border-blue-500/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 text-xs font-bold rounded-lg bg-[#102A43] text-[#19C7D9] border border-[#1E3352]">
                    {prj.domain}
                  </span>
                  <span className="text-xs font-mono text-gray-400">{prj.project_code}</span>
                  <span
                    className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                      prj.status === 'Active'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                    }`}
                  >
                    {prj.status}
                  </span>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white font-heading">{prj.title}</h3>
                  <p className="text-xs text-gray-300 leading-relaxed">{prj.objective}</p>
                </div>

                {/* Research Questions & Methodology */}
                <div className="space-y-3 bg-[#071426] p-4 rounded-xl border border-[#1E3352] text-xs">
                  <div>
                    <span className="font-bold text-[#19C7D9] uppercase text-[10px] tracking-wider block mb-1">
                      Core Research Question:
                    </span>
                    <p className="text-gray-300 italic">{prj.research_questions}</p>
                  </div>
                  <div className="pt-2 border-t border-[#1E3352]">
                    <span className="font-bold text-[#2878FF] uppercase text-[10px] tracking-wider block mb-1">
                      Experimental Methodology:
                    </span>
                    <p className="text-gray-300">{prj.methodology}</p>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-gray-400">Investigation Progress</span>
                    <span className="text-[#19C7D9]">{prj.progress_pct}%</span>
                  </div>
                  <div className="w-full bg-[#102A43] h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-[#2878FF] to-[#19C7D9] h-full rounded-full transition-all duration-500"
                      style={{ width: `${prj.progress_pct}%` }}
                    />
                  </div>
                </div>

                {/* Team members */}
                <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-[#1E3352]">
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-[#19C7D9]" />
                    <span>
                      <strong>Lead:</strong> {prj.lead_researcher}
                    </span>
                  </div>
                  {prj.team_members && (
                    <div className="text-[11px] text-gray-400 truncate max-w-[200px]">
                      Team: {prj.team_members}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

