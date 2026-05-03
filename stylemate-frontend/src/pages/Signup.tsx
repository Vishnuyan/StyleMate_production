import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Shirt, Mail, Lock, User, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiFetch } from '../lib/api';

export default function Signup() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [name, setName] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await apiFetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        toast.success('Account created successfully!');
        navigate('/dashboard');
      } else {
        toast.error(data.message || 'Signup failed');
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card w-full max-w-md p-8 md:p-10"
      >
        <div className="text-center mb-10">
          <Link to="/" className="inline-flex items-center space-x-2 mb-6">
            <Shirt className="h-8 w-8 text-gold" />
            <span className="text-2xl font-serif font-bold tracking-tighter">STYLEMATE</span>
          </Link>
          <h1 className="text-3xl font-serif font-bold">Create Account</h1>
          <p className="text-white/60 text-sm mt-2">Join the future of fashion intelligence</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-white/60">Full Name</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-white/20" />
              <input 
                type="text" 
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="luxury-input pl-12" 
                placeholder="John Doe"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-white/60">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-white/20" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="luxury-input pl-12" 
                placeholder="name@example.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-white/60">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-white/20" />
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="luxury-input pl-12" 
                placeholder="••••••••"
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="luxury-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{loading ? 'Creating account...' : 'Create Account'}</span>
            {!loading && <ArrowRight className="h-4 w-4" />}
          </button>
        </form>

        <div className="mt-8 text-center text-sm">
          <span className="text-white/60">Already have an account? </span>
          <Link to="/login" className="text-gold font-bold hover:underline">Sign In</Link>
        </div>
      </motion.div>
    </div>
  );
}
