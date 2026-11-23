'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import {
  Shield,
  Key,
  Smartphone,
  Laptop,
  Lock,
  LogOut,
  AlertTriangle,
  CheckCircle2,
  Trash2,
  Clock,
  MapPin,
  RefreshCw,
  Cpu,
  Layers,
} from 'lucide-react';

export default function AccountSecurityView() {
  const { user, refreshUser, logout } = useApp();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);

  // Change Password state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdMsg, setPwdMsg] = useState({ text: '', isError: false });
  const [pwdLoading, setPwdLoading] = useState(false);

  // MFA state
  const [mfaEnabled, setMfaEnabled] = useState(user?.mfa_enabled || false);
  const [mfaLoading, setMfaLoading] = useState(false);
  const [mfaMsg, setMfaMsg] = useState('');

  const loadSessions = () => {
    setLoadingSessions(true);
    bmirApi
      .getActiveSessions()
      .then((data) => {
        setSessions(data.sessions || []);
        setLoadingSessions(false);
      })
      .catch(() => setLoadingSessions(false));
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdMsg({ text: '', isError: false });
    if (newPassword !== confirmPassword) {
      setPwdMsg({ text: 'New passwords do not match.', isError: true });
      return;
    }
    if (newPassword.length < 8) {
      setPwdMsg({ text: 'Password must be at least 8 characters.', isError: true });
      return;
    }
    setPwdLoading(true);
    try {
      await bmirApi.changePassword(oldPassword, newPassword);
      setPwdMsg({ text: 'Password changed successfully.', isError: false });
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPwdMsg({ text: err.message || 'Failed to change password', isError: true });
    } finally {
      setPwdLoading(false);
    }
  };

  const handleToggleMfa = async () => {
    setMfaLoading(true);
    setMfaMsg('');
    try {
      const res = await bmirApi.toggleMfa(!mfaEnabled);
      setMfaEnabled(res.mfa_enabled);
      setMfaMsg(res.message);
      refreshUser();
    } catch (err: any) {
      alert(err.message || 'MFA update failed');
    } finally {
      setMfaLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await bmirApi.revokeSession(sessionId);
      loadSessions();
    } catch (err) {
      alert('Failed to revoke session');
    }
  };

  const handleRevokeAll = async () => {
    if (!confirm('Are you sure you want to terminate all other active client sessions?')) return;
    try {
      await bmirApi.logoutAllSessions();
      alert('All sessions invalidated. Please sign in again.');
      logout();
    } catch (err) {
      alert('Failed to terminate sessions');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <Shield className="w-3.5 h-3.5" />
            <span>Identity & Access Governance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            Account Security Centre
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Protect intellectual property assets with multi-factor authentication, enterprise session
            governance, and strict credential lifecycle management.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Change Password Form */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
          <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
            <Key className="w-4 h-4 text-[#2878FF]" />
            <span>Update Account Password</span>
          </h3>

          {pwdMsg.text && (
            <div
              className={`p-3 rounded-xl text-xs flex items-center space-x-2 ${
                pwdMsg.isError
                  ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                  : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
              }`}
            >
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{pwdMsg.text}</span>
            </div>
          )}

          <form onSubmit={handleChangePassword} className="space-y-3 text-xs">
            <div>
              <label className="block text-gray-300 font-semibold mb-1">Current Password</label>
              <input
                type="password"
                required
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
              />
            </div>

            <div>
              <label className="block text-gray-300 font-semibold mb-1">New Password (min 8 chars)</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
              />
            </div>

            <div>
              <label className="block text-gray-300 font-semibold mb-1">Confirm New Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
              />
            </div>

            <button
              type="submit"
              disabled={pwdLoading}
              className="w-full py-2.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-white text-xs font-bold border border-[#1E3352] transition-colors disabled:opacity-50"
            >
              {pwdLoading ? 'Validating...' : 'Update Password'}
            </button>
          </form>
        </div>

        {/* Multi-Factor Authentication (MFA) */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <Smartphone className="w-4 h-4 text-purple-400" />
              <span>Multi-Factor Authentication (MFA)</span>
            </h3>

            <p className="text-xs text-gray-400 leading-relaxed">
              Require an additional verification factor (TOTP authenticator app or hardware token) before
              accessing sensitive unpublished invention disclosures and trade secrets.
            </p>

            <div className="p-4 rounded-2xl bg-[#071426] border border-[#1E3352] flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-white">Two-Factor Authentication</div>
                <div className="text-[11px] text-gray-400">
                  Status: {mfaEnabled ? <strong className="text-emerald-400">Enabled</strong> : 'Disabled'}
                </div>
              </div>

              <button
                type="button"
                onClick={handleToggleMfa}
                disabled={mfaLoading}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors ${
                  mfaEnabled
                    ? 'bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20'
                }`}
              >
                {mfaLoading ? 'Updating...' : mfaEnabled ? 'Disable MFA' : 'Enable MFA'}
              </button>
            </div>

            {mfaMsg && <div className="text-xs text-emerald-400">{mfaMsg}</div>}
          </div>

          <div className="p-3 rounded-xl bg-[#071426] border border-blue-500/20 text-[11px] text-gray-400">
            <strong className="text-white">Security Policy:</strong> All administrative accounts with
            patent documentation privileges are mandated to enforce multi-factor authentication.
          </div>
        </div>
      </div>

      {/* Active Sessions & Device Management */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Laptop className="w-4 h-4 text-[#19C7D9]" />
            <h3 className="text-sm font-bold text-white font-heading">
              Active Authorized Sessions & Device Fleet
            </h3>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={loadSessions}
              className="p-1.5 rounded-lg bg-[#102A43] hover:bg-[#1E3352] text-gray-300 text-xs"
              title="Refresh Sessions"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleRevokeAll}
              className="px-3 py-1.5 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 text-xs font-bold transition-colors"
            >
              Terminate All Other Sessions
            </button>
          </div>
        </div>

        <div className="space-y-3 text-xs">
          {loadingSessions ? (
            <div className="py-6 text-center text-gray-500">Loading session telemetry...</div>
          ) : sessions.length === 0 ? (
            <div className="py-6 text-center text-gray-500">No active external sessions recorded</div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                className="p-3.5 rounded-2xl bg-[#071426] border border-[#1E3352] flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-xl bg-[#102A43] flex items-center justify-center text-[#19C7D9]">
                    <Laptop className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-bold text-white flex items-center space-x-2">
                      <span>{s.device_name}</span>
                      {s.is_current && (
                        <span className="text-[9px] font-bold px-2 py-0.2 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          Current Device
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-gray-400 flex items-center space-x-2 mt-0.5">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-gray-500" />
                        <span>{s.location}</span>
                      </span>
                      <span>·</span>
                      <span>IP: {s.ip_address}</span>
                    </div>
                  </div>
                </div>

                {!s.is_current && (
                  <button
                    onClick={() => handleRevokeSession(s.id)}
                    className="p-2 rounded-xl text-gray-400 hover:text-red-400 bg-[#102A43]"
                    title="Revoke Session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

