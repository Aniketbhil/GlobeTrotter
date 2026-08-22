import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './features/auth/Login';
import { Signup } from './features/auth/Signup';
import { useAuthStore } from './store/authStore';

// Temporary Dashboard Placeholder for Chapter 1 testing
const Dashboard = () => {
  const logout = useAuthStore(state => state.logout);
  return (
    <div className="min-h-screen bg-background p-8 flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold text-text-primary mb-4">Dashboard</h1>
      <p className="text-text-secondary mb-8">Login Successful!</p>
      <button 
        onClick={logout} 
        className="px-4 py-2 bg-surface border border-border-default rounded-xl hover:bg-surface-hover"
      >
        Sign Out
      </button>
    </div>
  );
};

// Protected Route Wrapper
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
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        {/* Redirect root to dashboard (which handles auth redirect) */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}