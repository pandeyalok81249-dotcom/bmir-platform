'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import { ShieldCheck, Mail, Phone, MapPin, ExternalLink } from 'lucide-react';

export default function Footer() {
  const { t, lang } = useApp();

  return (
    <footer className="bg-[#050D1A] text-gray-400 border-t border-[#1E3352] pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 pb-12 border-b border-[#1E3352]">
          {/* Col 1: Identity */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center font-bold text-white shadow">
                <span>B</span>
              </div>
              <span className="text-xl font-bold text-white tracking-tight">BMIR 2.0</span>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              {t.brand.subheading}
            </p>
            <div className="text-xs text-gray-400 space-y-1">
              <div className="font-semibold text-gray-200">
                {t.brand.founder} · {t.brand.founderRole}
              </div>
              <div>{t.brand.location}</div>
            </div>
          </div>

          {/* Col 2: Research Divisions */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white tracking-wider uppercase font-heading">
              {t.domains.title}
            </h4>
            <ul className="text-xs space-y-2">
              <li>• Artificial Intelligence & Deep Learning</li>
              <li>• Agriculture & Smart Farming (Krishi)</li>
              <li>• Healthcare & Acoustic Diagnostics</li>
              <li>• Renewable Energy & Green Hydrogen</li>
              <li>• Urban Infrastructure & Transit Safety</li>
              <li>• Robotics & Aquatic Automation</li>
            </ul>
          </div>

          {/* Col 3: Direct Institutional Contact */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white tracking-wider uppercase font-heading">
              {t.contact.title}
            </h4>
            <div className="text-xs space-y-2.5">
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-[#19C7D9] shrink-0" />
                <span>Bhagalpur, Bihar, India - 812001</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-[#19C7D9] shrink-0" />
                <a href="tel:+918340328914" className="hover:text-white">
                  +91 8340 328914
                </a>
              </div>
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-[#19C7D9] shrink-0" />
                <a href="mailto:contact@bmirresearch.in" className="hover:text-white">
                  contact@bmirresearch.in
                </a>
              </div>
              <div className="flex items-center space-x-2">
                <ExternalLink className="w-4 h-4 text-[#19C7D9] shrink-0" />
                <a href="https://bmirresearch.in" target="_blank" rel="noreferrer" className="hover:text-white">
                  https://bmirresearch.in
                </a>
              </div>
            </div>
          </div>

          {/* Col 4: Verified Intellectual Property Disclaimer */}
          <div className="space-y-3 bg-[#081220] p-4 rounded-xl border border-[#1E3352]">
            <div className="flex items-center space-x-2 text-[#19C7D9]">
              <ShieldCheck className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">
                {lang === 'hi' ? 'सत्यापित प्रलेखन' : 'Verified Documentation'}
              </span>
            </div>
            <p className="text-[11px] leading-relaxed text-gray-400">
              {lang === 'hi'
                ? 'प्रकाशन पेटेंट की स्वीकृति नहीं है। BMIR किसी भी अविष्कार के लिए झूठी सरकारी या संस्थागत स्वीकृति का दावा नहीं करता है। सभी 17 पेटेंट आवेदन रिकॉर्ड और 3 जर्नल प्रकाशन आधिकारिक रिकॉर्ड पर आधारित हैं।'
                : 'Publication is not patent grant. BMIR makes no fabricated claims of institutional partnerships, awards, or patent grants. All public claims reflect verified Indian Patent Office filing and gazette records.'}
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 space-y-4 sm:space-y-0">
          <div>
            © {new Date().getFullYear()} Bharat Multisector Innovation & Research (BMIR). All rights reserved.
          </div>
          <div className="flex space-x-6">
            <span>Non-Confidential Public Portal</span>
            <span>·</span>
            <span>Security & Integrity Assured</span>
            <span>·</span>
            <span>Bhagalpur, Bihar</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

