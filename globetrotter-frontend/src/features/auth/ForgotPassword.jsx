import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { forgotPassword } from './authApi';
import logo from '../../assets/GlobeTrotter_Logo.png';

const forgotSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

export const ForgotPassword = () => {
  const [status, setStatus] = useState({ type: "", message: "" });
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(forgotSchema)
  });

  const onSubmit = async (data) => {
    try {
      setStatus({ type: "", message: "" });
      await forgotPassword(data.email);
      setStatus({ type: "success", message: "Password reset link sent to your email." });
    } catch (error) {
      setStatus({ type: "error", message: error.response?.data?.detail?.[0]?.msg || "Failed to send reset link." });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 animate-in fade-in zoom-in-95 duration-300">
      <div className="w-full max-w-110 bg-surface p-8 rounded-2xl shadow-sm border border-border-default">
        <div className="text-center mb-8">
          <img src={logo} alt="GlobeTrotter" className="h-10 w-auto mx-auto mb-6" onError={(e) => e.target.style.display = 'none'} />
          <h1 className="text-2xl font-bold text-text-primary mb-2">Forgot Password</h1>
          <p className="text-text-secondary">Enter your email to receive a reset link</p>
        </div>

        {status.message && (
          <div className={`px-4 py-3 rounded-xl mb-6 text-sm border ${status.type === 'success' ? 'bg-success-soft text-success border-success/20' : 'bg-error-soft text-error border-error/20'}`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Input 
            label="Email Address" 
            type="email" 
            {...register('email')} 
            error={errors.email?.message} 
          />
          <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
            Send Reset Link
          </Button>
        </form>

        <p className="text-center text-sm text-text-secondary mt-6">
          Remembered your password? <Link to="/login" className="text-primary font-medium hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  );
};