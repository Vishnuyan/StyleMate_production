import React from 'react';
import { motion } from 'motion/react';
import { ArrowRight, Sparkles, ShieldCheck, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative h-[90vh] flex items-center justify-center">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&q=80&w=2070" 
            alt="Fashion Background" 
            className="w-full h-full object-cover opacity-40"
            referrerPolicy="no-referrer"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-luxury-black/0 via-luxury-black/50 to-luxury-black" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-block px-4 py-1.5 mb-6 text-xs font-bold tracking-[0.3em] uppercase bg-white/10 backdrop-blur-md rounded-full border border-white/10">
              AI-Powered Personal Stylist
            </span>
            <h1 className="text-6xl md:text-8xl font-serif font-bold mb-8 leading-tight tracking-tighter">
              Discover Your <br />
              <span className="italic text-gold">Perfect Silhouette</span>
            </h1>
            <p className="max-w-2xl mx-auto text-lg text-white/70 mb-10 font-light leading-relaxed">
              Stylemate uses advanced computer vision to analyze your body shape and skin tone, 
              delivering curated outfit recommendations tailored uniquely to you.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/prediction" className="luxury-button flex items-center space-x-2 group">
                <span>Start Recommendation</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link to="/about" className="px-6 py-3 text-sm font-medium hover:text-gold transition-colors">
                Learn How It Works
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-luxury-gray">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-serif font-bold mb-4">The Stylemate Advantage</h2>
            <div className="h-1 w-20 bg-gold mx-auto" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: <Sparkles className="h-8 w-8 text-gold" />,
                title: "AI Precision",
                desc: "Our models are trained on thousands of fashion profiles to identify your unique body shape and skin tone with high accuracy."
              },
              {
                icon: <Zap className="h-8 w-8 text-gold" />,
                title: "Instant Results",
                desc: "Upload your photo and get detailed recommendations for casual, formal, and party wear in seconds."
              },
              {
                icon: <ShieldCheck className="h-8 w-8 text-gold" />,
                title: "Privacy First",
                desc: "Your photos are processed securely and are never stored without your explicit permission. Your data is your own."
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="glass-card p-8 hover:border-gold/30 transition-colors"
              >
                <div className="mb-6">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
                <p className="text-white/60 text-sm leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Future Services Preview */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl font-serif font-bold mb-6">Beyond Outfits</h2>
              <p className="text-white/70 mb-8 leading-relaxed">
                We're expanding the Stylemate ecosystem to provide a comprehensive fashion experience. 
                Soon, you'll be able to access specialized recommendations for every aspect of your look.
              </p>
              <ul className="space-y-4">
                {[
                  "Jewelry matching based on skin undertones",
                  "Event-themed dress suggestions",
                  "Seasonal wardrobe planning",
                  "Color palette optimization"
                ].map((item, i) => (
                  <li key={i} className="flex items-center space-x-3 text-sm">
                    <div className="h-1.5 w-1.5 rounded-full bg-gold" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl overflow-hidden">
                <img 
                  src="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=2070" 
                  alt="Jewelry" 
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              </div>
             
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gold">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-serif font-bold text-black mb-8">Ready to redefine your style?</h2>
          <Link to="/signup" className="inline-block px-10 py-4 bg-black text-white font-bold rounded-full hover:bg-luxury-gray transition-colors">
            Join Stylemate Today
          </Link>
        </div>
      </section>
    </div>
  );
}
