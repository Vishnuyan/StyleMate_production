// src/pages/Login.tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion'; // Note: you had 'motion/react' which might be a typo; assuming framer-motion
import { Shirt, Mail, Lock, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiFetch } from '../lib/api';

export default function Login() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await apiFetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        toast.error(errorData.detail || 'Login failed');
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      console.error(error);
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
          <h1 className="text-3xl font-serif font-bold">Welcome Back</h1>
          <p className="text-white/60 text-sm mt-2">Sign in to your account to continue</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
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
            <span>{loading ? 'Signing in...' : 'Sign In'}</span>
            {!loading && <ArrowRight className="h-4 w-4" />}
          </button>
        </form>
        <div className="mt-8 text-center text-sm">
          <span className="text-white/60">Don't have an account? </span>
          <Link to="/signup" className="text-gold font-bold hover:underline">Sign Up</Link>
        </div>
      </motion.div>
    </div>
  );
}