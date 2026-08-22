import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './features/auth/Login';
import { Signup } from './features/auth/Signup';
import { ForgotPassword } from './features/auth/ForgotPassword';
import { ResetPassword } from './features/auth/ResetPassword';
import { Dashboard } from './features/trips/Dashboard';
import { CreateTrip } from './features/trips/CreateTrip';
import { ItineraryBuilder } from './features/itinerary/ItineraryBuilder';
import { TripBudget } from './features/budget/TripBudget'; // <--- NEW
import { AppLayout } from './components/layouts/AppLayout';
import { useAuthStore } from './store/authStore';

const ProtectedRoute = ({ children }) => {
  const token = useAuthStore(state => state.token);
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* App Shell Routes */}
        <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          
          <Route path="trips/new" element={<CreateTrip />} />
          <Route path="trips/:tripId/itinerary" element={<ItineraryBuilder />} />
          <Route path="trips/:tripId/budget" element={<TripBudget />} /> {/* <--- NEW */}
        </Route>
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}