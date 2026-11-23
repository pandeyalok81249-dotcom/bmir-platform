'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { Mail, Phone, MapPin, Calendar, Clock, CheckCircle2 } from 'lucide-react';

export default function ContactCentre() {
  const { t, lang } = useApp();
  const [meetingRequested, setMeetingRequested] = useState(false);
  const [meetingForm, setMeetingForm] = useState({
    name: '',
    email: '',
    preferredDate: '',
    topic: 'Technical Review',
  });

  const handleMeetingSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMeetingRequested(true);
  };

  return (
    <section id="contact" className="py-20 bg-[#080F1C] text-white border-b border-[#1E3352]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#19C7D9] bg-[#102A43] px-3 py-1 rounded-full border border-[#1E3352]">
            <Phone className="w-3.5 h-3.5" />
            <span>{t.contact.title}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">
            {t.contact.subtitle}
          </h2>
          <p className="text-sm text-gray-400">
            {lang === 'hi'
              ? 'आधिकारिक अनुसंधान पत्राचार, तकनीकी समीक्षा और बैठकों के लिए सीधा संपर्क।'
              : 'Direct communication line for institutional correspondence, peer review, and inventor meetings.'}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 max-w-5xl mx-auto">
          {/* Contact Details Card */}
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-6">
            <h3 className="text-xl font-bold text-white font-heading">
              {t.contact.headquarters}
            </h3>

            <div className="space-y-4 text-xs">
              <div className="flex items-start space-x-3 p-3.5 rounded-xl bg-[#071426] border border-[#1E3352]">
                <MapPin className="w-5 h-5 text-[#19C7D9] shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Physical Location</div>
                  <div className="text-gray-300 mt-0.5">{t.brand.location} - 812001</div>
                  <div className="text-gray-500 text-[11px] mt-0.5">Republic of India</div>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3.5 rounded-xl bg-[#071426] border border-[#1E3352]">
                <Phone className="w-5 h-5 text-[#19C7D9] shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">{t.contact.directPhone}</div>
                  <a href="tel:+918340328914" className="text-blue-400 hover:underline font-mono text-sm block mt-0.5">
                    +91 8340 328914
                  </a>
                  <div className="text-gray-500 text-[11px]">Available during IST business hours (09:00 - 18:00)</div>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3.5 rounded-xl bg-[#071426] border border-[#1E3352]">
                <Mail className="w-5 h-5 text-[#19C7D9] shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Official Electronic Mail</div>
                  <a href="mailto:contact@bmirresearch.in" className="text-blue-400 hover:underline block mt-0.5">
                    contact@bmirresearch.in
                  </a>
                  <div className="text-gray-500 text-[11px]">Response within 2 business days</div>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#102A43]/40 border border-[#1E3352] text-xs text-gray-300">
              <span className="font-bold text-white block mb-1">Founder Direct Note:</span>
              "We welcome rigorous technical feedback, mathematical critiques of our engineering models, and institutional validation partnerships."
              <div className="text-right text-[#19C7D9] font-semibold mt-2">— Binod Pandey</div>
            </div>
          </div>

          {/* Meeting Request Card */}
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-6">
            <h3 className="text-xl font-bold text-white font-heading">
              {t.contact.scheduleMeeting}
            </h3>

            {meetingRequested ? (
              <div className="py-12 text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h4 className="text-lg font-bold text-white font-heading">Meeting Request Logged</h4>
                <p className="text-xs text-gray-300 max-w-sm mx-auto">
                  Thank you, {meetingForm.name}. A confirmation email will be sent to {meetingForm.email} with teleconference coordinates.
                </p>
                <button
                  onClick={() => setMeetingRequested(false)}
                  className="text-xs text-blue-400 hover:underline pt-2"
                >
                  Schedule another time
                </button>
              </div>
            ) : (
              <form onSubmit={handleMeetingSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Your Full Name *</label>
                  <input
                    type="text"
                    required
                    value={meetingForm.name}
                    onChange={(e) => setMeetingForm({ ...meetingForm, name: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. Dr. Ramesh Gupta"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Your Email Address *</label>
                  <input
                    type="email"
                    required
                    value={meetingForm.email}
                    onChange={(e) => setMeetingForm({ ...meetingForm, email: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. r.gupta@institution.org"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Topic for Discussion</label>
                  <select
                    value={meetingForm.topic}
                    onChange={(e) => setMeetingForm({ ...meetingForm, topic: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-gray-300 focus:outline-none focus:border-[#2878FF]"
                  >
                    <option value="Technical Review">Prototype Technical Review</option>
                    <option value="Patent Discussion">Patent Licensing & IP Discussion</option>
                    <option value="Joint Research">Academic Grant & Joint Research</option>
                    <option value="Field Trials">Agricultural / Clinical Field Trials</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 font-semibold mb-1">Preferred Date / Time Window</label>
                  <input
                    type="text"
                    value={meetingForm.preferredDate}
                    onChange={(e) => setMeetingForm({ ...meetingForm, preferredDate: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                    placeholder="e.g. Next Tuesday afternoon (IST)"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-white font-bold text-xs border border-[#1E3352] transition-colors"
                >
                  Send Meeting Request
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

