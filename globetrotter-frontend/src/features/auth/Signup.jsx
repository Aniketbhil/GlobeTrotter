import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { signup } from './authApi';
import logo from '../../assets/GlobeTrotter_Logo.png';

const signupSchema = z.object({
  first_name: z.string().min(2, "First name must be at least 2 characters"),
  last_name: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export const Signup = () => {
  const navigate = useNavigate();
  const [globalError, setGlobalError] = useState("");
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(signupSchema)
  });

  const onSubmit = async (data) => {
    try {
      setGlobalError("");
      await signup(data);
      navigate('/login', { state: { message: "Account created successfully! Please sign in." } });
    } catch (error) {
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to create account. Please try again.");
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <div className="relative hidden w-0 flex-1 lg:block bg-surface-muted border-r border-border-default">
        <div className="absolute inset-0 h-full w-full bg-accent-soft flex items-center justify-center p-12">
           <div className="absolute inset-0 bg-linear-to-tr from-accent/5 to-primary/5 mix-blend-multiply" />
           <div className="relative z-10 max-w-xl text-center">
             <h2 className="text-4xl font-bold text-text-primary mb-6">
                Your next adventure awaits.
             </h2>
             <p className="text-lg text-text-secondary leading-relaxed">
                Join a community of travelers organizing multi-city trips, optimizing budgets, and sharing their experiences with ease.
             </p>
           </div>
        </div>
      </div>

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
              Create an account
            </h1>
            <p className="mt-2 text-sm text-text-secondary">
              Start planning your perfect multi-city trip today.
            </p>
          </div>

          {globalError && (
            <div className="bg-error-soft text-error px-4 py-3 rounded-xl mb-6 text-sm border border-error/20">
              {globalError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <Input 
                label="First Name" 
                placeholder="Jane"
                {...register('first_name')} 
                error={errors.first_name?.message} 
              />
              <Input 
                label="Last Name" 
                placeholder="Doe"
                {...register('last_name')} 
                error={errors.last_name?.message} 
              />
            </div>
            
            <Input 
              label="Email Address" 
              type="email" 
              placeholder="name@example.com"
              {...register('email')} 
              error={errors.email?.message} 
            />
            
            <Input 
              label="Password" 
              type="password" 
              placeholder="••••••••"
              {...register('password')} 
              error={errors.password?.message} 
            />
            
            <Button type="submit" size="lg" className="w-full mt-4" isLoading={isSubmitting}>
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-8">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-primary hover:text-primary-hover transition-colors">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};