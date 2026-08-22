import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { resetPassword } from './authApi';
import logo from '../../assets/GlobeTrotter_Logo.png';

const resetSchema = z.object({
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string()
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

export const ResetPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [globalError, setGlobalError] = useState("");
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(resetSchema)
  });

  const onSubmit = async (data) => {
    try {
      setGlobalError("");
      await resetPassword(token, data.new_password);
      navigate('/login', { state: { message: "Password reset successfully! Please sign in." } });
    } catch (error) {
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to reset password. The link might be expired.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 animate-in fade-in zoom-in-95 duration-300">
      <div className="w-full max-w-110 bg-surface p-8 rounded-2xl shadow-sm border border-border-default">
        <div className="text-center mb-8">
          <img src={logo} alt="GlobeTrotter" className="h-10 w-auto mx-auto mb-6" onError={(e) => e.target.style.display = 'none'} />
          <h1 className="text-2xl font-bold text-text-primary mb-2">Reset Password</h1>
          <p className="text-text-secondary">Create a new secure password</p>
        </div>

        {globalError && (
          <div className="bg-error-soft text-error px-4 py-3 rounded-xl mb-6 text-sm border border-error/20">
            {globalError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Input 
            label="New Password" 
            type="password" 
            {...register('new_password')} 
            error={errors.new_password?.message} 
          />
          <Input 
            label="Confirm Password" 
            type="password" 
            {...register('confirm_password')} 
            error={errors.confirm_password?.message} 
          />
          <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
            Reset Password
          </Button>
        </form>
      </div>
    </div>
  );
};