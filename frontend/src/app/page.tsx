'use client';

import React from 'react';
import { useApp } from '@/lib/context';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Hero from '@/components/public/Hero';
import AboutSection from '@/components/public/AboutSection';
import InnovationPortfolio from '@/components/public/InnovationPortfolio';
import ResearchProjectsSection from '@/components/public/ResearchProjectsSection';
import PatentCentre from '@/components/public/PatentCentre';
import ResearchDomainsSection from '@/components/public/ResearchDomainsSection';
import CollaborationPortal from '@/components/public/CollaborationPortal';
import ContactCentre from '@/components/public/ContactCentre';

// Platform Views
import PlatformLayout from '@/components/platform/PlatformLayout';
import DashboardView from '@/components/platform/DashboardView';
import AIAssistantView from '@/components/platform/AIAssistantView';
import MultiModelCompareView from '@/components/platform/MultiModelCompareView';
import InnovationDiscoveryView from '@/components/platform/InnovationDiscoveryView';
import InnovationPortfolioView from '@/components/platform/InnovationPortfolioView';
import ResearchProjectsView from '@/components/platform/ResearchProjectsView';
import TechnicalFeasibilityView from '@/components/platform/TechnicalFeasibilityView';
import LiteratureAssistantView from '@/components/platform/LiteratureAssistantView';
import PatentAssistantView from '@/components/platform/PatentAssistantView';
import ExperimentManagementView from '@/components/platform/ExperimentManagementView';
import KnowledgeBaseView from '@/components/platform/KnowledgeBaseView';
import RoadmapGeneratorView from '@/components/platform/RoadmapGeneratorView';
import DocumentCentreView from '@/components/platform/DocumentCentreView';
import CollaborationMgmtView from '@/components/platform/CollaborationMgmtView';
import PlatformAnalyticsView from '@/components/platform/PlatformAnalyticsView';
import AdminControlCentre from '@/components/platform/AdminControlCentre';
import AccountSecurityView from '@/components/platform/AccountSecurityView';
import ProfileManagementView from '@/components/platform/ProfileManagementView';
import NotificationCentreView from '@/components/platform/NotificationCentreView';

export default function Home() {
  const { activeView } = useApp();

  // If in public view, render the international institutional website
  if (activeView === 'public') {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-1">
          <Hero />
          <AboutSection />
          <InnovationPortfolio />
          <ResearchProjectsSection />
          <PatentCentre />
          <ResearchDomainsSection />
          <CollaborationPortal />
          <ContactCentre />
        </main>
        <Footer />
      </div>
    );
  }

  // Otherwise, render the authenticated BMIR AI Research Intelligence Platform
  return (
    <PlatformLayout>
      {activeView === 'dashboard' && <DashboardView />}
      {activeView === 'assistant' && <AIAssistantView />}
      {activeView === 'multimodel' && <MultiModelCompareView />}
      {activeView === 'discovery' && <InnovationDiscoveryView />}
      {activeView === 'portfolio' && <InnovationPortfolioView />}
      {activeView === 'projects' && <ResearchProjectsView />}
      {activeView === 'feasibility' && <TechnicalFeasibilityView />}
      {activeView === 'literature' && <LiteratureAssistantView />}
      {activeView === 'patents' && <PatentAssistantView />}
      {activeView === 'experiments' && <ExperimentManagementView />}
      {activeView === 'knowledge' && <KnowledgeBaseView />}
      {activeView === 'roadmaps' && <RoadmapGeneratorView />}
      {activeView === 'documents' && <DocumentCentreView />}
      {activeView === 'collaboration_mgmt' && <CollaborationMgmtView />}
      {activeView === 'analytics' && <PlatformAnalyticsView />}
      {activeView === 'notifications_view' && <NotificationCentreView />}
      {activeView === 'profile' && <ProfileManagementView />}
      {activeView === 'security_settings' && <AccountSecurityView />}
      {(activeView === 'admin' || activeView === 'user_mgmt') && <AdminControlCentre />}
    </PlatformLayout>
  );
}

