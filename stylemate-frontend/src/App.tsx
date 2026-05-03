import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Prediction from './pages/Prediction';
import About from './pages/About';
import Contact from './pages/Contact';
import Accessories from './pages/Accessories';
import Wardrobe from "./pages/Wardrobe";
import Outfit from "./pages/Outfit";

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/prediction" 
            element={
              <ProtectedRoute>
                <Prediction />
              </ProtectedRoute>
            } 
          />

          <Route
            path="/accessories"
            element={
              <ProtectedRoute>
                <Accessories />
              </ProtectedRoute>
            }
          />

          <Route
            path="/wardrobe"
            element={
            <ProtectedRoute>
            <Wardrobe />
            </ProtectedRoute>
            }
          />
          
          <Route
            path="/outfit"
            element={
              <ProtectedRoute>
                <Outfit />
              </ProtectedRoute>
            }
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}
