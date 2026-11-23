'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import { LogOut, AlertTriangle, X } from 'lucide-react';

export default function LogoutModal() {
  const { logoutModalOpen, setLogoutModalOpen, confirmLogout, user } = useApp();

  if (!logoutModalOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-sm w-full p-6 space-y-5 text-white shadow-2xl">
        <button
          onClick={() => setLogoutModalOpen(false)}
          className="absolute top-5 right-5 p-1.5 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
          <LogOut className="w-6 h-6" />
        </div>

        <div className="space-y-1.5">
          <h3 className="text-lg font-bold font-heading text-white">Sign Out of BMIR Workspace?</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Your server session will be terminated and credentials securely invalidated. Any ongoing unsaved
            simulations or chat drafts will be saved to your local project ledger.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs space-y-0.5">
          <div className="text-gray-400">Signed in as:</div>
          <div className="font-bold text-white truncate">{user?.full_name || 'Binod Pandey'}</div>
          <div className="text-[11px] text-[#19C7D9]">{user?.email}</div>
        </div>

        <div className="flex items-center space-x-3 pt-2">
          <button
            onClick={() => setLogoutModalOpen(false)}
            className="flex-1 py-2.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs font-semibold text-gray-300 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={confirmLogout}
            className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:opacity-95 text-xs font-bold text-white shadow-md transition-all"
          >
            Confirm Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}

