'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import {
  LayoutDashboard,
  Bot,
  Layers,
  Sparkles,
  FolderGit2,
  Target,
  Radar,
  BookOpen,
  FileCheck,
  FlaskConical,
  Database,
  CalendarDays,
  FileText,
  Handshake,
  BarChart3,
  Settings,
  Users,
  ShieldCheck,
  ArrowLeft,
  LogOut,
  User as UserIcon,
  Globe,
  Search,
  Bell,
  Menu,
  X,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Shield,
  Clock,
  CheckCircle2,
  Sun,
  Moon,
} from 'lucide-react';
import LogoutModal from '@/components/platform/LogoutModal';

interface NavItem {
  id: string;
  label: string;
  icon: any;
  adminOnly?: boolean;
}

interface NavGroup {
  label: string;
  adminOnly?: boolean;
  items: NavItem[];
}

interface PlatformLayoutProps {
  children: React.ReactNode;
}

export default function PlatformLayout({ children }: PlatformLayoutProps) {
  const { user, logout, activeView, setActiveView, lang, setLang, theme, toggleTheme, t } = useApp();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Search State
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  // Notifications State
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const searchInputRef = useRef<HTMLInputElement>(null);

  // Load notifications
  useEffect(() => {
    bmirApi
      .getNotifications()
      .then((data) => {
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      })
      .catch(() => {});
  }, []);

  // Global search handler
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setSearching(true);
      bmirApi
        .globalSearch(searchQuery)
        .then((res) => {
          setSearchResults(res.results || []);
          setSearching(false);
        })
        .catch(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Keyboard shortcut Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false);
        setNotificationsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navGroups: NavGroup[] = [
    {
      label: 'WORKSPACE',
      items: [
        { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
        { id: 'assistant', label: 'AI Research Assistant', icon: Bot },
        { id: 'multimodel', label: 'Multi-Model Intelligence', icon: Layers },
      ],
    },
    {
      label: 'INNOVATION',
      items: [
        { id: 'discovery', label: 'Innovation Discovery', icon: Sparkles },
        { id: 'portfolio', label: 'Innovation Portfolio', icon: FolderGit2 },
        { id: 'projects', label: 'Research Projects', icon: Target },
        { id: 'feasibility', label: 'Technical Feasibility', icon: Radar },
      ],
    },
    {
      label: 'RESEARCH',
      items: [
        { id: 'literature', label: 'Literature Assistant', icon: BookOpen },
        { id: 'patents', label: 'Patent Research', icon: FileCheck },
        { id: 'experiments', label: 'Experiment Management', icon: FlaskConical },
        { id: 'knowledge', label: 'RAG Knowledge Base', icon: Database },
      ],
    },
    {
      label: 'MANAGEMENT',
      items: [
        { id: 'roadmaps', label: 'Roadmap Generator', icon: CalendarDays },
        { id: 'documents', label: 'Document Centre', icon: FileText },
        { id: 'collaboration_mgmt', label: 'Collaboration Management', icon: Handshake },
        { id: 'analytics', label: 'Analytics & Reports', icon: BarChart3 },
        { id: 'notifications_view', label: 'Notifications Dispatch', icon: Bell },
      ],
    },
    {
      label: 'ADMINISTRATION & PROFILE',
      items: [
        { id: 'profile', label: 'Researcher Profile', icon: UserIcon },
        { id: 'security_settings', label: 'Security & Access', icon: ShieldCheck },
        { id: 'admin', label: 'Admin Control Centre', icon: Settings, adminOnly: true },
        { id: 'user_mgmt', label: 'User Management', icon: Users, adminOnly: true },
      ],
    },
  ];

  const isAdmin = user && ['super_admin', 'founder', 'research_admin'].includes(user.role);

  const handleSelectSearchResult = (result: any) => {
    setIsSearchOpen(false);
    if (result.type === 'Innovation') {
      setActiveView('portfolio');
    } else if (result.type === 'Patent Record') {
      setActiveView('patents');
    } else if (result.type === 'Research Project') {
      setActiveView('projects');
    } else if (result.type === 'Knowledge Document') {
      setActiveView('documents');
    }
  };

  return (
    <div className="min-h-screen bg-[#080F1C] text-white flex flex-col">
      {/* Top Header */}
      <header className="h-16 bg-[#071426] border-b border-[#1E3352] px-4 sm:px-6 flex items-center justify-between sticky top-0 z-40 shadow-md">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
          >
            {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden md:flex p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43] hover:bg-[#1E3352] transition-colors"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>

          <div
            onClick={() => setActiveView('public')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center font-bold text-white shadow-md">
              <span className="font-heading">B</span>
            </div>
            <div className="hidden sm:block">
              <div className="text-sm font-bold text-white font-heading tracking-wide flex items-center space-x-1.5">
                <span>BMIR</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-500/20 text-[#19C7D9] border border-blue-500/30">
                  2.0
                </span>
              </div>
              <div className="text-[10px] text-gray-400">Bharat Multisector Innovation & Research</div>
            </div>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-6">
          <button
            onClick={() => {
              setIsSearchOpen(true);
              setTimeout(() => searchInputRef.current?.focus(), 100);
            }}
            className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl bg-[#080F1C] border border-[#1E3352] hover:border-[#2878FF] text-xs text-gray-400 transition-all shadow-inner"
          >
            <div className="flex items-center space-x-2">
              <Search className="w-3.5 h-3.5 text-gray-400" />
              <span>Search innovations, patents, projects...</span>
            </div>
            <kbd className="px-1.5 py-0.5 rounded bg-[#102A43] text-[10px] font-mono text-gray-400 border border-[#1E3352]">
              Ctrl K
            </kbd>
          </button>
        </div>

        {/* Right Header Controls */}
        <div className="flex items-center space-x-2.5">
          {/* Mobile Search Button */}
          <button
            onClick={() => setIsSearchOpen(true)}
            className="md:hidden p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
          >
            <Search className="w-4 h-4" />
          </button>

          {/* Language Toggle */}
          <button
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs text-gray-300 transition-colors"
          >
            <Globe className="w-3.5 h-3.5 text-[#19C7D9]" />
            <span className="font-semibold">{lang === 'en' ? 'EN' : 'HI'}</span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-[#102A43] hover:bg-[#1E3352] text-xs text-gray-300 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          >
            {theme === 'dark' ? <Moon className="w-3.5 h-3.5 text-[#19C7D9]" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
          </button>

          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="relative p-2 rounded-xl text-gray-300 hover:text-white bg-[#102A43] hover:bg-[#1E3352] transition-colors"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-[#0D1829] border border-[#1E3352] rounded-2xl shadow-2xl p-4 space-y-3 z-50 text-xs">
                <div className="flex items-center justify-between border-b border-[#1E3352] pb-2">
                  <span className="font-bold text-white font-heading">Institutional Notifications</span>
                  <span className="text-[10px] text-[#19C7D9] font-medium">{notifications.length} events</span>
                </div>

                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="py-4 text-center text-gray-500">No unread notifications</div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        className="p-2.5 rounded-xl bg-[#071426] border border-[#1E3352] space-y-1 hover:border-blue-500/40 transition-colors"
                      >
                        <div className="font-bold text-gray-200 flex items-center justify-between">
                          <span>{n.title}</span>
                          {n.unread && <span className="w-1.5 h-1.5 rounded-full bg-[#19C7D9]" />}
                        </div>
                        <div className="text-[11px] text-gray-400">{n.detail}</div>
                      </div>
                    ))
                  )}
                </div>
                <div className="pt-2 border-t border-[#1E3352] text-center">
                  <button
                    onClick={() => {
                      setNotificationsOpen(false);
                      setActiveView('notifications_view');
                    }}
                    className="text-[11px] text-[#19C7D9] hover:underline font-semibold"
                  >
                    Open Notification Dispatch →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Profile Pill */}
          <div
            onClick={() => setActiveView('profile')}
            className="flex items-center space-x-2 pl-2 border-l border-[#1E3352] cursor-pointer hover:opacity-90 transition-opacity"
            title="Open Researcher Profile"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center text-white font-bold text-xs shadow">
              {user?.full_name ? user.full_name.charAt(0) : 'B'}
            </div>
            <div className="hidden lg:block text-left text-xs leading-tight">
              <div className="font-bold text-white truncate max-w-[120px]">
                {user?.full_name || 'Binod Pandey'}
              </div>
              <div className="text-[10px] text-[#19C7D9] capitalize flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>{user?.role.replace('_', ' ') || 'Founder'}</span>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 transition-colors ml-1"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Body with Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`${
            collapsed ? 'w-16' : 'w-64'
          } ${
            mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
          } bg-[#071426] border-r border-[#1E3352] flex flex-col justify-between shrink-0 transition-all duration-300 fixed md:static inset-y-16 left-0 z-30 overflow-y-auto shadow-xl`}
        >
          <div className="py-4 space-y-5">
            {/* Founder Profile Card when expanded */}
            {!collapsed && (
              <div className="px-3">
                <div className="p-3.5 rounded-2xl bg-[#0D1829] border border-[#1E3352] flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-xl bg-[#102A43] border border-[#1E3352] flex items-center justify-center font-bold text-[#19C7D9] text-xs shrink-0">
                    BP
                  </div>
                  <div className="overflow-hidden">
                    <div className="font-bold text-xs text-white truncate">Binod Pandey</div>
                    <div className="text-[10px] text-gray-400">Founder & Inventor</div>
                    <div className="text-[9px] text-emerald-400 flex items-center space-x-1 mt-0.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span>Online · Bhagalpur, India</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Groups */}
            <nav className="space-y-4 px-2">
              {navGroups.map((group) => {
                if (group.adminOnly && !isAdmin) return null;
                return (
                  <div key={group.label} className="space-y-1">
                    {!collapsed && (
                      <div className="px-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                        {group.label}
                      </div>
                    )}
                    {group.items.map((item) => {
                      if (item.adminOnly && !isAdmin) return null;
                      const Icon = item.icon;
                      const isActive =
                        activeView === item.id ||
                        (item.id === 'admin' && activeView === 'user_mgmt');
                      return (
                        <button
                          key={item.id}
                          onClick={() => {
                            if (item.id === 'user_mgmt') {
                              setActiveView('admin');
                            } else {
                              setActiveView(item.id);
                            }
                            setMobileOpen(false);
                          }}
                          title={collapsed ? item.label : undefined}
                          className={`w-full flex items-center ${
                            collapsed ? 'justify-center px-2 py-2.5' : 'space-x-3 px-3 py-2'
                          } rounded-xl text-xs font-medium transition-all ${
                            isActive
                              ? 'bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white shadow-md shadow-blue-500/20 font-semibold'
                              : 'text-gray-300 hover:text-white hover:bg-[#102A43]'
                          }`}
                        >
                          <Icon className="w-4 h-4 shrink-0" />
                          {!collapsed && <span className="truncate">{item.label}</span>}
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </nav>
          </div>

          {/* Bottom Card / Return to Public */}
          <div className="p-3 border-t border-[#1E3352] space-y-2">
            {!collapsed ? (
              <div className="space-y-2">
                <button
                  onClick={() => setActiveView('public')}
                  className="w-full flex items-center justify-center space-x-2 py-2 rounded-xl bg-[#0D1829] hover:bg-[#102A43] border border-[#1E3352] text-xs text-gray-300 hover:text-white transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Public Portal</span>
                </button>
                <div className="text-[10px] text-gray-500 text-center">
                  © 2026 BMIR · All Rights Reserved
                </div>
              </div>
            ) : (
              <button
                onClick={() => setActiveView('public')}
                className="w-full flex justify-center p-2 rounded-xl hover:bg-[#102A43] text-gray-400 hover:text-white"
                title="Back to Public Portal"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
          </div>
        </aside>

        {/* Main Content Pane */}
        <main className="flex-1 overflow-y-auto max-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8 bg-[#080F1C]">
          {children}
        </main>
      </div>

      {/* Global Search Dialog Modal */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-xl w-full p-6 space-y-4 shadow-2xl text-white">
            <div className="flex items-center justify-between border-b border-[#1E3352] pb-3">
              <div className="flex items-center space-x-2 text-xs text-[#19C7D9] font-bold uppercase">
                <Search className="w-4 h-4" />
                <span>Search BMIR Knowledge & Records</span>
              </div>
              <button
                onClick={() => setIsSearchOpen(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Type keywords (e.g. maize, hydrogen, acoustic, patent no)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 bg-[#071426] border border-[#1E3352] rounded-xl text-xs text-white focus:outline-none focus:border-[#2878FF]"
              />
            </div>

            <div className="max-h-72 overflow-y-auto space-y-2 text-xs">
              {searching ? (
                <div className="py-6 text-center text-gray-400">Searching database...</div>
              ) : searchResults.length === 0 ? (
                searchQuery ? (
                  <div className="py-6 text-center text-gray-400">No verified matching records found</div>
                ) : (
                  <div className="py-6 text-center text-gray-500">
                    Search across all 27 innovations, 17 patent records, 4 research projects, and scientific papers.
                  </div>
                )
              ) : (
                searchResults.map((r) => (
                  <div
                    key={`${r.type}-${r.id}`}
                    onClick={() => handleSelectSearchResult(r)}
                    className="p-3 rounded-xl bg-[#071426] hover:bg-[#102A43] border border-[#1E3352] hover:border-[#2878FF] cursor-pointer transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-[10px] font-bold px-1.5 py-0.2 rounded bg-[#102A43] text-gray-300">
                          {r.type}
                        </span>
                        {r.code && <span className="font-mono text-[10px] text-[#19C7D9]">{r.code}</span>}
                        {r.verification_status && (
                          <span
                            className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                              r.verification_status === 'Verified'
                                ? 'bg-emerald-500/10 text-emerald-400'
                                : 'bg-amber-500/10 text-amber-400'
                            }`}
                          >
                            {r.verification_status}
                          </span>
                        )}
                      </div>
                      <div className="font-bold text-white text-xs mt-1">{r.title}</div>
                      <div className="text-[11px] text-gray-400">{r.category}</div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-gray-400" />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
      {/* Logout Confirmation Modal */}
      <LogoutModal />
    </div>
  );
}
