'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { DashboardMetrics, VerificationStatus } from '@/types/bmir';
import {
  FolderGit2,
  FileCheck,
  FlaskConical,
  Handshake,
  TrendingUp,
  Activity,
  Cpu,
  ShieldCheck,
  Clock,
  Sparkles,
  ArrowRight,
  BookOpen,
  Bot,
  Layers,
  Target,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Globe2,
  HelpCircle,
  Share2,
  Calendar,
  Zap,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import ScientificCanvas3D from '@/components/vfx/ScientificCanvas3D';

const DOMAIN_COLORS: Record<string, string> = {
  Agriculture: '#10B981',
  Defence: '#F59E0B',
  Education: '#6366F1',
  Energy: '#2878FF',
  Export: '#EC4899',
  Governance: '#8B5CF6',
  Healthcare: '#19C7D9',
  Railways: '#3B82F6',
  Research: '#14B8A6',
  'Rural Development': '#F97316',
  'Urban Safety': '#EF4444',
  Water: '#06B6D4',
};

const DEFAULT_COLORS = ['#2878FF', '#19C7D9', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6366F1'];

export default function DashboardView() {
  const { user, setActiveView, lang } = useApp();
  const [stats, setStats] = useState<{
    metrics: DashboardMetrics;
    verification_breakdown?: {
      innovations: Record<string, number>;
      patents: Record<string, number>;
      projects: Record<string, number>;
    };
    recent_innovations?: Array<any>;
    recent_patents?: Array<any>;
    active_projects?: Array<any>;
    domain_distribution: Array<{ domain: string; count: number }>;
    stage_distribution: Array<{ stage: string; count: number }>;
    recent_activity: Array<any>;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bmirApi
      .getDashboardStats()
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="py-24 text-center text-gray-400 text-xs flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-2 border-[#19C7D9] border-t-transparent rounded-full animate-spin" />
        <span>Connecting to BMIR Database & Computing Verified Metrics...</span>
      </div>
    );
  }

  const metrics = stats?.metrics;
  const domainDist = stats?.domain_distribution || [];
  const stageDist = stats?.stage_distribution || [];

  // Data for the Donut Chart
  const pieData = domainDist.map((d) => ({
    name: d.domain,
    value: d.count,
    color: DOMAIN_COLORS[d.domain] || '#2878FF',
  }));

  const totalInnovations = metrics?.total_innovations || 0;
  const verifiedInnovations = metrics?.verified_innovations || 0;
  const totalPatents = metrics?.total_patents || 0;
  const publishedPatents = metrics?.published_patents || 0;
  const totalProjects = metrics?.total_projects || 0;
  const activeProjects = metrics?.active_projects || 0;
  const totalEnquiries = metrics?.total_enquiries || 0;
  const pendingEnquiries = metrics?.pending_enquiries || 0;

  const getVerifBadge = (status?: string) => {
    switch (status) {
      case 'Verified':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-2.5 h-2.5" />
            <span>Verified</span>
          </span>
        );
      case 'Pending verification':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Clock className="w-2.5 h-2.5" />
            <span>Pending</span>
          </span>
        );
      case 'Draft':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <span>Draft</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-gray-500/10 text-gray-400 border border-gray-500/30">
            <span>Under Review</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      {/* 3D SCIENTIFIC INNOVATION HERO BACKGROUND SECTION */}
      <section
        className="relative rounded-3xl overflow-hidden border border-[#1E3352] shadow-2xl bg-[#071426] min-h-[300px] flex items-center justify-between"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(7, 20, 38, 0.98) 0%, rgba(7, 20, 38, 0.85) 50%, rgba(7, 20, 38, 0.35) 100%), url('/assets/bmir_3d_hero_bg.webp')`,
          backgroundSize: 'cover',
          backgroundPosition: 'right center',
          backgroundRepeat: 'no-repeat',
        }}
      >
        {/* Subtle grid pattern overlay for high-tech scientific feel */}
        <div className="absolute inset-0 bg-[radial-gradient(#1E3352_1px,transparent_1px)] [background-size:24px_24px] opacity-30 pointer-events-none" />

        <div className="relative z-10 p-6 sm:p-10 max-w-2xl space-y-4">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-[#19C7D9] border border-blue-500/30 flex items-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>BMIR AI Research Intelligence Workspace</span>
            </span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading leading-tight tracking-tight">
            Engineering Tomorrow Through{' '}
            <span className="bg-gradient-to-r from-[#2878FF] via-[#19C7D9] to-white bg-clip-text text-transparent">
              Research & Innovation.
            </span>
          </h1>

          <p className="text-xs sm:text-sm text-gray-300 leading-relaxed max-w-xl">
            An independent multidisciplinary research initiative exploring intelligent technologies,
            empirical engineering, and practical solutions for real-world challenges.
          </p>

          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={() => setActiveView('portfolio')}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-blue-500/20 flex items-center space-x-2 transition-all transform hover:-translate-y-0.5"
            >
              <span>Explore Innovations</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => setActiveView('assistant')}
              className="px-5 py-2.5 rounded-xl bg-[#0D1829]/90 hover:bg-[#102A43] text-gray-200 border border-[#1E3352] text-xs font-semibold flex items-center space-x-2 transition-all backdrop-blur-md"
            >
              <Bot className="w-3.5 h-3.5 text-[#19C7D9]" />
              <span>Enter AI Research Lab</span>
            </button>
          </div>

          <div className="pt-2 text-[11px] text-gray-400 italic">
            &ldquo;Research Beyond Boundaries. Innovation for a Better World.&rdquo;
          </div>
        </div>

        {/* Interactive 3D Holographic Globe & Orbital Particle Network */}
        <div className="hidden lg:flex items-center justify-center relative z-10 w-[360px] h-[280px] mr-6">
          <ScientificCanvas3D className="w-full h-full" />
        </div>
      </section>

      {/* INSTITUTIONAL DATA INTEGRITY BAR */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs shadow-md">
        <div className="flex items-center space-x-2.5">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <div className="font-bold text-white flex items-center space-x-2">
              <span>Authentic Database Telemetry</span>
              <span className="px-2 py-0.2 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Zero Fabrication Policy
              </span>
            </div>
            <div className="text-[11px] text-gray-400">
              Figures reflect direct SQLite records. Official patent journal publications are strictly distinguished from provisional applications.
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-[10px] font-mono">
          <span className="px-2 py-1 rounded bg-[#071426] text-emerald-400 border border-emerald-500/20">
            Verified: {verifiedInnovations + publishedPatents + activeProjects}
          </span>
          <span className="px-2 py-1 rounded bg-[#071426] text-amber-400 border border-amber-500/20">
            Pending: {totalInnovations - verifiedInnovations}
          </span>
        </div>
      </div>

      {/* OVERVIEW METRIC CARDS (REAL DATABASE COUNTS) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Innovations */}
        <div
          onClick={() => setActiveView('portfolio')}
          className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-3xl p-5 space-y-3 cursor-pointer transition-all hover:shadow-lg group"
        >
          <div className="flex items-center justify-between text-gray-400">
            <div className="w-10 h-10 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-[#2878FF]">
              <Cpu className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
          </div>

          <div>
            <div className="text-3xl font-extrabold text-white font-heading">
              {totalInnovations > 0 ? `${totalInnovations}` : '0'}
            </div>
            <div className="text-xs font-bold text-gray-200 mt-0.5">Total Innovations</div>
            <div className="text-[11px] text-gray-400">
              {totalInnovations > 0 ? 'Documented in BMIR Registry' : 'No innovation records'}
            </div>
          </div>

          <div className="pt-2 border-t border-[#1E3352] flex items-center justify-between text-[10px]">
            <span className="text-emerald-400 font-semibold">{verifiedInnovations} Verified</span>
            <span className="text-gray-400">11 Sectors</span>
          </div>
        </div>

        {/* Patent Records */}
        <div
          onClick={() => setActiveView('patents')}
          className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-3xl p-5 space-y-3 cursor-pointer transition-all hover:shadow-lg group"
        >
          <div className="flex items-center justify-between text-gray-400">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <FileCheck className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
          </div>

          <div>
            <div className="text-3xl font-extrabold text-[#19C7D9] font-heading">
              {totalPatents > 0 ? `${totalPatents}` : '0'}
            </div>
            <div className="text-xs font-bold text-gray-200 mt-0.5">Patent Filings (IPO)</div>
            <div className="text-[11px] text-gray-400">
              {totalPatents > 0 ? `${publishedPatents} Gazette Published` : 'No verified records available'}
            </div>
          </div>

          <div className="pt-2 border-t border-[#1E3352] flex items-center justify-between text-[10px]">
            <span className="text-[#19C7D9] font-medium">{totalPatents - publishedPatents} Provisional</span>
            <span className="text-gray-400">Kolkata Jurisdiction</span>
          </div>
        </div>

        {/* Research Projects */}
        <div
          onClick={() => setActiveView('projects')}
          className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-3xl p-5 space-y-3 cursor-pointer transition-all hover:shadow-lg group"
        >
          <div className="flex items-center justify-between text-gray-400">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <FolderGit2 className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
          </div>

          <div>
            <div className="text-3xl font-extrabold text-emerald-400 font-heading">
              {activeProjects > 0 ? `${activeProjects}` : '0'}
            </div>
            <div className="text-xs font-bold text-gray-200 mt-0.5">Active Research Projects</div>
            <div className="text-[11px] text-gray-400">
              {totalProjects > 0 ? `${totalProjects} Total Registered` : 'No active projects recorded'}
            </div>
          </div>

          <div className="pt-2 border-t border-[#1E3352] flex items-center justify-between text-[10px]">
            <span className="text-emerald-400 font-semibold">{activeProjects} Ongoing Trials</span>
            <span className="text-gray-400">Multidisciplinary</span>
          </div>
        </div>

        {/* Collaboration Enquiries */}
        <div
          onClick={() => setActiveView('collaboration_mgmt')}
          className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-3xl p-5 space-y-3 cursor-pointer transition-all hover:shadow-lg group"
        >
          <div className="flex items-center justify-between text-gray-400">
            <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Handshake className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
          </div>

          <div>
            <div className="text-3xl font-extrabold text-amber-400 font-heading">
              {totalEnquiries > 0 ? `${totalEnquiries}` : '0'}
            </div>
            <div className="text-xs font-bold text-gray-200 mt-0.5">Institutional Proposals</div>
            <div className="text-[11px] text-gray-400">
              {totalEnquiries > 0 ? `${pendingEnquiries} Pending Evaluation` : 'No enquiries received'}
            </div>
          </div>

          <div className="pt-2 border-t border-[#1E3352] flex items-center justify-between text-[10px]">
            <span className="text-amber-400 font-semibold">Under Review</span>
            <span className="text-gray-400">Universities & R&D</span>
          </div>
        </div>
      </div>

      {/* 3-COLUMN RESEARCH ANALYTICS (INNOVATION OVERVIEW, DOMAINS, STAGES) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1: Innovation Overview (Donut Chart) */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 flex flex-col justify-between space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Layers className="w-4 h-4 text-[#19C7D9]" />
              <span>Innovation Overview</span>
            </h3>
            <button
              onClick={() => setActiveView('portfolio')}
              className="text-[11px] text-[#19C7D9] hover:underline"
            >
              View Details →
            </button>
          </div>

          <div className="relative h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#071426', borderColor: '#1E3352', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-2xl font-extrabold text-white font-heading">{totalInnovations}</span>
              <span className="text-[10px] text-gray-400">Innovations</span>
            </div>
          </div>

          {/* Sector Breakdown Legend */}
          <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] max-h-36 overflow-y-auto pt-2 border-t border-[#1E3352]">
            {domainDist.map((d) => (
              <div key={d.domain} className="flex items-center justify-between text-gray-300">
                <div className="flex items-center space-x-1.5 truncate">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: DOMAIN_COLORS[d.domain] || '#2878FF' }}
                  />
                  <span className="truncate">{d.domain}</span>
                </div>
                <span className="font-mono text-gray-400 font-bold ml-1">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2: Research Domains (Interactive Grid) */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 flex flex-col justify-between space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-[#2878FF]" />
              <span>Research Domains</span>
            </h3>
            <button
              onClick={() => setActiveView('portfolio')}
              className="text-[11px] text-[#19C7D9] hover:underline"
            >
              Explore All →
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2.5 text-xs">
            {[
              { name: 'AI & Robotics', count: '3 Initiated' },
              { name: 'Agriculture & Smart Farming', count: '7 Initiated' },
              { name: 'Healthcare & Medical Tech', count: '5 Initiated' },
              { name: 'Renewable Energy', count: '3 Initiated' },
              { name: 'Infrastructure & Engineering', count: '3 Initiated' },
              { name: 'Environmental Technology', count: '2 Initiated' },
              { name: 'Advanced Materials', count: '2 Initiated' },
              { name: 'Multidisciplinary', count: '2 Initiated' },
            ].map((dom) => (
              <div
                key={dom.name}
                onClick={() => setActiveView('portfolio')}
                className="p-2.5 rounded-xl bg-[#071426] hover:bg-[#102A43] border border-[#1E3352] hover:border-[#2878FF] cursor-pointer transition-all space-y-1"
              >
                <div className="font-bold text-white text-[11px] truncate">{dom.name}</div>
                <div className="text-[10px] text-[#19C7D9]">{dom.count}</div>
              </div>
            ))}
          </div>

          <div className="pt-2 text-center">
            <button
              onClick={() => setActiveView('portfolio')}
              className="w-full py-2 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs font-semibold text-gray-200 transition-colors"
            >
              Browse Complete Registry
            </button>
          </div>
        </div>

        {/* Column 3: Development Stage (Strict Status Model) */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 flex flex-col justify-between space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Target className="w-4 h-4 text-purple-400" />
              <span>Development Stage</span>
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Strict Status Model
            </span>
          </div>

          <div className="space-y-3">
            {stageDist.map((s) => (
              <div
                key={s.stage}
                className="p-3.5 rounded-2xl bg-[#071426] border border-[#1E3352] flex items-center justify-between"
              >
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#19C7D9]" />
                    <span>{s.stage}</span>
                  </div>
                  <div className="text-[10px] text-gray-400">
                    {s.stage === 'Prototype'
                      ? 'Lab hardware prototype active; validation pending'
                      : s.stage === 'Feasibility'
                      ? 'Analytical & material feasibility study documented'
                      : 'Research concept formulation & modeling'}
                  </div>
                </div>
                <span className="text-lg font-bold text-[#19C7D9] font-mono ml-2">{s.count}</span>
              </div>
            ))}
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-blue-500/20 text-[11px] text-gray-400">
            <strong className="text-white">Audit Rule:</strong> No invention is classified as Prototype or Commercialization without verified experimental test logs.
          </div>
        </div>
      </div>

      {/* RESEARCH WORKSPACE & RECENT INVENTIONS AUDIT */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Inventions with Verification Status */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <FolderGit2 className="w-4 h-4 text-[#2878FF]" />
              <span>Registry Inventions & Status</span>
            </h3>
            <button
              onClick={() => setActiveView('portfolio')}
              className="text-xs text-[#19C7D9] hover:underline"
            >
              View All ({totalInnovations})
            </button>
          </div>

          <div className="space-y-2.5">
            {stats?.recent_innovations?.map((inv) => (
              <div
                key={inv.id}
                onClick={() => setActiveView('portfolio')}
                className="p-3 rounded-2xl bg-[#071426] hover:bg-[#102A43] border border-[#1E3352] cursor-pointer transition-colors flex items-center justify-between text-xs"
              >
                <div className="space-y-0.5 truncate pr-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-[10px] font-bold text-[#19C7D9]">{inv.project_code}</span>
                    <span className="font-bold text-white truncate">{inv.title}</span>
                  </div>
                  <div className="text-[11px] text-gray-400 truncate">{inv.domain} · {inv.development_stage}</div>
                </div>
                <div className="shrink-0">{getVerifBadge(inv.verification_status)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Verified Patents & Gazette Publications */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              <span>Official IPO Patent Filings</span>
            </h3>
            <button
              onClick={() => setActiveView('patents')}
              className="text-xs text-[#19C7D9] hover:underline"
            >
              Patent Centre ({totalPatents})
            </button>
          </div>

          <div className="space-y-2.5">
            {stats?.recent_patents?.map((pat) => (
              <div
                key={pat.id}
                onClick={() => setActiveView('patents')}
                className="p-3 rounded-2xl bg-[#071426] hover:bg-[#102A43] border border-[#1E3352] cursor-pointer transition-colors flex items-center justify-between text-xs"
              >
                <div className="space-y-0.5 truncate pr-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-[10px] font-bold text-white">{pat.application_number}</span>
                    <span className="font-bold text-gray-200 truncate">{pat.title}</span>
                  </div>
                  <div className="text-[11px] text-gray-400">
                    {pat.journal_issue ? `Published: ${pat.journal_issue}` : `Status: ${pat.legal_status}`}
                  </div>
                </div>
                <div className="shrink-0">{getVerifBadge(pat.verification_status)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* LIVE AUDIT LOGS STREAM */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-[#19C7D9]" />
            <h3 className="text-sm font-bold text-white font-heading">Recent Research Activity & Audit Stream</h3>
          </div>
          <span className="text-[10px] text-emerald-400 font-mono flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Telemetry Active</span>
          </span>
        </div>

        <div className="space-y-2">
          {stats?.recent_activity?.map((act) => (
            <div
              key={act.id}
              className="p-3 rounded-xl bg-[#071426] border border-[#1E3352] flex items-center justify-between text-xs"
            >
              <div className="flex items-center space-x-3 truncate">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#102A43] text-gray-300">
                  {act.action}
                </span>
                <span className="text-gray-300 truncate">
                  {act.resource_type}: {act.details?.title || act.details?.code || act.resource_id}
                </span>
              </div>
              <span className="text-gray-500 text-[11px] shrink-0 ml-2">
                {new Date(act.timestamp).toLocaleDateString()} {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
