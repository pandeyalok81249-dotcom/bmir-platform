'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import { Compass, Lightbulb, UserCheck, ShieldAlert, CheckCircle2, Award, FileText } from 'lucide-react';

export default function AboutSection() {
  const { t, lang } = useApp();

  return (
    <section id="about" className="py-20 bg-[#080F1C] text-gray-200 border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <Compass className="w-3.5 h-3.5" />
            <span>{t.about.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.about.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {t.brand.tagline}
          </p>
        </div>

        {/* Vision & Mission Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-8 space-y-4 hover:border-blue-500/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-[#2878FF]">
              <Compass className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white font-heading">{t.about.visionTitle}</h3>
            <p className="text-sm text-gray-300 leading-relaxed">{t.about.visionText}</p>
          </div>

          <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-8 space-y-4 hover:border-cyan-500/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-[#19C7D9]">
              <Lightbulb className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white font-heading">{t.about.missionTitle}</h3>
            <p className="text-sm text-gray-300 leading-relaxed">{t.about.missionText}</p>
          </div>
        </div>

        {/* Founder Profile - Rigorously verified without false credentials */}
        <div className="bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] rounded-3xl p-8 sm:p-12 mb-16">
          <div className="flex flex-col lg:flex-row items-start gap-8">
            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center text-white text-3xl font-extrabold font-heading shrink-0 shadow-xl">
              BP
            </div>
            <div className="space-y-4 flex-1">
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-2xl font-bold text-white font-heading">{t.about.founderTitle}: {t.brand.founder}</h3>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Verified Independent Inventor
                </span>
              </div>
              <p className="text-sm text-gray-300 leading-relaxed">
                {t.about.founderBio}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs">
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  <div className="text-gray-400">Location</div>
                  <div className="font-semibold text-white mt-0.5">Bhagalpur, Bihar, India</div>
                </div>
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  <div className="text-gray-400">Published Patent Gazettes</div>
                  <div className="font-semibold text-[#19C7D9] mt-0.5">Issue 23/2026 & 24/2026</div>
                </div>
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  <div className="text-gray-400">Co-Inventorship</div>
                  <div className="font-semibold text-blue-400 mt-0.5">Dr. Shyam Sundar Mandal</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Innovation Methodology */}
        <div className="space-y-6 mb-16">
          <h3 className="text-2xl font-bold text-white font-heading text-center">
            {t.about.methodologyTitle}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Empirical Problem Formulation',
                desc: 'Identifies practical bottlenecks in high-humidity maize drying, lotus nut harvesting, and rural medical telemetry.',
              },
              {
                step: '02',
                title: 'Scientific Feasibility Modeling',
                desc: 'Evaluates thermodynamic limits, chemical reaction rates, and mechanical load limits prior to component procurement.',
              },
              {
                step: '03',
                title: 'Rigorous Physical Prototyping',
                desc: 'Fabricates test jigs, custom sensor boards, and mechanical assemblies with transparent failure logs.',
              },
              {
                step: '04',
                title: 'Institutional Validation & Review',
                desc: 'Submits prototypes to academic departments, accredited test laboratories, and peer-reviewed journals.',
              },
            ].map((m) => (
              <div key={m.step} className="bg-[#0D1829] border border-[#1E3352] p-6 rounded-2xl space-y-3">
                <div className="text-2xl font-extrabold text-[#19C7D9] font-heading">{m.step}</div>
                <h4 className="text-base font-bold text-white">{m.title}</h4>
                <p className="text-xs text-gray-400 leading-relaxed">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Strict Verification Disclaimer Box */}
        <div className="bg-[#121A2A] border-l-4 border-[#19C7D9] p-6 rounded-r-2xl flex items-start space-x-4">
          <ShieldAlert className="w-6 h-6 text-[#19C7D9] shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs text-gray-300 leading-relaxed">
            <div className="font-bold text-white uppercase tracking-wider">
              {lang === 'hi' ? 'सत्यापन एवं नीतिगत प्रकटीकरण' : 'Verification & Integrity Disclosure'}
            </div>
            <div>{t.about.disclaimerNotice}</div>
          </div>
        </div>
      </div>
    </section>
  );
}

