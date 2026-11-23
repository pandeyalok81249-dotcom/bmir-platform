'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Handshake, CheckCircle2, Building, Send, Shield, FileText, ArrowRight } from 'lucide-react';

export default function CollaborationPortal() {
  const { t, lang } = useApp();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    organization: '',
    organization_type: 'University',
    pathway: 'Research Collaboration',
    project_interest: 'Intelligent Maize Dryer & Conditioning System',
    message: '',
    proposal_summary: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [submittedNumber, setSubmittedNumber] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    try {
      const res = await bmirApi.submitCollaborationEnquiry(formData);
      setSubmittedNumber(res.enquiry_number);
    } catch (err: any) {
      setErrorMsg(err.message || 'Submission failed. Please check network.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="collaboration" className="py-20 bg-[#071426] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <Handshake className="w-3.5 h-3.5" />
            <span>{t.collaboration.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.collaboration.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? 'विश्वविद्यालयों, प्रयोगशालाओं, उद्योगों और कॉर्पोरेट अनुसंधान केंद्रों के लिए समर्पित साझेदारी मार्ग।'
              : 'Structured institutional engagement pathways for universities, testing laboratories, and corporate R&D.'}
          </p>
        </div>

        {/* Pathways Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="bg-[#0D1829] border border-[#1E3352] p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-[#2878FF] font-bold">
              01
            </div>
            <h4 className="text-base font-bold text-white font-heading">Academic & University Research</h4>
            <p className="text-xs text-gray-300 leading-relaxed">
              Joint research grant proposals, laboratory testing of agricultural and acoustic sensor prototypes, and student master thesis partnerships.
            </p>
          </div>

          <div className="bg-[#0D1829] border border-[#1E3352] p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-[#19C7D9] font-bold">
              02
            </div>
            <h4 className="text-base font-bold text-white font-heading">Prototype & Field Validation</h4>
            <p className="text-xs text-gray-300 leading-relaxed">
              Collaborative multi-centre pilot trials with agricultural FPOs, clinical evaluation of diagnostic models, and pressure testing facilities.
            </p>
          </div>

          <div className="bg-[#0D1829] border border-[#1E3352] p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 font-bold">
              03
            </div>
            <h4 className="text-base font-bold text-white font-heading">Technology Licensing & Transfer</h4>
            <p className="text-xs text-gray-300 leading-relaxed">
              Structured licensing of verified patent specifications, commercial manufacturing blueprints, and joint IP development agreements.
            </p>
          </div>
        </div>

        {/* Interactive Proposal Form */}
        <div className="bg-gradient-to-b from-[#0D1829] to-[#0A1626] border border-[#1E3352] rounded-3xl p-8 sm:p-12 max-w-4xl mx-auto shadow-2xl">
          {submittedNumber ? (
            <div className="text-center py-10 space-y-5">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto text-emerald-400">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-white font-heading">
                {lang === 'hi' ? 'सहयोग प्रस्ताव सफलतापूर्वक दर्ज किया गया' : 'Collaboration Proposal Submitted Successfully'}
              </h3>
              <p className="text-sm text-gray-300 max-w-xl mx-auto">
                {lang === 'hi'
                  ? 'आपका प्रस्ताव BMIR समीक्षा समिति को अग्रेषित कर दिया गया है। आपका संदर्भ कोड नीचे दिया गया है:'
                  : 'Your proposal has been routed to the BMIR Research Coordination Committee. Keep your reference code for all communications:'}
              </p>
              <div className="inline-block px-6 py-3 rounded-xl bg-[#071426] border border-[#19C7D9]/40 text-[#19C7D9] font-mono text-xl font-bold">
                {submittedNumber}
              </div>
              <div className="pt-4">
                <button
                  onClick={() => setSubmittedNumber(null)}
                  className="px-6 py-2.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs font-semibold text-gray-200"
                >
                  Submit Another Enquiry
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-white font-heading">{t.collaboration.formTitle}</h3>
                <p className="text-xs text-gray-400">
                  Submissions are confidential and encrypted in transit to protect preliminary research alignments.
                </p>
              </div>

              {errorMsg && (
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400">
                  {errorMsg}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.name} *</label>
                  <input
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. Dr. Anand Verma"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.email} *</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. anand.verma@university.ac.in"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.phone}</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="+91 98765 43210"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.org} *</label>
                  <input
                    type="text"
                    required
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. Indian Institute of Technology"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.orgType}</label>
                  <select
                    value={formData.organization_type}
                    onChange={(e) => setFormData({ ...formData, organization_type: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
                  >
                    <option value="University">University / Academic Institution</option>
                    <option value="Research Lab">Accredited Testing & Research Lab</option>
                    <option value="Corporate R&D">Corporate R&D Division</option>
                    <option value="Technology Company">Technology Startup / Enterprise</option>
                    <option value="Investor / Incubator">Technology Incubator / Impact Investor</option>
                    <option value="Independent Researcher">Independent Scientist / Engineer</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.pathway}</label>
                  <select
                    value={formData.pathway}
                    onChange={(e) => setFormData({ ...formData, pathway: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-300 focus:outline-none focus:border-[#2878FF]"
                  >
                    <option value="Research Collaboration">Joint Research Collaboration</option>
                    <option value="Prototype Development">Prototype Development & Testing</option>
                    <option value="Technical Review">Peer Technical Review & Validation</option>
                    <option value="Licensing">Patent Licensing & Technology Transfer</option>
                    <option value="Funding">Research Grant / Development Funding</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.projectInterest}</label>
                <input
                  type="text"
                  value={formData.project_interest}
                  onChange={(e) => setFormData({ ...formData, project_interest: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                  placeholder="e.g. Intelligent Maize Dryer, Green Hydrogen Cylinder, AI-SHRUTI"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">{t.collaboration.message} *</label>
                <textarea
                  required
                  rows={4}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
                  placeholder="Describe your research interests, proposed technical scope, and expected outcomes..."
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] hover:opacity-95 text-white font-bold text-xs tracking-wide shadow-lg shadow-blue-500/25 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? 'Transmitting Proposal...' : t.collaboration.submitBtn}</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}

