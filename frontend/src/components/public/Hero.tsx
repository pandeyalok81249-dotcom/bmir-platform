'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import { Sparkles, ArrowRight, ShieldCheck, Microscope, Cpu, Layers } from 'lucide-react';

export default function Hero() {
  const { t, lang, setActiveView, setIsAuthModalOpen, user } = useApp();

  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-[#071426] via-[#0A1A30] to-[#080F1C] text-white pt-24 pb-20 border-b border-[#1E3352]">
      {/* Background Animated Scientific Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] bg-gradient-to-tr from-blue-600/15 to-cyan-500/15 blur-[120px] pointer-events-none rounded-full" />
      <div className="absolute -top-10 -right-10 w-96 h-96 bg-[#2878FF]/10 blur-[100px] pointer-events-none rounded-full" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          {/* Eyebrow Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#102A43] border border-[#1E3352] text-xs font-semibold text-[#19C7D9] tracking-wider uppercase">
            <Microscope className="w-3.5 h-3.5" />
            <span>{t.hero.badge}</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight font-heading leading-tight text-white">
            {t.hero.headline}
          </h1>

          {/* Subheading */}
          <p className="text-base sm:text-lg text-gray-300 font-normal leading-relaxed max-w-2xl mx-auto">
            {t.hero.subheading}
          </p>

          {/* Founder line */}
          <div className="flex items-center justify-center space-x-3 text-xs sm:text-sm text-gray-400">
            <span className="font-semibold text-white">{t.brand.founder}</span>
            <span>·</span>
            <span>{t.brand.founderRole}</span>
            <span>·</span>
            <span className="text-[#19C7D9]">{t.brand.location}</span>
          </div>

          {/* Action CTAs */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => {
                if (user) {
                  setActiveView('dashboard');
                } else {
                  setIsAuthModalOpen(true);
                }
              }}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] hover:opacity-95 text-white font-bold text-sm tracking-wide shadow-lg shadow-blue-500/25 flex items-center justify-center space-x-2.5 transition-all transform hover:-translate-y-0.5"
            >
              <Sparkles className="w-4 h-4 text-white" />
              <span>{t.hero.enterLab}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <a
              href="#portfolio"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-gray-200 border border-[#1E3352] font-semibold text-sm tracking-wide transition-all text-center"
            >
              {t.hero.exploreInnovations}
            </a>

            <a
              href="#collaboration"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-transparent hover:bg-white/5 text-gray-300 font-medium text-sm transition-all text-center"
            >
              {t.hero.collaborate}
            </a>
          </div>
        </div>

        {/* Verified Impact & Records Grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          <div className="bg-[#0B1A2E]/80 backdrop-blur-sm border border-[#1E3352] rounded-2xl p-5 text-center hover:border-blue-500/40 transition-colors">
            <div className="text-3xl sm:text-4xl font-extrabold text-[#19C7D9] font-heading">27</div>
            <div className="mt-1 text-xs text-gray-300 font-medium">{t.hero.statProjects}</div>
            <div className="text-[10px] text-gray-400 mt-1">Multidisciplinary fields</div>
          </div>

          <div className="bg-[#0B1A2E]/80 backdrop-blur-sm border border-[#1E3352] rounded-2xl p-5 text-center hover:border-blue-500/40 transition-colors">
            <div className="text-3xl sm:text-4xl font-extrabold text-[#2878FF] font-heading">17</div>
            <div className="mt-1 text-xs text-gray-300 font-medium">{t.hero.statPatents}</div>
            <div className="text-[10px] text-gray-400 mt-1">Documented IPO records</div>
          </div>

          <div className="bg-[#0B1A2E]/80 backdrop-blur-sm border border-[#1E3352] rounded-2xl p-5 text-center hover:border-blue-500/40 transition-colors">
            <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-heading">3</div>
            <div className="mt-1 text-xs text-gray-300 font-medium">{t.hero.statJournal}</div>
            <div className="text-[10px] text-gray-400 mt-1">Official Gazette published</div>
          </div>

          <div className="bg-[#0B1A2E]/80 backdrop-blur-sm border border-[#1E3352] rounded-2xl p-5 text-center hover:border-blue-500/40 transition-colors">
            <div className="text-3xl sm:text-4xl font-extrabold text-amber-400 font-heading">15</div>
            <div className="mt-1 text-xs text-gray-300 font-medium">{t.hero.statFiled}</div>
            <div className="text-[10px] text-gray-400 mt-1">Application verified</div>
          </div>
        </div>

        {/* Honest Grounding Notice */}
        <div className="mt-8 text-center text-xs text-gray-400 flex items-center justify-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-[#19C7D9]" />
          <span>
            {lang === 'hi'
              ? 'सत्यापित साक्ष्य आधारित: सभी प्रलेख भारतीय पेटेंट कार्यालय के आधिकारिक अभिलेखों पर आधारित हैं।'
              : 'Evidence-grounded: All technical disclosures reflect documented Indian Patent Office application references.'}
          </span>
        </div>
      </div>
    </div>
  );
}

