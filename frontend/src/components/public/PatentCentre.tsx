'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { PatentRecord } from '@/types/bmir';
import { ShieldCheck, FileCheck, Search, AlertTriangle, ExternalLink, BookOpen, Clock } from 'lucide-react';

export default function PatentCentre() {
  const { t, lang } = useApp();
  const [patents, setPatents] = useState<PatentRecord[]>([]);
  const [filterType, setFilterType] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bmirApi
      .getPatentRecords({
        patent_type: filterType === 'all' ? undefined : filterType,
        q: search || undefined,
      })
      .then((data) => {
        setPatents(data);
        setLoading(false);
      });
  }, [filterType, search]);

  return (
    <section id="patents" className="py-20 bg-[#071426] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-12">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <FileCheck className="w-3.5 h-3.5" />
            <span>{t.patents.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.patents.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? 'भारतीय पेटेंट कार्यालय (IPO) के आधिकारिक राजपत्र प्रकाशन और आवेदन रिकॉर्ड।'
              : 'Verifiable documentation of patent application numbers, IPO journal gazette publications, and co-inventorship.'}
          </p>
        </div>

        {/* Essential Legal Grounding Disclaimer */}
        <div className="bg-[#0C1A2E] border-l-4 border-amber-400 p-6 rounded-r-2xl mb-12 flex items-start space-x-4 shadow-lg">
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs text-gray-300 leading-relaxed">
            <div className="font-bold text-white uppercase tracking-wider">
              {lang === 'hi' ? 'कानूनी प्रकटीकरण (LEGAL COMPLIANCE)' : 'LEGAL NOTICE & STATUTORY CLARIFICATION'}
            </div>
            <div>{t.patents.disclaimer}</div>
          </div>
        </div>

        {/* Tabs & Search */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-8">
          {/* Status Tabs */}
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'all', label: t.patents.allTab },
              { id: 'Published', label: t.patents.publishedTab },
              { id: 'Provisional', label: t.patents.provisionalTab },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilterType(tab.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${filterType === tab.id
                    ? 'bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white shadow-md'
                    : 'bg-[#102A43] text-gray-300 hover:bg-[#1E3352] border border-[#1E3352]'
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t.patents.searchPlaceholder}
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-[#0D1829] border border-[#1E3352] text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#2878FF]"
            />
          </div>
        </div>

        {/* Patents Cards List */}
        {loading ? (
          <div className="py-12 text-center text-gray-400">Loading intellectual property records...</div>
        ) : (
          <div className="space-y-4">
            {patents.map((p) => {
              const isPublished = p.patent_type === 'Published' || Boolean(p.journal_issue);

              return (
                <div
                  key={p.id}
                  className={`bg-[#0D1829] border rounded-2xl p-6 transition-all ${isPublished ? 'border-cyan-500/40 bg-gradient-to-r from-[#0D1829] to-[#0A1A2E]' : 'border-[#1E3352]'
                    }`}
                >
                  <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ${isPublished
                              ? 'bg-cyan-500/20 text-[#19C7D9] border border-cyan-500/40'
                              : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            }`}
                        >
                          {p.patent_type}
                        </span>
                        <span className="font-mono text-xs text-gray-400 font-semibold">
                          App: {p.application_number}
                        </span>
                        {p.provisional_application_number && (
                          <span className="text-[11px] text-gray-400">
                            (Provisional: {p.provisional_application_number})
                          </span>
                        )}
                      </div>

                      <h3 className="text-xl font-bold text-white font-heading">{p.title}</h3>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs text-gray-300">
                        <div>
                          <span className="text-gray-400">Lead Inventor: </span>
                          <span className="font-semibold text-white">{p.lead_inventor}</span>
                        </div>
                        {p.co_inventors && (
                          <div>
                            <span className="text-gray-400">Co-Inventor: </span>
                            <span className="font-semibold text-blue-400">{p.co_inventors}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-400">Jurisdiction: </span>
                          <span className="text-gray-300">{p.jurisdiction}</span>
                        </div>
                      </div>

                      {p.verification_notes && (
                        <p className="text-xs text-gray-400 pt-1 italic">
                          Documentation Evidence: {p.verification_notes}
                        </p>
                      )}
                    </div>

                    {/* Published Journal Reference Callout */}
                    {isPublished && (
                      <div className="bg-[#071426] border border-[#1E3352] p-4 rounded-xl text-xs space-y-1 min-w-[220px]">
                        <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
                          <BookOpen className="w-4 h-4" />
                          <span>IPO Journal Publication</span>
                        </div>
                        <div className="text-gray-300">
                          Date: <span className="font-semibold text-white">{p.publication_date || 'Published 2026'}</span>
                        </div>
                        {p.journal_issue && (
                          <div className="text-gray-400">
                            Ref: {p.journal_issue} · Page {p.journal_page || 'Gazette'}
                          </div>
                        )}
                        <div className="text-[10px] text-[#19C7D9] pt-1">
                          Official Gazette Record
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}

