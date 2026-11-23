'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { Sparkles, Globe, User, LogOut, Menu, X, Shield, ChevronRight } from 'lucide-react';

export default function Header() {
  const { lang, setLang, t, user, logout, setIsAuthModalOpen, activeView, setActiveView } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { id: 'about', label: t.nav.about, href: '#about' },
    { id: 'portfolio', label: t.nav.portfolio, href: '#portfolio' },
    { id: 'projects', label: t.nav.projects, href: '#projects' },
    { id: 'patents', label: t.nav.patents, href: '#patents' },
    { id: 'domains', label: t.nav.domains, href: '#domains' },
    { id: 'collaboration', label: t.nav.collaboration, href: '#collaboration' },
    { id: 'contact', label: t.nav.contact, href: '#contact' },
  ];

  const handleNavClick = (href: string) => {
    setActiveView('public');
    setMobileMenuOpen(false);
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-[#071426]/95 backdrop-blur-md border-b border-[#1E3352] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => {
            setActiveView('public');
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
        >
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <span className="text-xl tracking-wider font-extrabold">B</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white font-heading">BMIR</span>
              <span className="px-1.5 py-0.5 text-[10px] uppercase font-bold tracking-widest bg-blue-500/20 text-[#19C7D9] border border-[#19C7D9]/30 rounded">
                2.0
              </span>
            </div>
            <div className="text-[11px] text-gray-400 font-medium tracking-wide hidden sm:block">
              {lang === 'hi' ? 'भारत मल्टीसेक्टर इनोवेशन एंड रिसर्च' : 'Bharat Multisector Innovation & Research'}
            </div>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex items-center space-x-6 text-sm font-medium text-gray-300">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => handleNavClick(link.href)}
              className="hover:text-white hover:text-[#19C7D9] transition-colors"
            >
              {link.label}
            </button>
          ))}
        </nav>

        {/* Right CTA & Controls */}
        <div className="hidden sm:flex items-center space-x-3">
          {/* Language Switcher */}
          <button
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#102A43] hover:bg-[#1E3352] text-gray-200 border border-[#1E3352] transition-colors"
            title="Toggle English / हिंदी"
          >
            <Globe className="w-3.5 h-3.5 text-[#19C7D9]" />
            <span>{lang === 'en' ? 'हिंदी' : 'English'}</span>
          </button>

          {/* AI Lab Access Button */}
          <button
            onClick={() => {
              if (user) {
                setActiveView('dashboard');
              } else {
                setIsAuthModalOpen(true);
              }
            }}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#2878FF] to-[#19C7D9] hover:opacity-95 text-white font-semibold text-xs tracking-wide shadow-md shadow-blue-500/25 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-white animate-pulse" />
            <span>{t.hero.enterLab}</span>
          </button>

          {/* User Auth Info */}
          {user ? (
            <div className="flex items-center space-x-2 pl-2 border-l border-[#1E3352]">
              <button
                onClick={() => setActiveView('dashboard')}
                className="flex items-center space-x-2 text-xs font-semibold text-gray-200 bg-[#102A43] hover:bg-[#1E3352] px-3 py-1.5 rounded-lg border border-[#1E3352]"
              >
                <Shield className="w-3.5 h-3.5 text-[#19C7D9]" />
                <span className="max-w-[100px] truncate">{user.full_name}</span>
                <span className="text-[10px] text-blue-400 capitalize">({user.role.replace('_', ' ')})</span>
              </button>
              <button
                onClick={logout}
                className="p-1.5 text-gray-400 hover:text-red-400 rounded-lg hover:bg-[#102A43]"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsAuthModalOpen(true)}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-gray-300 hover:text-white hover:bg-[#102A43] rounded-lg transition-colors"
            >
              <User className="w-3.5 h-3.5" />
              <span>{t.nav.signIn}</span>
            </button>
          )}
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden items-center space-x-2">
          <button
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="px-2 py-1 text-xs font-bold rounded bg-[#102A43] text-gray-200 border border-[#1E3352]"
          >
            {lang === 'en' ? 'हि' : 'EN'}
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-gray-400 hover:text-white"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-[#071426] border-b border-[#1E3352] px-4 pt-2 pb-6 space-y-3">
          <div className="grid grid-cols-2 gap-2 pb-3 border-b border-[#1E3352]">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => handleNavClick(link.href)}
                className="text-left text-sm py-2 px-3 rounded hover:bg-[#102A43] text-gray-300"
              >
                {link.label}
              </button>
            ))}
          </div>
          <div className="pt-2 flex flex-col space-y-2">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                if (user) {
                  setActiveView('dashboard');
                } else {
                  setIsAuthModalOpen(true);
                }
              }}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-semibold text-center text-sm shadow"
            >
              {t.hero.enterLab}
            </button>
            {user ? (
              <button
                onClick={logout}
                className="w-full py-2 text-center text-xs text-red-400 font-medium"
              >
                {t.nav.signOut} ({user.full_name})
              </button>
            ) : (
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setIsAuthModalOpen(true);
                }}
                className="w-full py-2 text-center text-xs text-gray-300 font-medium"
              >
                {t.nav.signIn}
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

