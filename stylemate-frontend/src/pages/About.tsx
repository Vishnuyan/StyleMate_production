import React from 'react';
import { motion } from 'motion/react';
import { Shirt, Sparkles, Users, Globe } from 'lucide-react';

export default function About() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-24">
      <div className="max-w-3xl mx-auto text-center mb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-5xl md:text-6xl font-serif font-bold mb-8">The Future of <br /><span className="text-gold italic">Personal Style</span></h1>
          <p className="text-lg text-white/60 leading-relaxed font-light">
            Stylemate was born from a simple idea: that technology should empower personal expression. 
            We combine state-of-the-art AI with deep fashion expertise to help you look and feel your best.
          </p>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-24 items-center mb-32">
        <div className="relative">
          <div className="aspect-[4/5] rounded-2xl overflow-hidden">
            <img 
              src="https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&q=80&w=1000" 
              alt="Fashion Tech" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
          <div className="absolute -bottom-10 -right-10 glass-card p-10 hidden lg:block">
            <Sparkles className="h-12 w-12 text-gold mb-4" />
            <p className="text-2xl font-serif font-bold">98% Accuracy</p>
            <p className="text-xs text-white/40 uppercase tracking-widest">In Body Shape Detection</p>
          </div>
        </div>
        <div className="space-y-8">
          <h2 className="text-4xl font-serif font-bold">Our Mission</h2>
          <p className="text-white/70 leading-relaxed">
            We believe that everyone deserves a personal stylist. Fashion is more than just clothes; 
            it's a form of communication. By understanding the unique geometry of your body and the 
            undertones of your skin, we unlock a world of confidence.
          </p>
          <div className="space-y-6">
            {[
              { icon: <Users className="h-5 w-5 text-gold" />, title: "Inclusive Design", desc: "Our models are trained on diverse datasets to ensure accuracy for all body types and skin tones." },
              { icon: <Globe className="h-5 w-5 text-gold" />, title: "Global Trends", desc: "We integrate global fashion trends with timeless style principles." },
              { icon: <Shirt className="h-5 w-5 text-gold" />, title: "Sustainable Style", desc: "By helping you find what truly fits, we reduce returns and promote intentional shopping." }
            ].map((item, i) => (
              <div key={i} className="flex items-start space-x-4">
                <div className="p-2 bg-white/5 rounded-lg">{item.icon}</div>
                <div>
                  <h4 className="font-bold text-sm mb-1">{item.title}</h4>
                  <p className="text-xs text-white/50 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass-card p-12 text-center bg-gradient-to-b from-white/5 to-transparent">
        <h2 className="text-3xl font-serif font-bold mb-6">Our Journey</h2>
        <p className="max-w-2xl mx-auto text-white/60 mb-12">
          Started as a research project in 2023, Stylemate has evolved into a comprehensive fashion intelligence platform. 
          We're just getting started on our mission to revolutionize how the world dresses.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { label: "Users", value: "50k+" },
            { label: "Recommendations", value: "1M+" },
            { label: "Countries", value: "120+" },
            { label: "Style Experts", value: "15" }
          ].map((stat, i) => (
            <div key={i}>
              <p className="text-3xl font-serif font-bold text-gold mb-1">{stat.value}</p>
              <p className="text-[10px] font-bold uppercase tracking-widest text-white/40">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
