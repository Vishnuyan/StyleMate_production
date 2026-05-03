import React from 'react';
import { motion } from 'motion/react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Contact() {
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      toast.success('Message sent! We will get back to you soon.');
      setLoading(false);
      (e.target as HTMLFormElement).reset();
    }, 1500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-24">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-24">
        <div>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h1 className="text-5xl font-serif font-bold mb-8">Get in <span className="text-gold italic">Touch</span></h1>
            <p className="text-lg text-white/60 mb-12 font-light leading-relaxed">
              Have questions about our AI technology or want to partner with us? 
              Our team of fashion tech experts is here to help.
            </p>

            <div className="space-y-8">
              {[
                { icon: <Mail className="h-6 w-6 text-gold" />, label: "Email Us", value: "hello@stylemate.ai" },
                { icon: <Phone className="h-6 w-6 text-gold" />, label: "Call Us", value: "+1 (555) 123-4567" },
                { icon: <MapPin className="h-6 w-6 text-gold" />, label: "Visit Us", value: "123 Fashion Ave, New York, NY" }
              ].map((item, i) => (
                <div key={i} className="flex items-center space-x-6">
                  <div className="p-4 bg-white/5 rounded-2xl border border-white/10">{item.icon}</div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-1">{item.label}</p>
                    <p className="text-lg font-medium">{item.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-10"
        >
          <h2 className="text-2xl font-serif font-bold mb-8">Send a Message</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-white/60">First Name</label>
                <input type="text" required className="luxury-input" placeholder="John" />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-white/60">Last Name</label>
                <input type="text" required className="luxury-input" placeholder="Doe" />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-white/60">Email Address</label>
              <input type="email" required className="luxury-input" placeholder="john@example.com" />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-white/60">Subject</label>
              <select className="luxury-input">
                <option>General Inquiry</option>
                <option>Technical Support</option>
                <option>Partnership</option>
                <option>Press</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-white/60">Message</label>
              <textarea required rows={4} className="luxury-input resize-none" placeholder="How can we help you?"></textarea>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="luxury-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{loading ? 'Sending...' : 'Send Message'}</span>
              {!loading && <Send className="h-4 w-4" />}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
