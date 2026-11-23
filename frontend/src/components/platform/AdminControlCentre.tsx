'use client';

import React, { useState, useEffect } from 'react';
import { bmirApi } from '@/lib/api';
import { User, CollaborationEnquiry } from '@/types/bmir';
import { Settings, Users, Handshake, Cpu, Shield, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function AdminControlCentre() {
  const [activeTab, setActiveTab] = useState<'users' | 'enquiries' | 'providers'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [enquiries, setEnquiries] = useState<CollaborationEnquiry[]>([]);
  const [providerStatus, setProviderStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const u = await bmirApi.getUsersList();
        setUsers(u);
      } else if (activeTab === 'enquiries') {
        const e = await bmirApi.getCollaborationEnquiries();
        setEnquiries(e);
      } else if (activeTab === 'providers') {
        const p = await bmirApi.getProviderStatus();
        setProviderStatus(p);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await bmirApi.updateUserRole(userId, newRole);
      loadData();
    } catch (err: any) {
      alert(`Role update failed: ${err.message}`);
    }
  };

  const handleEnquiryStatus = async (id: string, status: string) => {
    try {
      await bmirApi.updateEnquiryStatus(id, status, `Reviewed in Admin Control Centre`);
      loadData();
    } catch (err: any) {
      alert(`Status update failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <Settings className="w-3.5 h-3.5" />
          <span>Governance & Administration</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Admin Control Centre
        </h2>
        <p className="text-xs text-gray-400">
          Manage user permissions, review institutional collaboration proposals, and monitor AI provider gateways.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-[#1E3352] pb-3">
        {[
          { id: 'users', label: 'User Roles & Permissions', icon: Users },
          { id: 'enquiries', label: 'Collaboration Proposals', icon: Handshake },
          { id: 'providers', label: 'AI Provider Gateway Status', icon: Cpu },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white shadow'
                  : 'bg-[#0D1829] text-gray-300 hover:bg-[#102A43] border border-[#1E3352]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="py-12 text-center text-gray-400">Loading control data...</div>
      ) : activeTab === 'users' ? (
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-white font-heading">Registered Platform Users</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="text-[11px] text-gray-400 border-b border-[#1E3352] uppercase">
                <tr>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Organization</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Change Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E3352]">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-[#102A43]/40">
                    <td className="py-3 px-4 font-semibold text-white">
                      <div>{u.full_name}</div>
                      <div className="text-[11px] text-gray-400">{u.email}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/20 text-[#19C7D9]">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3 px-4">{u.organization || 'BMIR'}</td>
                    <td className="py-3 px-4">
                      <span className="text-emerald-400 font-semibold">Active</span>
                    </td>
                    <td className="py-3 px-4">
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="px-2 py-1 rounded-lg bg-[#071426] border border-[#1E3352] text-xs text-gray-200"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="external_collaborator">Collaborator</option>
                        <option value="research_engineer">Engineer</option>
                        <option value="research_scientist">Scientist</option>
                        <option value="research_admin">Admin</option>
                        <option value="founder">Founder</option>
                        <option value="super_admin">Super Admin</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'enquiries' ? (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-white font-heading">Incoming Institutional Enquiries</h3>
          {enquiries.map((enq) => (
            <div
              key={enq.id}
              className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3 text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-[#1E3352]">
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-[#19C7D9]">{enq.enquiry_number}</span>
                  <span className="text-gray-400">· {enq.organization}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                    {enq.pathway}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-0.5 rounded font-bold ${
                      enq.status === 'Approved'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : enq.status === 'Under Review'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-amber-500/20 text-amber-400'
                    }`}
                  >
                    {enq.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-gray-300">
                <div>
                  <strong>Contact:</strong> {enq.full_name} ({enq.email} | {enq.phone || 'N/A'})
                </div>
                <div>
                  <strong>Interest:</strong> {enq.project_interest || 'General'}
                </div>
              </div>

              <p className="text-gray-200 bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                {enq.message}
              </p>

              {/* Action Buttons */}
              <div className="flex space-x-2 pt-2">
                <button
                  onClick={() => handleEnquiryStatus(enq.id!, 'Under Review')}
                  className="px-3 py-1.5 rounded-lg bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 text-xs font-semibold"
                >
                  Mark Under Review
                </button>
                <button
                  onClick={() => handleEnquiryStatus(enq.id!, 'Approved')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 text-xs font-semibold"
                >
                  Approve for Meeting
                </button>
                <button
                  onClick={() => handleEnquiryStatus(enq.id!, 'Declined')}
                  className="px-3 py-1.5 rounded-lg bg-rose-600/30 hover:bg-rose-600/50 text-rose-300 text-xs font-semibold"
                >
                  Decline
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] space-y-6">
          <h3 className="text-sm font-bold text-white font-heading">AI Model Gateways & Telemetry</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {Object.entries(providerStatus?.providers || {}).map(([key, p]: [string, any]) => (
              <div key={key} className="p-4 rounded-xl bg-[#071426] border border-[#1E3352] space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white uppercase text-[11px]">{key.replace('_', ' ')}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      p.configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                    }`}
                  >
                    {p.configured ? 'Active' : 'Unconfigured'}
                  </span>
                </div>
                <div className="text-gray-400">Default Model: {p.default_model}</div>
                <div className="text-[11px] text-gray-500">{p.status}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

