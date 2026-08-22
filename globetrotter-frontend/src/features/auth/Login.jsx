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
    <div className="flex min-h-screen bg-background overflow-hidden">
      {/* Image Side (Left) */}
      <div className="relative hidden lg:flex lg:w-1/2 bg-surface-muted border-r border-border-default animate-in slide-in-from-left-8 fade-in duration-500">
        <div className="absolute inset-0 h-full w-full">
           <img 
            src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop" 
            alt="Travel map" 
            className="h-full w-full object-cover"
          />
          {/* Dark overlay for contrast */}
          <div className="absolute inset-0 bg-black/20" />
          {/* Dark gradient for text readability */}
          <div className="absolute inset-0 bg-linear-to-t from-black/80 via-black/40 to-transparent flex flex-col justify-end p-12 xl:p-16">
             <h2 className="text-4xl font-bold text-white mb-4">Design your dream journey.</h2>
             <p className="text-lg text-white/90 max-w-lg">Explore global destinations, visualize your itinerary, and manage your budget seamlessly.</p>
          </div>
        </div>
      </div>

      {/* Form Side (Right) */}
      <div className="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:w-1/2 lg:px-20 xl:px-24 z-10 bg-surface animate-in slide-in-from-right-8 fade-in duration-500">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8">
            <img src={logo} alt="GlobeTrotter" className="h-10 w-auto mb-8" onError={(e) => e.target.style.display = 'none'} />
            <h1 className="text-3xl font-bold tracking-tight text-text-primary">Welcome back</h1>
            <p className="mt-2 text-sm text-text-secondary">Sign in to manage your personalized travel plans.</p>
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
              {...register('email')} 
              error={errors.email?.message} 
            />
            
            <div className="space-y-1">
              <Input 
                label="Password" 
                type="password" 
                {...register('password')} 
                error={errors.password?.message} 
              />
              <div className="flex justify-end mt-1">
                <Link to="/forgot-password" className="text-sm font-medium text-primary hover:text-primary-hover">
                  Forgot password?
                </Link>
              </div>
            </div>
            
            <Button type="submit" size="lg" className="w-full mt-6" isLoading={isSubmitting}>
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
    </div>
  );
};