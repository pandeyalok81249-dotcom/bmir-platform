'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import {
  Bell,
  CheckCircle2,
  Clock,
  Handshake,
  FileCheck,
  ShieldAlert,
  FolderGit2,
  BookOpen,
  Filter,
  Check,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';

export default function NotificationCentreView() {
  const { setActiveView } = useApp();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const loadNotifs = () => {
    setLoading(true);
    bmirApi
      .getNotifications(selectedCategory)
      .then((data) => {
        setNotifications(data.notifications || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    loadNotifs();
  }, [selectedCategory]);

  const handleMarkRead = async (id: string) => {
    try {
      await bmirApi.markNotificationRead(id);
      loadNotifs();
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await bmirApi.markAllNotificationsRead();
      loadNotifs();
    } catch {}
  };

  const categories = [
    { id: 'all', label: 'All Notifications' },
    { id: 'collaboration', label: 'Collaboration Enquiries' },
    { id: 'patent', label: 'Patent & IP Updates' },
    { id: 'security', label: 'Security & Telemetry' },
    { id: 'research', label: 'Research Updates' },
  ];

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'collaboration':
        return <Handshake className="w-4 h-4 text-amber-400" />;
      case 'patent':
        return <FileCheck className="w-4 h-4 text-emerald-400" />;
      case 'security':
        return <ShieldAlert className="w-4 h-4 text-red-400" />;
      case 'research':
        return <FolderGit2 className="w-4 h-4 text-[#19C7D9]" />;
      default:
        return <Bell className="w-4 h-4 text-[#2878FF]" />;
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <Bell className="w-3.5 h-3.5" />
            <span>Institutional Dispatch</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            Notification Centre
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Real-time telemetry and alerts for patent gazette releases, institutional collaboration
            enquiries, peer review reviews, and zero-trust security events.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={loadNotifs}
            className="p-2.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-gray-300 text-xs"
            title="Refresh"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleMarkAllRead}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-md hover:opacity-95 flex items-center space-x-1.5"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Mark All as Read</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#1E3352] pb-3">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCategory(c.id)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              selectedCategory === c.id
                ? 'bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white shadow-md'
                : 'bg-[#0D1829] text-gray-400 hover:text-white border border-[#1E3352]'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-xs">Loading institutional alerts...</div>
      ) : notifications.length === 0 ? (
        <div className="py-16 text-center bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <h4 className="text-sm font-bold text-white">All Caught Up</h4>
          <p className="text-xs text-gray-400">
            No unread notifications or pending events in this category.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                n.unread
                  ? 'bg-[#0D1829] border-blue-500/40 shadow-md'
                  : 'bg-[#071426]/70 border-[#1E3352] text-gray-400'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div className="w-9 h-9 rounded-xl bg-[#102A43] flex items-center justify-center shrink-0 mt-0.5">
                  {getCategoryIcon(n.category)}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white text-xs">{n.title}</span>
                    {n.unread && (
                      <span className="w-2 h-2 rounded-full bg-[#19C7D9] animate-pulse" />
                    )}
                  </div>

                  <p className="text-xs text-gray-300 leading-relaxed">{n.detail}</p>

                  <div className="text-[11px] text-gray-500 flex items-center space-x-2 pt-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(n.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2 shrink-0">
                {n.link_url && (
                  <button
                    onClick={() => setActiveView(n.link_url)}
                    className="px-3 py-1.5 rounded-lg bg-[#102A43] hover:bg-[#1E3352] text-[11px] text-[#19C7D9] font-medium flex items-center space-x-1"
                  >
                    <span>View</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
                {n.unread && (
                  <button
                    onClick={() => handleMarkRead(n.id)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#102A43]"
                    title="Mark as Read"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

