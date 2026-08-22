import { useState } from 'react';
import { NavLink, Outlet, useNavigate, Link } from 'react-router-dom';
import { Map, CalendarDays, Compass, Settings, LogOut, Menu, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import logo from '../../assets/GlobeTrotter_Logo.png';

export const AppLayout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: Map },
    { name: 'Calendar', path: '/calendar', icon: CalendarDays },
    { name: 'Explore', path: '/explore', icon: Compass },
  ];

  // Show Admin Panel only if user is an admin
  if (user?.is_admin) {
    navItems.push({ name: 'Admin Panel', path: '/admin', icon: Settings });
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-surface border-r border-border-default">
      {/* Logo Area */}
      <div className="p-6 flex items-center gap-3">
        <img src={logo} alt="GlobeTrotter" className="w-8 h-8 object-contain shrink-0" />
        <span className="font-manrope font-bold text-xl text-text-primary tracking-tight">
          GlobeTrotter
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={() => setIsMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
                isActive
                  ? 'bg-primary-soft text-primary'
                  : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
              }`
            }
          >
            <item.icon size={20} />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* User Profile & Settings Bottom Area */}
      <div className="p-4 border-t border-border-subtle">
        <Link 
          to="/profile" 
          onClick={() => setIsMobileMenuOpen(false)}
          className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-hover transition-colors mb-2"
        >
          <div className="w-10 h-10 rounded-full bg-surface-muted overflow-hidden shrink-0 border border-border-default">
            {user?.photo_url ? (
              <img src={user.photo_url} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-primary text-white font-bold">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-text-primary truncate">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-text-secondary truncate">{user?.email}</p>
          </div>
        </Link>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-3 text-sm font-medium text-error hover:bg-error-soft rounded-xl transition-colors"
        >
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </div>
  );

  return (
    // FIXED: Added h-screen and overflow-hidden to lock the layout height
    <div className="flex h-screen overflow-hidden bg-background">
      
      {/* Desktop Sidebar (Fixed in place) */}
      <aside className="hidden md:block w-72 shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile Header & Menu */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-surface border-b border-border-default z-30 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <img src={logo} alt="GlobeTrotter" className="w-8 h-8 object-contain shrink-0" />
          <span className="font-manrope font-bold text-lg text-text-primary">GlobeTrotter</span>
        </div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-text-secondary">
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-20 bg-background/80 backdrop-blur-sm pt-16">
          <div className="h-full w-4/5 max-w-sm bg-surface shadow-2xl animate-in slide-in-from-left duration-300">
            <SidebarContent />
          </div>
        </div>
      )}

      {/* Main Content Area (This alone will scroll now) */}
      <main className="flex-1 overflow-y-auto pt-16 md:pt-0">
        <div className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
      
    </div>
  );
};