import { useEffect, useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Map, CalendarDays, Compass, Settings, LogOut, Menu, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { getMe } from '../../features/auth/authApi';
import logo from '../../assets/GlobeTrotter_Logo.png';

export const AppLayout = () => {
  const location = useLocation();
  const { user, setUser, setLoading, logout } = useAuthStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      if (!user) {
        setLoading(true);
        try {
          const userData = await getMe();
          setUser(userData);
        } catch (error) {
          console.error("Failed to fetch user", error);
          logout(); 
        } finally {
          setLoading(false);
        }
      }
    };
    fetchUser();
  }, [user, setUser, setLoading, logout]);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: Map },
    { name: 'Calendar', path: '/calendar', icon: CalendarDays },
    { name: 'Explore', path: '/explore', icon: Compass },
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row">
      {/* Mobile Top Navbar */}
      <div className="md:hidden flex items-center justify-between p-4 bg-surface border-b border-border-default z-20">
        <img src={logo} alt="GlobeTrotter" className="h-8 w-auto" onError={(e) => { e.target.style.display = 'none'; }} />
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-text-primary p-2">
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar (Desktop) & Mobile Drawer */}
      <aside className={`
        fixed inset-y-0 left-0 z-10 w-64 bg-surface border-r border-border-default transform transition-transform duration-300 ease-in-out
        md:relative md:translate-x-0 flex flex-col
        ${isMobileMenuOpen ? 'translate-x-0 top-16.25 h-[calc(100vh-65px)]' : '-translate-x-full'}
      `}>
        <div className="hidden md:flex p-6 items-center">
          <img src={logo} alt="GlobeTrotter" className="h-8 w-auto" onError={(e) => { e.target.style.display = 'none'; }} />
        </div>

        <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname.includes(item.path);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
                  isActive 
                    ? 'bg-primary-soft text-primary' 
                    : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                }`}
              >
                <Icon size={20} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border-subtle">
          {user && (
            <div className="flex items-center gap-3 px-4 py-3 mb-2 bg-surface-muted rounded-xl">
              <div className="w-8 h-8 rounded-full bg-primary text-text-on-primary flex items-center justify-center font-bold">
                {user.first_name?.[0]}{user.last_name?.[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-text-primary truncate">{user.first_name} {user.last_name}</p>
                <p className="text-xs text-text-muted truncate">{user.email}</p>
              </div>
            </div>
          )}
          <Link to="/profile" className="flex items-center gap-3 px-4 py-3 rounded-xl text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors">
            <Settings size={20} />
            Settings
          </Link>
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-error hover:bg-error-soft transition-colors mt-1">
            <LogOut size={20} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8 relative">
        <Outlet />
      </main>
    </div>
  );
};