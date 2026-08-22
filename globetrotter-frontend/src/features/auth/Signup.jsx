import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { signup } from './authApi';
import logo from '../../assets/GlobeTrotter_Logo.png';

// Schema matches all 9 backend fields perfectly
const signupSchema = z.object({
  first_name: z.string().min(2, "Required"),
  last_name: z.string().min(2, "Required"),
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Min 8 chars"),
  city: z.string().optional(),
  country: z.string().optional(),
  phone_number: z.string().optional(),
  photo_url: z.string().url("Invalid URL").optional().or(z.literal('')),
  additional_info: z.string().optional(),
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
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to create account.");
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      
      {/* Form Side (Left) - Denser grid to fit all fields without scrolling */}
      <div className="flex flex-1 flex-col justify-center px-4 py-2 sm:px-6 lg:w-1/2 lg:px-12 xl:px-16 z-10 bg-surface overflow-y-auto animate-in slide-in-from-left-8 fade-in duration-500">
        <div className="mx-auto w-full max-w-md my-auto">
          
          <div className="mb-4">
            <img src={logo} alt="GlobeTrotter" className="h-8 w-auto mb-3" onError={(e) => e.target.style.display = 'none'} />
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Create an account</h1>
            <p className="mt-1 text-sm text-text-secondary">Start planning your perfect multi-city trip today.</p>
          </div>

          {globalError && (
            <div className="bg-error-soft text-error px-3 py-2 rounded-xl mb-3 text-sm border border-error/20">
              {globalError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            {/* Row 1 */}
            <div className="grid grid-cols-2 gap-3">
              <Input label="First Name *" {...register('first_name')} error={errors.first_name?.message} />
              <Input label="Last Name *" {...register('last_name')} error={errors.last_name?.message} />
            </div>
            
            {/* Row 2 */}
            <div className="grid grid-cols-2 gap-3">
              <Input label="Email Address *" type="email" {...register('email')} error={errors.email?.message} />
              <Input label="Password *" type="password" {...register('password')} error={errors.password?.message} />
            </div>
            
            {/* Row 3 */}
            <div className="grid grid-cols-2 gap-3">
              <Input label="City (Optional)" {...register('city')} error={errors.city?.message} />
              <Input label="Country (Optional)" {...register('country')} error={errors.country?.message} />
            </div>
            
            {/* Row 4 */}
            <div className="grid grid-cols-2 gap-3">
              <Input label="Phone (Optional)" {...register('phone_number')} error={errors.phone_number?.message} />
              <Input label="Photo URL (Optional)" placeholder="https://..." {...register('photo_url')} error={errors.photo_url?.message} />
            </div>
            
            {/* Row 5 */}
            <Input label="Additional Info (Optional)" {...register('additional_info')} error={errors.additional_info?.message} />
            
            <Button type="submit" size="lg" className="w-full mt-2" isLoading={isSubmitting}>
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-4">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-primary hover:text-primary-hover transition-colors">
              Sign in here
            </Link>
          </p>
        </div>
      </div>

      {/* Image Side (Right) */}
      <div className="relative hidden lg:flex lg:w-1/2 bg-surface-muted border-l border-border-default animate-in slide-in-from-right-8 fade-in duration-500">
        <div className="absolute inset-0 h-full w-full">
          <img 
            src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2074&auto=format&fit=crop" 
            alt="Travel inspiration" 
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute inset-0 bg-linear-to-t from-black/80 via-black/40 to-transparent flex flex-col justify-end p-12 xl:p-16">
             <h2 className="text-4xl font-bold text-white mb-4">Your next adventure awaits.</h2>
             <p className="text-lg text-white/90 max-w-lg">Join a community of travelers organizing trips, optimizing budgets, and sharing experiences.</p>
          </div>
        </div>
      </div>
    </div>
  );
};