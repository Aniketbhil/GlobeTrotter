import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getCities, addStop } from './itineraryApi';

const stopSchema = z.object({
  city_id: z.string().min(1, "Please select a city"),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
  budget_estimate: z.preprocess((val) => (val === "" ? undefined : Number(val)), z.number().optional()),
  notes: z.string().optional(),
}).refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
  message: "End date cannot be before start date",
  path: ["end_date"],
});

export const AddStopModal = ({ isOpen, onClose, tripId, onStopAdded }) => {
  const [cities, setCities] = useState([]);
  const [globalError, setGlobalError] = useState("");
  const [isLoadingCities, setIsLoadingCities] = useState(true);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(stopSchema)
  });

  useEffect(() => {
    if (isOpen) {
      setIsLoadingCities(true);
      getCities()
        .then(data => setCities(data.items || []))
        .catch(() => setGlobalError("Could not connect to backend to fetch cities."))
        .finally(() => setIsLoadingCities(false));
      reset();
      setGlobalError("");
    }
  }, [isOpen, reset]);

  const onSubmit = async (data) => {
    try {
      setGlobalError("");
      await addStop(tripId, data);
      onStopAdded(); 
      onClose();
    } catch (error) {
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to add stop.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Travel Stop">
      {globalError && (
        <div className="bg-error-soft text-error px-4 py-3 rounded-xl mb-4 text-sm border border-error/20">
          {globalError}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-text-primary">Destination City *</label>
          <select 
            className="h-10 w-full rounded-xl border border-border-strong bg-input-background px-3 text-sm text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus"
            {...register('city_id')}
            disabled={isLoadingCities || cities.length === 0}
          >
            <option value="">{isLoadingCities ? "Loading cities..." : "Select a city..."}</option>
            {cities.map(c => (
              <option key={c.id} value={c.id}>{c.name}, {c.country}</option>
            ))}
          </select>
          {errors.city_id && <span className="text-sm text-error">{errors.city_id.message}</span>}
          
          {/* Warning if Database is empty */}
          {!isLoadingCities && cities.length === 0 && (
            <span className="text-sm text-warning font-medium mt-1 bg-warning-soft p-2 rounded-lg">
              ⚠️ Database is empty. Please ask Aniket to add a City via the backend API first.
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input label="Start Date *" type="date" {...register('start_date')} error={errors.start_date?.message} />
          <Input label="End Date *" type="date" {...register('end_date')} error={errors.end_date?.message} />
        </div>

        <Input label="Budget Estimate (Optional)" type="number" placeholder="0.00" {...register('budget_estimate')} error={errors.budget_estimate?.message} />
        <Input label="Notes (Optional)" placeholder="Flight details, hotel names..." {...register('notes')} error={errors.notes?.message} />
        
        <div className="pt-4 flex justify-end gap-3">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" isLoading={isSubmitting} disabled={cities.length === 0}>Save Stop</Button>
        </div>
      </form>
    </Modal>
  );
};