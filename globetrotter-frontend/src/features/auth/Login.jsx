import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { login } from './authApi';
import { useAuthStore } from '../../store/authStore';
import logo from '../../assets/GlobeTrotter_Logo.png';

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const setToken = useAuthStore((state) => state.setToken);
  
  const [globalError, setGlobalError] = useState("");
  const successMessage = location.state?.message;

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data) => {
    try {
      setGlobalError("");
      const response = await login(data.email, data.password);
      setToken(response.access_token);
      navigate('/dashboard');
    } catch (error) {
      setGlobalError(error.response?.data?.detail || "Invalid email or password.");
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <div className="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-100">
          <div className="mb-8">
            <img 
              src={logo} 
              alt="GlobeTrotter" 
              className="h-10 w-auto mb-10" 
              onError={(e) => {
                e.target.style.display = 'none';
              }} 
            />
            <h1 className="text-3xl font-bold tracking-tight text-text-primary">
              Welcome back
            </h1>
            <p className="mt-2 text-sm text-text-secondary">
              Sign in to manage your personalized travel plans.
            </p>
          </div>

          {successMessage && (
            <div className="bg-success-soft text-success px-4 py-3 rounded-xl mb-6 text-sm border border-success/20">
              {successMessage}
            </div>
          )}

          {globalError && (
            <div className="bg-error-soft text-error px-4 py-3 rounded-xl mb-6 text-sm border border-error/20">
              {globalError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <Input 
              label="Email Address" 
              type="email" 
              placeholder="name@example.com"
              {...register('email')} 
              error={errors.email?.message} 
            />
            
            <div className="space-y-1">
              <Input 
                label="Password" 
                type="password" 
                placeholder="••••••••"
                {...register('password')} 
                error={errors.password?.message} 
              />
              <div className="flex justify-end">
                <Link to="#" className="text-sm font-medium text-primary hover:text-primary-hover">
                  Forgot password?
                </Link>
              </div>
            </div>
            
            <Button type="submit" size="lg" className="w-full mt-4" isLoading={isSubmitting}>
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-8">
            Don't have an account?{' '}
            <Link to="/signup" className="font-semibold text-primary hover:text-primary-hover transition-colors">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>

      <div className="relative hidden w-0 flex-1 lg:block bg-surface-muted">
        <div className="absolute inset-0 h-full w-full object-cover bg-primary-soft flex items-center justify-center p-12">
           {/* Placeholder for a beautiful travel image. We use CSS gradient to keep it premium until you add a real photo */}
           <div className="absolute inset-0 bg-linear-to-br from-primary/10 to-accent/10 mix-blend-multiply" />
           <div className="relative z-10 max-w-xl text-center">
             <h2 className="text-4xl font-bold text-primary mb-6">
                Design your dream journey.
             </h2>
             <p className="text-lg text-text-secondary leading-relaxed">
                Explore global destinations, visualize your itinerary, and manage your travel budget all in one beautiful platform.
             </p>
           </div>
        </div>
      </div>
    </div>
  );
};