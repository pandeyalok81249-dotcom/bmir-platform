import type { Metadata } from 'next';
import './globals.css';
import { AppProvider } from '@/lib/context';
import AuthModal from '@/components/platform/AuthModal';

export const metadata: Metadata = {
  title: 'BMIR 2.0 | Bharat Multisector Innovation & Research',
  description:
    'Enterprise-grade AI research, multidisciplinary engineering, patent intelligence, and global collaboration ecosystem led by independent inventor Binod Pandey, Bhagalpur, Bihar, India.',
  keywords: [
    'BMIR',
    'Bharat Multisector Innovation & Research',
    'Binod Pandey',
    'Bhagalpur',
    'AI Research Platform',
    'Independent Inventor',
    'Indian Patent Office',
    'Green Hydrogen Cylinder',
    'Intelligent Maize Dryer',
    'AI-SHRUTI',
  ],
  authors: [{ name: 'Binod Pandey', url: 'https://bmirresearch.in' }],
  openGraph: {
    title: 'BMIR 2.0 — Research Beyond Boundaries',
    description:
      'Independent multidisciplinary research initiative and AI intelligence workspace for smart agriculture, healthcare, and clean tech.',
    url: 'https://bmirresearch.in',
    siteName: 'Bharat Multisector Innovation & Research',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Manrope:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#080F1C] text-gray-100 min-h-screen antialiased selection:bg-[#2878FF] selection:text-white">
        <AppProvider>
          {children}
          <AuthModal />
        </AppProvider>
      </body>
    </html>
  );
}

