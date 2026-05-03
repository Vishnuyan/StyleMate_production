import React from 'react';
import { Shirt, Instagram, Twitter, Facebook } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-luxury-gray border-t border-white/5 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Shirt className="h-6 w-6 text-gold" />
              <span className="text-xl font-serif font-bold tracking-tighter">STYLEMATE</span>
            </div>
            <p className="text-sm text-white/60 leading-relaxed">
              Elevating your personal style through AI-driven fashion intelligence. Discover the perfect look for every occasion.
            </p>
          </div>
          
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">Services</h4>
            <ul className="space-y-4 text-sm text-white/60">
              <li><a href="#" className="hover:text-gold transition-colors">Outfit Recommendation</a></li>
              <li><a href="#" className="hover:text-gold transition-colors">Skin Tone Analysis</a></li>
              <li><a href="#" className="hover:text-gold transition-colors">Body Shape Profiling</a></li>
              <li><a href="#" className="hover:text-gold transition-colors">Jewelry Matching (Coming Soon)</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">Company</h4>
            <ul className="space-y-4 text-sm text-white/60">
              <li><a href="/about" className="hover:text-gold transition-colors">About Us</a></li>
              <li><a href="/contact" className="hover:text-gold transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-gold transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-gold transition-colors">Terms of Service</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">Follow Us</h4>
            <div className="flex space-x-4">
              <a href="#" className="p-2 bg-white/5 rounded-full hover:bg-gold transition-colors"><Instagram className="h-5 w-5" /></a>
              <a href="#" className="p-2 bg-white/5 rounded-full hover:bg-gold transition-colors"><Twitter className="h-5 w-5" /></a>
              <a href="#" className="p-2 bg-white/5 rounded-full hover:bg-gold transition-colors"><Facebook className="h-5 w-5" /></a>
            </div>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-white/5 text-center text-xs text-white/40">
          <p>&copy; {new Date().getFullYear()} Stylemate AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
