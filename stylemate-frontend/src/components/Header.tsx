import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shirt, User, LogOut, Menu, X } from 'lucide-react';

export default function Header() {
  const [isOpen, setIsOpen] = React.useState(false);
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  // Safe user parsing
  const user = React.useMemo(() => {
    const stored = localStorage.getItem('user');
    if (!stored) return { name: '' };

    try {
      const parsed = JSON.parse(stored);
      return parsed && typeof parsed === 'object' ? parsed : { name: '' };
    } catch (err) {
      console.warn('Failed to parse user from localStorage:', err);
      localStorage.removeItem('user');
      return { name: '' };
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-luxury-black/80 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link to="/" className="flex items-center space-x-2">
            <Shirt className="h-8 w-8 text-gold" />
            <span className="text-2xl font-serif font-bold tracking-tighter">STYLEMATE</span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-sm font-medium hover:text-gold transition-colors">Home</Link>
            <Link to="/prediction" className="text-sm font-medium hover:text-gold transition-colors">Recommend</Link>
            <Link to="/accessories" className="text-sm font-medium hover:text-gold transition-colors">Accessories</Link>
            <Link to="/Wardrobe" className="text-sm font-medium hover:text-gold transition-colors">Wardrobe</Link>
            <Link to="/outfit" className="text-sm font-medium hover:text-gold transition-colors">Theme & Occasion</Link>
            <Link to="/about" className="text-sm font-medium hover:text-gold transition-colors">About</Link>
            <Link to="/contact" className="text-sm font-medium hover:text-gold transition-colors">Contact</Link>
            
            {token ? (
              <div className="flex items-center space-x-4 ml-4">
                <Link to="/dashboard" className="flex items-center space-x-2 text-sm font-medium hover:text-gold transition-colors">
                  <User className="h-4 w-4" />
                  <span>{user.name}</span>
                </Link>
                <button 
                  onClick={handleLogout}
                  className="p-2 hover:text-red-500 transition-colors"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4 ml-4">
                <Link to="/login" className="text-sm font-medium hover:text-gold transition-colors">Login</Link>
                <Link to="/signup" className="luxury-button !py-2 !px-4 text-sm">Sign Up</Link>
              </div>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="p-2">
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      {isOpen && (
        <div className="md:hidden bg-luxury-gray border-b border-white/5 px-4 py-6 space-y-4">
          <Link to="/" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Home</Link>
          <Link to="/prediction" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Recommend</Link>
          <Link to="/accessories" className="text-sm font-medium hover:text-gold transition-colors">Accessories Suggestion</Link>
          <Link to="/Wardrobe" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Wardrobe</Link>
          <Link to="/outfit" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Theme & Occasion</Link>
          <Link to="/about" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>About</Link>
          <Link to="/contact" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Contact</Link>
          {token ? (
            <>
              <Link to="/dashboard" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Dashboard</Link>
              <button onClick={handleLogout} className="block text-lg font-medium text-red-500">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="block text-lg font-medium" onClick={() => setIsOpen(false)}>Login</Link>
              <Link to="/signup" className="block text-lg font-medium text-gold" onClick={() => setIsOpen(false)}>Sign Up</Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}
