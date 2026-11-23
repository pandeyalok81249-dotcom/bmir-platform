'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Innovation, VerificationStatus } from '@/types/bmir';
import {
  Sparkles,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  FileEdit,
  EyeOff,
  Archive,
  BookOpen,
  Cpu,
  Layers,
  ArrowRight,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react';

export default function InnovationPortfolioView() {
  const { lang, setActiveView } = useApp();
  const [innovations, setInnovations] = useState<Innovation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [selectedStage, setSelectedStage] = useState('All');
  const [selectedVerif, setSelectedVerif] = useState<string>('All');
  const [activeInnovation, setActiveInnovation] = useState<Innovation | null>(null);

  useEffect(() => {
    bmirApi
      .getInnovations()
      .then((data) => {
        setInnovations(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const domains = ['All', ...Array.from(new Set(innovations.map((i) => i.domain)))];
  const stages = ['All', 'Concept', 'Feasibility', 'Prototype', 'Testing', 'Validation'];
  const verifStatuses = ['All', 'Verified', 'Pending verification', 'Draft', 'Unpublished', 'Archived'];

  const filtered = innovations.filter((item) => {
    const matchesSearch =
      searchQuery === '' ||
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.project_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDomain = selectedDomain === 'All' || item.domain === selectedDomain;
    const matchesStage = selectedStage === 'All' || item.development_stage === selectedStage;
    const matchesVerif =
      selectedVerif === 'All' ||
      (selectedVerif === 'Verified' && item.verification_status === 'Verified') ||
      (selectedVerif === 'Pending verification' && item.verification_status === 'Pending verification') ||
      (selectedVerif === 'Draft' && item.verification_status === 'Draft') ||
      (selectedVerif === 'Unpublished' && item.verification_status === 'Unpublished') ||
      (selectedVerif === 'Archived' && item.verification_status === 'Archived');

    return matchesSearch && matchesDomain && matchesStage && matchesVerif;
  });

  const getVerifBadge = (status?: VerificationStatus) => {
    switch (status) {
      case 'Verified':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            <span>Verified Record</span>
          </span>
        );
      case 'Pending verification':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Clock className="w-3 h-3" />
            <span>Pending Verification</span>
          </span>
        );
      case 'Draft':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <FileEdit className="w-3 h-3" />
            <span>Draft Concept</span>
          </span>
        );
      case 'Unpublished':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">
            <EyeOff className="w-3 h-3" />
            <span>Unpublished / Confidential</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-500/10 text-gray-400 border border-gray-500/30">
            <Clock className="w-3 h-3" />
            <span>Under Review</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <Layers className="w-3.5 h-3.5" />
            <span>Institutional Registry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            BMIR Innovation Portfolio
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Complete database of multidisciplinary engineering initiatives. Each record maintains an
            explicit verification status backed by documented IPO gazette entries or laboratory evaluations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveView('discovery')}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-md hover:opacity-95"
          >
            Launch AI Discovery
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Search Box */}
          <div className="relative md:col-span-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search title, code, problem..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-white focus:outline-none focus:border-[#2878FF]"
            />
          </div>

          {/* Verification Status Filter */}
          <div>
            <select
              value={selectedVerif}
              onChange={(e) => setSelectedVerif(e.target.value)}
              className="w-full px-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
            >
              <option value="All">All Verification Statuses</option>
              <option value="Verified">Verified Only</option>
              <option value="Pending verification">Pending Verification</option>
              <option value="Draft">Draft Concepts</option>
              <option value="Unpublished">Unpublished</option>
              <option value="Archived">Archived</option>
            </select>
          </div>

          {/* Domain Filter */}
          <div>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-full px-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
            >
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d === 'All' ? 'All Domains' : d}
                </option>
              ))}
            </select>
          </div>

          {/* Stage Filter */}
          <div>
            <select
              value={selectedStage}
              onChange={(e) => setSelectedStage(e.target.value)}
              className="w-full px-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
            >
              {stages.map((s) => (
                <option key={s} value={s}>
                  {s === 'All' ? 'All Stages' : s}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Count Summary */}
        <div className="flex items-center justify-between text-[11px] text-gray-400 pt-1 border-t border-[#1E3352]/50">
          <div>
            Displaying <span className="font-bold text-white">{filtered.length}</span> of{' '}
            <span className="font-bold text-white">{innovations.length}</span> innovations
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-emerald-400">
              Verified: {innovations.filter((i) => i.verification_status === 'Verified').length}
            </span>
            <span className="text-amber-400">
              Pending: {innovations.filter((i) => i.verification_status === 'Pending verification').length}
            </span>
            <span className="text-blue-400">
              Draft: {innovations.filter((i) => i.verification_status === 'Draft').length}
            </span>
          </div>
        </div>
      </div>

      {/* Grid of Innovations */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-xs">Loading database records...</div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-2">
          <ShieldAlert className="w-8 h-8 text-gray-500 mx-auto" />
          <h4 className="text-sm font-bold text-white">No Innovation Records Found</h4>
          <p className="text-xs text-gray-400">
            No database records match the selected verification or domain filters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((inv) => (
            <div
              key={inv.id}
              onClick={() => setActiveInnovation(inv)}
              className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-2xl p-5 flex flex-col justify-between space-y-4 cursor-pointer transition-all hover:shadow-lg group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                    {inv.project_code}
                  </span>
                  {getVerifBadge(inv.verification_status)}
                </div>

                <div>
                  <div className="text-[11px] text-[#19C7D9] font-medium">{inv.domain}</div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#2878FF] transition-colors line-clamp-2">
                    {inv.title}
                  </h3>
                </div>

                <p className="text-xs text-gray-400 line-clamp-3 leading-relaxed">
                  {inv.summary}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1E3352] flex items-center justify-between text-[11px]">
                <div className="flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#19C7D9]" />
                  <span className="text-gray-300 font-medium">{inv.development_stage}</span>
                </div>
                <span className="text-[#19C7D9] font-semibold flex items-center space-x-1 group-hover:translate-x-1 transition-transform">
                  <span>Inspect</span>
                  <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Inspector for Selected Innovation */}
      {activeInnovation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-2xl w-full p-6 sm:p-8 space-y-5 max-h-[90vh] overflow-y-auto text-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1E3352] pb-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                    {activeInnovation.project_code}
                  </span>
                  {getVerifBadge(activeInnovation.verification_status)}
                </div>
                <h2 className="text-xl font-bold font-heading text-white">{activeInnovation.title}</h2>
                <div className="text-xs text-[#19C7D9]">{activeInnovation.domain}</div>
              </div>
              <button
                onClick={() => setActiveInnovation(null)}
                className="p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <div className="font-semibold text-gray-300">Problem Statement</div>
                <p className="text-gray-400 leading-relaxed bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  {activeInnovation.problem_statement}
                </p>
              </div>

              <div className="space-y-1">
                <div className="font-semibold text-gray-300">Proposed Solution & Mechanism</div>
                <p className="text-gray-400 leading-relaxed bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  {activeInnovation.proposed_solution}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352] space-y-1">
                  <div className="text-gray-400">Development Stage</div>
                  <div className="font-bold text-white">{activeInnovation.development_stage}</div>
                </div>
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352] space-y-1">
                  <div className="text-gray-400">Prototype Status</div>
                  <div className="font-semibold text-gray-300">{activeInnovation.prototype_status}</div>
                </div>
              </div>

              {activeInnovation.patent_application_no && (
                <div className="bg-[#071426] p-3 rounded-xl border border-blue-500/30 space-y-1">
                  <div className="text-blue-400 font-semibold">IPO Patent Filing Reference</div>
                  <div className="text-white font-mono font-bold">
                    Application #{activeInnovation.patent_application_no}
                  </div>
                  <div className="text-[11px] text-gray-400">
                    Status: {activeInnovation.patent_status}
                  </div>
                </div>
              )}

              {activeInnovation.validation_required && (
                <div className="space-y-1">
                  <div className="font-semibold text-gray-300">Required Scientific Validation</div>
                  <p className="text-gray-400 bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                    {activeInnovation.validation_required}
                  </p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#1E3352] flex justify-end">
              <button
                onClick={() => setActiveInnovation(null)}
                className="px-4 py-2 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

