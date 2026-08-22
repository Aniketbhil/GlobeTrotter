import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Map } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card, CardContent } from '../../components/ui/Card';
import { createTrip } from './tripsApi';

const createTripSchema = z.object({
  name: z.string().min(3, "Trip name must be at least 3 characters"),
  description: z.string().optional(),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
}).refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
  message: "End date cannot be before start date",
  path: ["end_date"],
});

export const CreateTrip = () => {
  const navigate = useNavigate();
  const [globalError, setGlobalError] = useState("");
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(createTripSchema)
  });

  const onSubmit = async (data) => {
    try {
      setGlobalError("");
      const newTrip = await createTrip(data);
      // Navigate to the itinerary builder for this new trip (Chapter 4)
      navigate(`/trips/${newTrip.id}/itinerary`);
    } catch (error) {
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to create trip. Please try again.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-500">
      {/* Breadcrumb / Back Navigation */}
      <Link to="/dashboard" className="inline-flex items-center text-sm font-medium text-text-secondary hover:text-primary transition-colors">
        <ArrowLeft size={16} className="mr-2" />
        Back to Dashboard
      </Link>

      <div>
        <h1 className="text-3xl font-bold font-manrope text-text-primary">Plan a New Trip</h1>
        <p className="text-text-secondary mt-1">Start by giving your journey a name and timeframe.</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          {globalError && (
            <div className="bg-error-soft text-error px-4 py-3 rounded-xl mb-6 text-sm border border-error/20">
              {globalError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <Input 
              label="Trip Name *" 
              placeholder="e.g., Summer in Europe 2026"
              {...register('name')} 
              error={errors.name?.message} 
            />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <Input
                label="Start Date *" 
                type="date"
                {...register('start_date')} 
                error={errors.start_date?.message} 
              />
              <Input 
                label="End Date *" 
                type="date"
                {...register('end_date')} 
                error={errors.end_date?.message} 
              />
            </div>

            <div className="flex flex-col gap-1.5 w-full">
              <label htmlFor="description" className="text-sm font-medium text-text-primary">
                Description (Optional)
              </label>
              <textarea
                id="description"
                rows={4}
                className="flex w-full rounded-xl border border-border-strong bg-input-background px-3 py-2 text-sm text-text-primary transition-colors placeholder:text-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:border-border-focus resize-none"
                placeholder="What is the main goal of this trip?"
                {...register('description')}
              />
              {errors.description?.message && (
                <span className="text-sm text-error mt-1">{errors.description?.message}</span>
              )}
            </div>
            
            <div className="pt-4 flex justify-end">
              <Button type="submit" size="lg" className="w-full md:w-auto gap-2" isLoading={isSubmitting}>
                <Map size={18} />
                Create Itinerary
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};