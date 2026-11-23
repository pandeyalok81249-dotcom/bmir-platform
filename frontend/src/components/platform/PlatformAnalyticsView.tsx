'use client';

import React, { useState, useEffect } from 'react';
import { bmirApi } from '@/lib/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import {
  BarChart3,
  PieChart as PieIcon,
  ShieldCheck,
  TrendingUp,
  FileCheck,
  Cpu,
  Layers,
} from 'lucide-react';

const COLORS = ['#2878FF', '#19C7D9', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6366F1', '#14B8A6'];

export default function PlatformAnalyticsView() {
  const [stats, setStats] = useState<any>(null);
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
    return <div className="py-20 text-center text-gray-400 text-xs">Computing database analytics...</div>;
  }

  const domainData = stats?.domain_distribution || [];
  const stageData = stats?.stage_distribution || [];
  const verifData = [
    { name: 'Verified', value: stats?.metrics?.verified_innovations || 0, color: '#10B981' },
    { name: 'Pending Verification', value: stats?.metrics?.pending_innovations || 0, color: '#F59E0B' },
    { name: 'Draft Concepts', value: stats?.metrics?.draft_innovations || 0, color: '#2878FF' },
  ].filter((d) => d.value > 0);

  const patentVerifData = [
    { name: 'Official Gazette Published', value: stats?.metrics?.published_patents || 0, color: '#10B981' },
    { name: 'Provisional Filed', value: stats?.metrics?.provisional_patents || 0, color: '#2878FF' },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Telemetry & Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            BMIR Research Analytics
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Live database analytics charting innovation distribution, verification levels, and stage
            maturity across all 11 scientific domains.
          </p>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-gray-400">Total Innovation Records</div>
          <div className="text-3xl font-extrabold text-white font-heading">
            {stats?.metrics?.total_innovations || 0}
          </div>
          <div className="text-[11px] text-emerald-400">
            {stats?.metrics?.verified_innovations || 0} Verified in Registry
          </div>
        </div>

        <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-gray-400">Patent Records</div>
          <div className="text-3xl font-extrabold text-[#2878FF] font-heading">
            {stats?.metrics?.total_patents || 0}
          </div>
          <div className="text-[11px] text-[#19C7D9]">
            {stats?.metrics?.published_patents || 0} Gazette Published
          </div>
        </div>

        <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-gray-400">Research Projects</div>
          <div className="text-3xl font-extrabold text-emerald-400 font-heading">
            {stats?.metrics?.total_projects || 0}
          </div>
          <div className="text-[11px] text-gray-400">
            {stats?.metrics?.active_projects || 0} Active Laboratory Studies
          </div>
        </div>

        <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-gray-400">Knowledge Documents</div>
          <div className="text-3xl font-extrabold text-purple-400 font-heading">
            {stats?.metrics?.total_documents || 0}
          </div>
          <div className="text-[11px] text-gray-400">Indexed for Semantic RAG</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Domain Distribution */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-[#19C7D9]" />
              <span>Innovations by Research Domain</span>
            </h3>
            <span className="text-xs text-gray-400">{domainData.length} Sectors</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={domainData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" stroke="#64748b" textAnchor="end" fontSize={11} />
                <YAxis dataKey="domain" type="category" stroke="#94a3b8" fontSize={10} width={100} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#071426', borderColor: '#1E3352', borderRadius: '12px' }}
                />
                <Bar dataKey="count" fill="#2878FF" radius={[0, 6, 6, 0]}>
                  {domainData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Development Stage Distribution */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Layers className="w-4 h-4 text-[#2878FF]" />
              <span>Development Stage Maturity</span>
            </h3>
            <span className="text-xs text-blue-400">Strict Status Model</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="count"
                  nameKey="stage"
                  label={({ stage, count }) => `${stage}: ${count}`}
                >
                  {stageData.map((_, index) => (
                    <Cell key={`pie-stage-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#071426', borderColor: '#1E3352', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Verification Status Breakdown */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Data Verification Breakdown</span>
            </h3>
            <span className="text-xs text-emerald-400">Evidence Policy</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={verifData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                  nameKey="name"
                >
                  {verifData.map((entry, index) => (
                    <Cell key={`verif-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#071426', borderColor: '#1E3352', borderRadius: '12px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Patent Legal Classification Breakdown */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <FileCheck className="w-4 h-4 text-[#19C7D9]" />
              <span>Patent Filing Classifications</span>
            </h3>
            <span className="text-xs text-gray-400">IPO Records</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={patentVerifData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                  nameKey="name"
                >
                  {patentVerifData.map((entry, index) => (
                    <Cell key={`pverif-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#071426', borderColor: '#1E3352', borderRadius: '12px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

