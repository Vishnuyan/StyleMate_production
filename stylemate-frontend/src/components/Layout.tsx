import React from 'react';
import Header from './Header';
import Footer from './Footer';
import { Toaster } from 'react-hot-toast';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Toaster position="top-right" />
      <Header />
      <main className="flex-grow pt-20">
        {children}
      </main>
      <Footer />
    </div>
  );
}
