'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import {
  User as UserIcon,
  Mail,
  Building,
  Phone,
  BookOpen,
  FolderGit2,
  FileCheck,
  ShieldCheck,
  CheckCircle2,
  Save,
  Sun,
  Moon,
  Bell,
  Sparkles,
  Camera,
  Layers,
  Award,
} from 'lucide-react';

export default function ProfileManagementView() {
  const { user, setUser, theme, toggleTheme, setActiveView } = useApp();
  const [fullName, setFullName] = useState(user?.full_name || 'Binod Pandey');
  const [designation, setDesignation] = useState(user?.designation || 'Founder & Independent Inventor');
  const [organization, setOrganization] = useState(user?.organization || 'Bharat Multisector Innovation & Research (BMIR)');
  const [bio, setBio] = useState(
    user?.bio ||
      'Independent inventor and founder of Bharat Multisector Innovation & Research (BMIR). Leading multidisciplinary engineering investigations across smart agriculture, clean hydrogen containment, and community acoustic diagnostic instruments.'
  );
  const [phone, setPhone] = useState(user?.phone || '+91 8340 328914');
  const [researchInterests, setResearchInterests] = useState(
    user?.research_interests ||
      'Smart Farming Automation, Composite Hydrogen Storage, Acoustic Medical Biomarkers, Wetland Mechatronics'
  );
  const [emailNotifs, setEmailNotifs] = useState(true);
  const [digestFreq, setDigestFreq] = useState('daily');
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Calculate actual profile completion percentage based on real fields
  const fields = [fullName, designation, organization, bio, phone, researchInterests, user?.email];
  const filledFields = fields.filter((f) => f && f.trim().length > 0).length;
  const completionPct = Math.round((filledFields / fields.length) * 100);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    try {
      const res = await bmirApi.updateProfile({
        full_name: fullName,
        designation,
        organization,
        bio,
        phone,
        research_interests: researchInterests,
        preferences: {
          theme,
          email_notifications: emailNotifs,
          digest_frequency: digestFreq,
        },
      });
      setUser(res.user);
      setSuccessMsg('Profile and preferences updated successfully.');
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err: any) {
      alert(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Header */}
      <div className="bg-[#0C1A2E] dark:bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center text-white text-2xl font-extrabold shadow-lg">
              {fullName ? fullName.charAt(0) : 'B'}
            </div>
            <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-[#071426] flex items-center justify-center">
              <CheckCircle2 className="w-3 h-3 text-white" />
            </div>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-extrabold text-white font-heading">{fullName}</h1>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-[#19C7D9] border border-blue-500/20">
                {user?.role.replace('_', ' ') || 'Founder'}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              {organization} · Location: Bhagalpur, Bihar, India
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="bg-[#071426] border border-[#1E3352] px-3.5 py-2 rounded-2xl text-right">
            <div className="text-[10px] text-gray-400 uppercase font-semibold">Profile Integrity</div>
            <div className="text-sm font-bold text-emerald-400 font-mono">{completionPct}% Complete</div>
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Identity & Contact Details */}
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
            <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
              <UserIcon className="w-4 h-4 text-[#19C7D9]" />
              <span>Researcher Identification</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-300 font-semibold mb-1">Full Legal Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Official Designation</label>
                <input
                  type="text"
                  required
                  value={designation}
                  onChange={(e) => setDesignation(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Institution / Research Organization</label>
                <input
                  type="text"
                  required
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Direct Phone Contact</label>
                <div className="relative">
                  <Phone className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full pl-9 pr-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-400 font-semibold mb-1">Institutional Email (Verified)</label>
                <div className="relative">
                  <Mail className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    disabled
                    value={user?.email || 'binod.pandey@bmirresearch.in'}
                    className="w-full pl-9 pr-3.5 py-2.5 bg-[#071426]/50 border border-[#1E3352] rounded-xl text-gray-400 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Research Biography & Interests */}
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md flex flex-col justify-between">
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-[#2878FF]" />
                <span>Biography & Research Scope</span>
              </h3>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Professional Research Biography</label>
                  <textarea
                    rows={4}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    className="w-full p-3.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF] leading-relaxed"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Core Research Interests (Comma-separated)</label>
                  <input
                    type="text"
                    value={researchInterests}
                    onChange={(e) => setResearchInterests(e.target.value)}
                    placeholder="e.g. Smart Agriculture, Renewable Energy, Acoustic Sensors"
                    className="w-full px-3.5 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-white focus:outline-none focus:border-[#2878FF]"
                  />
                </div>
              </div>
            </div>

            {/* Quick Link to Verified Records */}
            <div className="pt-4 border-t border-[#1E3352] flex items-center justify-between text-xs">
              <span className="text-gray-400">Associated IP & Projects</span>
              <button
                type="button"
                onClick={() => setActiveView('portfolio')}
                className="text-[#19C7D9] font-semibold hover:underline flex items-center space-x-1"
              >
                <span>View 27 Innovations</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </div>

        {/* Account Preferences Card */}
        <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-6 space-y-4 shadow-md">
          <h3 className="text-sm font-bold text-white font-heading flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>Workspace Preferences</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-[#071426] border border-[#1E3352] space-y-2">
              <div className="font-semibold text-gray-300 flex items-center justify-between">
                <span>Display Theme</span>
                <button
                  type="button"
                  onClick={toggleTheme}
                  className="p-1.5 rounded-lg bg-[#102A43] text-[#19C7D9]"
                >
                  {theme === 'dark' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
                </button>
              </div>
              <div className="text-[11px] text-gray-400">
                Current: <strong className="text-white capitalize">{theme} Mode</strong>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#071426] border border-[#1E3352] space-y-2">
              <div className="font-semibold text-gray-300">Email Notifications</div>
              <label className="flex items-center space-x-2 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={emailNotifs}
                  onChange={(e) => setEmailNotifs(e.target.checked)}
                  className="rounded border-[#1E3352] text-[#2878FF] focus:ring-0"
                />
                <span className="text-[11px] text-gray-300">Receive collaboration alert emails</span>
              </label>
            </div>

            <div className="p-4 rounded-2xl bg-[#071426] border border-[#1E3352] space-y-2">
              <div className="font-semibold text-gray-300">Research Digest</div>
              <select
                value={digestFreq}
                onChange={(e) => setDigestFreq(e.target.value)}
                className="w-full px-2 py-1 bg-[#102A43] border border-[#1E3352] rounded-lg text-white"
              >
                <option value="daily">Daily Summary</option>
                <option value="weekly">Weekly Gazette Digest</option>
                <option value="never">Mute Digests</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end space-x-3 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-lg shadow-blue-500/20 hover:opacity-95 flex items-center space-x-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving Profile...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}

