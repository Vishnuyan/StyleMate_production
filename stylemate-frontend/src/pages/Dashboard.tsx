// src/pages/Dashboard.tsx
import React from 'react';
import { motion } from 'framer-motion'; // Assuming framer-motion; adjust if different
import { User, History, Settings, Heart, ChevronRight, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const storedUser = localStorage.getItem('user');
  let user = { name: 'Guest', email: '' };

  if (storedUser) {
    try {
      user = JSON.parse(storedUser);
    } catch (e) {
      console.warn('Invalid user data in localStorage', e);
      localStorage.removeItem('user'); // Clean up bad data
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <aside className="w-full md:w-64 space-y-2">
          <div className="glass-card p-6 mb-8 text-center">
            <div className="h-20 w-20 bg-gold/20 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-gold/50">
              <User className="h-10 w-10 text-gold" />
            </div>
            <h2 className="text-xl font-serif font-bold">{user.name || 'User'}</h2>
            <p className="text-xs text-white/40 mt-1">{user.email || '—'}</p>
          </div>
          <nav className="space-y-1">
            {[
              { icon: <User className="h-4 w-4" />, label: "Profile", active: true },
              { icon: <History className="h-4 w-4" />, label: "History", active: false },
              { icon: <Heart className="h-4 w-4" />, label: "Favorites", active: false },
              { icon: <Settings className="h-4 w-4" />, label: "Settings", active: false },
            ].map((item, i) => (
              <button
                key={i}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm transition-colors ${
                  item.active ? 'bg-gold text-black font-bold' : 'text-white/60 hover:bg-white/5'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </aside>
        {/* Main Content */}
        <main className="flex-grow space-y-8">
          <header className="flex justify-between items-end">
            <div>
              <h1 className="text-3xl font-serif font-bold">Style Dashboard</h1>
              <p className="text-white/40 text-sm">Manage your fashion profile and recommendations</p>
            </div>
            <Link to="/prediction" className="luxury-button !py-2 !px-4 text-xs flex items-center space-x-2">
              <Sparkles className="h-3 w-3" />
              <span>New Analysis</span>
            </Link>
          </header>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-8">
              <h3 className="text-sm font-bold uppercase tracking-widest text-gold mb-6">Recent Recommendations</h3>
              <div className="space-y-4">
                {[
                  { date: "Oct 24, 2023", type: "Formal Wear", shape: "Hourglass" },
                  { date: "Oct 12, 2023", type: "Casual Look", shape: "Hourglass" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/20 transition-colors cursor-pointer group">
                    <div>
                      <p className="text-sm font-bold">{item.type}</p>
                      <p className="text-[10px] text-white/40 uppercase tracking-widest">{item.date} • {item.shape}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-white/20 group-hover:text-gold transition-colors" />
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-card p-8">
              <h3 className="text-sm font-bold uppercase tracking-widest text-gold mb-6">Style Profile</h3>
              <div className="space-y-6">
                <div className="flex justify-between items-center pb-4 border-b border-white/5">
                  <span className="text-sm text-white/60">Body Shape</span>
                  <span className="text-sm font-bold">Hourglass</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-white/5">
                  <span className="text-sm text-white/60">Skin Tone</span>
                  <span className="text-sm font-bold">Mid-Light</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-white/5">
                  <span className="text-sm text-white/60">Preferred Style</span>
                  <span className="text-sm font-bold">Minimalist</span>
                </div>
                <button className="text-xs text-gold font-bold hover:underline">Edit Profile Details</button>
              </div>
            </div>
          </div>
          <div className="glass-card p-8 bg-gradient-to-r from-gold/10 to-transparent border-gold/20">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <h3 className="text-xl font-serif font-bold">Unlock Jewelry Recommendations</h3>
                <p className="text-sm text-white/60 max-w-md">Our new skin-tone based jewelry matching service is launching soon. Be the first to try it!</p>
              </div>
              <button className="px-6 py-2 bg-gold text-black text-xs font-bold rounded-full">Notify Me</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}