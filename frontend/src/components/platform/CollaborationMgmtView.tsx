'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { CollaborationEnquiry } from '@/types/bmir';
import {
  Handshake,
  CheckCircle2,
  Clock,
  Building,
  Mail,
  Phone,
  MessageSquare,
  FileText,
  ShieldAlert,
  ArrowRight,
  Filter,
} from 'lucide-react';

export default function CollaborationMgmtView() {
  const { user } = useApp();
  const [enquiries, setEnquiries] = useState<CollaborationEnquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedEnquiry, setSelectedEnquiry] = useState<CollaborationEnquiry | null>(null);
  const [updating, setUpdating] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [internalNotes, setInternalNotes] = useState('');

  const loadEnquiries = () => {
    setLoading(true);
    bmirApi
      .getCollaborationEnquiries()
      .then((data) => {
        setEnquiries(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadEnquiries();
  }, []);

  const handleUpdateStatus = async () => {
    if (!selectedEnquiry || !selectedEnquiry.id) return;
    setUpdating(true);
    try {
      await bmirApi.updateEnquiryStatus(
        selectedEnquiry.id,
        newStatus || selectedEnquiry.status || 'Reviewed',
        internalNotes
      );
      setSelectedEnquiry(null);
      loadEnquiries();
    } catch (err) {
      alert('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const filtered = enquiries.filter(
    (e) => selectedStatus === 'All' || e.status === selectedStatus
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <Handshake className="w-3.5 h-3.5" />
            <span>Institutional Partnerships</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            Collaboration Management
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Review and govern institutional proposals submitted by universities, corporate R&D divisions,
            and engineering research laboratories worldwide.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-gray-300 focus:outline-none"
          >
            <option value="All">All Enquiries</option>
            <option value="Pending">Pending Review</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Enquiries List */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-xs">Loading collaboration enquiries...</div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-2">
          <ShieldAlert className="w-8 h-8 text-gray-500 mx-auto" />
          <h4 className="text-sm font-bold text-white">No Collaboration Enquiries Received</h4>
          <p className="text-xs text-gray-400">
            No institutional proposals or partnership requests match the current selection.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((enq) => (
            <div
              key={enq.id}
              onClick={() => {
                setSelectedEnquiry(enq);
                setNewStatus(enq.status || 'Under Review');
                setInternalNotes(enq.internal_notes || '');
              }}
              className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-2xl p-5 space-y-4 cursor-pointer transition-all shadow-md group"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                  {enq.enquiry_number || 'ENQ-NEW'}
                </span>
                <span
                  className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                    enq.status === 'Approved'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : enq.status === 'Under Review'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                  }`}
                >
                  {enq.status || 'Pending'}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-white group-hover:text-[#2878FF] transition-colors">
                  {enq.full_name}
                </h3>
                <div className="text-xs text-gray-400 flex items-center space-x-1.5 mt-0.5">
                  <Building className="w-3.5 h-3.5 text-[#19C7D9]" />
                  <span>{enq.organization} ({enq.organization_type})</span>
                </div>
              </div>

              <div className="text-xs text-gray-300 bg-[#071426] p-3 rounded-xl border border-[#1E3352] line-clamp-2">
                &ldquo;{enq.message}&rdquo;
              </div>

              <div className="flex items-center justify-between text-[11px] text-gray-400 pt-1">
                <span>Pathway: <strong className="text-gray-300">{enq.pathway}</strong></span>
                <span className="text-[#19C7D9] font-medium flex items-center space-x-1">
                  <span>Manage Review</span>
                  <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Review Modal */}
      {selectedEnquiry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-5 text-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1E3352] pb-4">
              <div>
                <div className="text-[10px] font-mono text-[#19C7D9] uppercase font-bold">
                  {selectedEnquiry.enquiry_number}
                </div>
                <h3 className="text-lg font-bold font-heading text-white">{selectedEnquiry.full_name}</h3>
                <div className="text-xs text-gray-400">{selectedEnquiry.organization}</div>
              </div>
              <button
                onClick={() => setSelectedEnquiry(null)}
                className="p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  <div className="text-gray-400">Email</div>
                  <div className="font-semibold text-white truncate">{selectedEnquiry.email}</div>
                </div>
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                  <div className="text-gray-400">Phone</div>
                  <div className="font-semibold text-white">{selectedEnquiry.phone || 'N/A'}</div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="text-gray-400 font-semibold">Institutional Proposal</div>
                <div className="bg-[#071426] p-3 rounded-xl border border-[#1E3352] text-gray-300 leading-relaxed max-h-40 overflow-y-auto">
                  {selectedEnquiry.message}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-gray-300 font-semibold">Update Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full px-3 py-2 bg-[#071426] border border-[#1E3352] rounded-xl text-white"
                >
                  <option value="Pending">Pending Review</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Approved">Approved for Technical Discussion</option>
                  <option value="Archived">Archived / Not Feasible</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-gray-300 font-semibold">Internal Review Notes</label>
                <textarea
                  rows={3}
                  value={internalNotes}
                  onChange={(e) => setInternalNotes(e.target.value)}
                  placeholder="Add evaluation findings, NDAs required, or technical committee remarks..."
                  className="w-full p-3 bg-[#071426] border border-[#1E3352] rounded-xl text-white"
                />
              </div>
            </div>

            <div className="pt-3 border-t border-[#1E3352] flex justify-end space-x-2">
              <button
                onClick={() => setSelectedEnquiry(null)}
                className="px-4 py-2 rounded-xl bg-[#102A43] text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateStatus}
                disabled={updating}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-md disabled:opacity-50"
              >
                {updating ? 'Saving...' : 'Save Decision'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

