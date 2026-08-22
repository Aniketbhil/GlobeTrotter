import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Auth Pages
import { Login } from './features/auth/Login';
import { Signup } from './features/auth/Signup';
import { ForgotPassword } from './features/auth/ForgotPassword';
import { ResetPassword } from './features/auth/ResetPassword';

// Main Application Pages
import { Dashboard } from './features/trips/Dashboard';
import { CreateTrip } from './features/trips/CreateTrip';
import { ItineraryBuilder } from './features/itinerary/ItineraryBuilder';
import { TripBudget } from './features/budget/TripBudget';
import { CalendarView } from './features/calendar/CalendarView';
import { Profile } from './features/profile/Profile';

// Sharing & Admin Pages
import { PublicItinerary } from './features/sharing/PublicItinerary';
import { AdminDashboard } from './features/admin/AdminDashboard';

// Layout & State
import { AppLayout } from './components/layouts/AppLayout';
import { useAuthStore } from './store/authStore';
import { useThemeStore } from './store/themeStore';

// Standard Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const token = useAuthStore(state => state.token);
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

// Admin Only Route Wrapper
const AdminRoute = ({ children }) => {
  // FIXED: Separated the selectors to prevent Zustand infinite loop crashes
  const token = useAuthStore(state => state.token);
  const user = useAuthStore(state => state.user);

  if (!token) return <Navigate to="/login" replace />;
  
  // Only redirect to dashboard if we have the user data AND they are explicitly not an admin
  if (user && user.is_admin === false) return <Navigate to="/dashboard" replace />;
  
  return children;
};

export default function App() {
  const initTheme = useThemeStore(state => state.initTheme);

  // Initialize light/dark theme on application load
  useEffect(() => {
    initTheme();
  }, [initTheme]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Unauthenticated Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* PUBLIC ROUTE - Anyone can view this without logging in */}
        <Route path="/shared/:slug" element={<PublicItinerary />} />
        
        {/* Protected App Shell Routes (Requires Login) */}
        <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          {/* Main Navigation */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="calendar" element={<CalendarView />} />
          <Route path="profile" element={<Profile />} />
          
          {/* Trip Workflows */}
          <Route path="trips/new" element={<CreateTrip />} />
          <Route path="trips/:tripId/itinerary" element={<ItineraryBuilder />} />
          <Route path="trips/:tripId/budget" element={<TripBudget />} />

          {/* Admin Tools */}
          <Route path="admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        </Route>
        
        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}