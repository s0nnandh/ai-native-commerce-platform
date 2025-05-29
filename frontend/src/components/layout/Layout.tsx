import type { ReactNode } from 'react';
import Header from './Header';
import Footer from './Footer';
import StickySearchHeader from '../search/StickySearchHeader';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen bg-background dark:bg-gray-900">
      <Header />
      <StickySearchHeader />
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
