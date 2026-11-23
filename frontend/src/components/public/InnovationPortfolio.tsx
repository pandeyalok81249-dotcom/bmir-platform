'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Innovation } from '@/types/bmir';
import { Search, Filter, ShieldCheck, ArrowRight, X, AlertCircle, Cpu, ExternalLink } from 'lucide-react';

export default function InnovationPortfolio() {
  const { t, lang } = useApp();
  const [innovations, setInnovations] = useState<Innovation[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedStage, setSelectedStage] = useState('');
  const [selectedInnov, setSelectedInnov] = useState<Innovation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [search, selectedDomain, selectedStage]);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await bmirApi.getInnovations({
        q: search || undefined,
        domain: selectedDomain || undefined,
        stage: selectedStage || undefined,
      });
      setInnovations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const domains = [
    'Agriculture',
    'Healthcare',
    'Urban safety',
    'Railways',
    'Governance',
    'Water',
    'Export',
    'Defence',
    'Energy',
    'Research',
    'Rural development',
    'Education',
  ];

  const stages = [
    'Concept',
    'Research',
    'Feasibility',
    'Design',
    'Prototype',
    'Testing',
    'Validation',
    'Commercialization',
  ];

  return (
    <section id="portfolio" className="py-20 bg-[#071426] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-12">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <Cpu className="w-3.5 h-3.5" />
            <span>{t.portfolio.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.portfolio.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? '27 शोध अवधारणाएं और तकनीकी समाधान — पारदर्शी स्थिति प्रलेखन के साथ।'
              : '27 multidisciplinary innovations formulated by independent inventor Binod Pandey with verified IPO records.'}
          </p>
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-[#0B1A2E] p-4 sm:p-6 rounded-2xl border border-[#1E3352] mb-10 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t.portfolio.searchPlaceholder}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#2878FF]"
              />
            </div>

            {/* Domain Filter */}
            <div>
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-sm text-gray-300 focus:outline-none focus:border-[#2878FF]"
              >
                <option value="">{t.portfolio.allDomains}</option>
                {domains.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>

            {/* Stage Filter */}
            <div>
              <select
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-sm text-gray-300 focus:outline-none focus:border-[#2878FF]"
              >
                <option value="">{t.portfolio.allStages}</option>
                {stages.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-[#1E3352]">
            <div>
              Showing <span className="font-bold text-[#19C7D9]">{innovations.length}</span> of 27 innovations
            </div>
            {(search || selectedDomain || selectedStage) && (
              <button
                onClick={() => {
                  setSearch('');
                  setSelectedDomain('');
                  setSelectedStage('');
                }}
                className="text-xs text-blue-400 hover:underline"
              >
                Clear all filters
              </button>
            )}
          </div>
        </div>

        {/* Innovations Cards Grid */}
        {loading ? (
          <div className="py-16 text-center text-gray-400">Loading innovations database...</div>
        ) : innovations.length === 0 ? (
          <div className="py-16 text-center text-gray-400">
            No innovations match your query. Try resetting filters.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {innovations.map((inv) => {
              const isJournalPublished = ['202631048563', '202631058488', '202631065492'].includes(
                inv.patent_application_no || ''
              );

              return (
                <div
                  key={inv.id}
                  className="bg-[#0D1829] border border-[#1E3352] hover:border-blue-500/50 rounded-2xl p-6 flex flex-col justify-between transition-all hover:shadow-xl hover:shadow-blue-500/5 group"
                >
                  <div className="space-y-3">
                    {/* Header tags */}
                    <div className="flex items-center justify-between">
                      <span className="px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-md bg-[#102A43] text-[#19C7D9] border border-[#1E3352]">
                        {inv.domain}
                      </span>
                      <span className="text-[11px] font-mono text-gray-400">{inv.project_code}</span>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-bold text-white group-hover:text-[#19C7D9] transition-colors font-heading">
                      {lang === 'hi' && inv.title_hi ? inv.title_hi : inv.title}
                    </h3>

                    {/* Summary */}
                    <p className="text-xs text-gray-300 line-clamp-3 leading-relaxed">
                      {lang === 'hi' && inv.summary_hi ? inv.summary_hi : inv.summary}
                    </p>

                    {/* Stage & Patent badges */}
                    <div className="space-y-2 pt-2">
                      <div className="flex items-center space-x-2 text-xs">
                        <span className="text-gray-400">Stage:</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {inv.development_stage}
                        </span>
                      </div>

                      <div className="text-[11px] text-gray-400">
                        {inv.patent_application_no ? (
                          <span className="text-emerald-400 font-medium flex items-center space-x-1">
                            <ShieldCheck className="w-3.5 h-3.5 inline" />
                            <span>
                              {inv.patent_application_no} ({inv.patent_status})
                            </span>
                            {isJournalPublished && (
                              <span className="text-cyan-400 font-bold">· Journal Published</span>
                            )}
                          </span>
                        ) : (
                          <span className="text-gray-500">Unfiled Concept / Formal Filing Pending</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* CTA link */}
                  <div className="pt-5 mt-4 border-t border-[#1E3352]">
                    <button
                      onClick={() => setSelectedInnov(inv)}
                      className="w-full flex items-center justify-between text-xs font-semibold text-[#19C7D9] hover:text-white transition-colors"
                    >
                      <span>{t.portfolio.viewDetails}</span>
                      <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Innovation Detail Modal */}
        {selectedInnov && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
            <div className="relative bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-3xl w-full p-6 sm:p-8 space-y-6 max-h-[90vh] overflow-y-auto shadow-2xl">
              {/* Close Button */}
              <button
                onClick={() => setSelectedInnov(null)}
                className="absolute top-6 right-6 p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Modal Header */}
              <div className="space-y-2 pr-10">
                <div className="flex items-center space-x-3">
                  <span className="px-2.5 py-1 text-xs font-bold uppercase rounded bg-[#102A43] text-[#19C7D9]">
                    {selectedInnov.domain}
                  </span>
                  <span className="text-xs font-mono text-gray-400">{selectedInnov.project_code}</span>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded bg-blue-500/20 text-blue-400">
                    {selectedInnov.development_stage}
                  </span>
                </div>
                <h2 className="text-2xl font-extrabold text-white font-heading">
                  {lang === 'hi' && selectedInnov.title_hi ? selectedInnov.title_hi : selectedInnov.title}
                </h2>
                <p className="text-xs text-gray-300">
                  {lang === 'hi' && selectedInnov.summary_hi ? selectedInnov.summary_hi : selectedInnov.summary}
                </p>
              </div>

              {/* Verified Development Status Notice */}
              <div className="p-4 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 flex items-start space-x-3">
                <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-white">Status Classification: </span>
                  {selectedInnov.prototype_status}
                </div>
              </div>

              {/* Problem & Solution Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1.5">
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] text-[#19C7D9]">
                    {t.portfolio.problem}
                  </h4>
                  <p className="text-gray-300 leading-relaxed">
                    {lang === 'hi' && selectedInnov.problem_statement_hi
                      ? selectedInnov.problem_statement_hi
                      : selectedInnov.problem_statement}
                  </p>
                </div>

                <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1.5">
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] text-[#2878FF]">
                    {t.portfolio.solution}
                  </h4>
                  <p className="text-gray-300 leading-relaxed">
                    {lang === 'hi' && selectedInnov.proposed_solution_hi
                      ? selectedInnov.proposed_solution_hi
                      : selectedInnov.proposed_solution}
                  </p>
                </div>
              </div>

              {/* Validation & Collaboration */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1.5">
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] text-emerald-400">
                    {t.portfolio.validationNeeded}
                  </h4>
                  <p className="text-gray-300 leading-relaxed">
                    {lang === 'hi' && selectedInnov.validation_required_hi
                      ? selectedInnov.validation_required_hi
                      : selectedInnov.validation_required}
                  </p>
                </div>

                <div className="bg-[#071426] p-4 rounded-xl border border-[#1E3352] space-y-1.5">
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] text-purple-400">
                    {t.portfolio.collaborationSought}
                  </h4>
                  <p className="text-gray-300 leading-relaxed">
                    {lang === 'hi' && selectedInnov.collaboration_sought_hi
                      ? selectedInnov.collaboration_sought_hi
                      : selectedInnov.collaboration_sought}
                  </p>
                </div>
              </div>

              {/* Patent & Co-Inventors Information */}
              <div className="bg-[#102A43]/50 p-4 rounded-xl border border-[#1E3352] space-y-2 text-xs">
                <div className="font-bold text-white uppercase tracking-wider text-[11px]">
                  Intellectual Property & Co-Inventorship Record
                </div>
                <div className="text-gray-300">
                  <strong>Patent Status:</strong>{' '}
                  {selectedInnov.patent_application_no ? (
                    <span className="text-[#19C7D9] font-mono">
                      Application No. {selectedInnov.patent_application_no} ({selectedInnov.patent_status})
                    </span>
                  ) : (
                    'Unfiled Concept; Form 1 Pending'
                  )}
                </div>
                {selectedInnov.co_inventors && (
                  <div className="text-gray-300">
                    <strong>Co-Inventors:</strong> {selectedInnov.co_inventors}
                  </div>
                )}
                <div className="text-[11px] text-gray-400 italic">
                  Note: Publication or filing does NOT constitute a granted patent. Institutional validation is
                  actively welcomed.
                </div>
              </div>

              {/* Contact / Collaborate Action */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
                <a
                  href="#collaboration"
                  onClick={() => setSelectedInnov(null)}
                  className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md text-center"
                >
                  Request Technical Collaboration on this Project
                </a>
                <a
                  href="tel:+918340328914"
                  className="text-xs text-gray-400 hover:text-white"
                >
                  Direct Inquiry: +91 8340 328914
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

