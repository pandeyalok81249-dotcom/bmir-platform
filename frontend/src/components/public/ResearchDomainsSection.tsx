'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import {
  BrainCircuit,
  Sprout,
  HeartPulse,
  Train,
  Shield,
  Droplets,
  Layers,
  Bot,
  Zap,
  Globe2,
  Atom,
} from 'lucide-react';

export default function ResearchDomainsSection() {
  const { t, lang } = useApp();

  const domainList = [
    {
      name: 'Artificial Intelligence',
      icon: BrainCircuit,
      color: 'from-blue-500 to-cyan-400',
      description: 'Multi-model reasoning architectures, computer vision for agricultural diagnostics, acoustic biomarker analysis, and RAG architectures.',
    },
    {
      name: 'Agriculture & Smart Farming',
      icon: Sprout,
      color: 'from-emerald-500 to-teal-400',
      description: 'Intelligent high-efficiency grain drying systems, automated maize cob harvesting, aquatic makhana wetland rovers, and hybrid seed technologies.',
    },
    {
      name: 'Healthcare & Medical Technology',
      icon: HeartPulse,
      color: 'from-rose-500 to-pink-400',
      description: 'Acoustic pulmonary diagnostics (AI-SHRUTI), non-invasive oxytocin sensors, mosquito vectors control, and multi-cancer early screening concepts.',
    },
    {
      name: 'Infrastructure & Civil Engineering',
      icon: Train,
      color: 'from-amber-500 to-orange-400',
      description: 'Enclosed bulk freight wagon safety (BHF-WAGON), automated rail track inspection, and rural infrastructure technologies.',
    },
    {
      name: 'Renewable Energy',
      icon: Zap,
      color: 'from-yellow-400 to-amber-500',
      description: 'Alkaline green hydrogen production systems, composite high-pressure storage cylinders, and clean ethanol vapor cooking.',
    },
    {
      name: 'Environmental Technology',
      icon: Droplets,
      color: 'from-cyan-500 to-blue-500',
      description: 'Hydrological evidence systems (Jal Sakshya), water quality telemetry, agricultural runoff filtration, and waste heat recovery.',
    },
    {
      name: 'Robotics & Automation',
      icon: Bot,
      color: 'from-indigo-500 to-purple-500',
      description: 'Amphibious wetland rovers for gorgon nut harvesting, agricultural drone crop sentinels, and mechatronic separation systems.',
    },
    {
      name: 'Advanced Materials',
      icon: Layers,
      color: 'from-purple-500 to-pink-500',
      description: 'Filament-wound carbon composite pressure vessels, thermal insulation barriers for drying chambers, and biodegradable agricultural mulches.',
    },
    {
      name: 'Defence & Public Safety',
      icon: Shield,
      color: 'from-red-500 to-orange-500',
      description: 'Integrated border surveillance architectures (RASHTRAKAVACH, PBDS v4.0), and multi-spectral urban surveillance networks (PRAHARI).',
    },
    {
      name: 'Social Impact Technologies',
      icon: Globe2,
      color: 'from-teal-500 to-emerald-500',
      description: 'Rural livelihood enhancement technologies, decentralized artisan agro-processing tools, and transparent civic land record validation (BHULEKH-DRISHTI).',
    },
    {
      name: 'Multidisciplinary Engineering',
      icon: Atom,
      color: 'from-blue-600 to-indigo-600',
      description: 'Cross-cutting physical-chemical systems integrating mechanical thermodynamics, embedded IoT sensors, and mathematical optimization.',
    },
  ];

  return (
    <section id="domains" className="py-20 bg-[#080F1C] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <Atom className="w-3.5 h-3.5" />
            <span>{t.domains.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.domains.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? '11 प्रमुख तकनीकी क्षेत्र जहां BMIR अनुसंधान एवं प्रोटोटाइप विकास संचालित करता है।'
              : 'Eleven core engineering and research divisions where BMIR actively conducts investigations and prototype development.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {domainList.map((d) => {
            const Icon = d.icon;
            return (
              <div
                key={d.name}
                className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-6 space-y-4 hover:border-blue-500/40 transition-colors flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${d.color} p-0.5 flex items-center justify-center shadow-lg`}
                  >
                    <div className="w-full h-full bg-[#0D1829] rounded-[10px] flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-white font-heading">{d.name}</h3>
                  <p className="text-xs text-gray-300 leading-relaxed">{d.description}</p>
                </div>

                <div className="pt-3 border-t border-[#1E3352]">
                  <a
                    href="#portfolio"
                    className="text-xs font-semibold text-[#19C7D9] hover:underline flex items-center space-x-1"
                  >
                    <span>Explore projects in this sector</span>
                    <span>→</span>
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

