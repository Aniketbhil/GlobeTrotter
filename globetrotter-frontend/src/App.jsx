import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './features/auth/Login';
import { Signup } from './features/auth/Signup';
import { Dashboard } from './features/trips/Dashboard';
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
        
        {/* App Shell Routes */}
        <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          {/* We will add /calendar, /explore, /profile, and /trips/new in upcoming chapters */}
        </Route>
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}