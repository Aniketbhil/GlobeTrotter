import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Camera, Trash2, Moon, Sun } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../store/authStore';
import { useThemeStore } from '../../store/themeStore';
import { updateMe, deleteMe, uploadPhoto, removePhoto, getMe } from '../auth/authApi';

// Schema matches the UserUpdate schema from the backend
const profileSchema = z.object({
  first_name: z.string().min(2, "Required").optional().or(z.literal('')),
  last_name: z.string().min(2, "Required").optional().or(z.literal('')),
  phone_number: z.string().optional().or(z.literal('')),
  city: z.string().optional().or(z.literal('')),
  country: z.string().optional().or(z.literal('')),
  additional_info: z.string().optional().or(z.literal('')),
  language: z.string().optional().or(z.literal('')),
});

export const Profile = () => {
  const { user, setUser, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const [status, setStatus] = useState({ type: "", message: "" });
  const [isPhotoUploading, setIsPhotoUploading] = useState(false);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      phone_number: user?.phone_number || '',
      city: user?.city || '',
      country: user?.country || '',
      additional_info: user?.additional_info || '',
      language: user?.language || 'English',
    }
  });

  // Ensure form updates if user data changes
  useEffect(() => {
    if (user) reset(user);
  }, [user, reset]);

  const onSubmit = async (data) => {
    try {
      setStatus({ type: "", message: "" });
      // Remove empty strings so we don't overwrite with blanks unintentionally
      const cleanData = Object.fromEntries(Object.entries(data).filter(([_, v]) => v !== ''));
      const updatedUser = await updateMe(cleanData);
      setUser(updatedUser);
      setStatus({ type: "success", message: "Profile updated successfully!" });
    } catch (error) {
      setStatus({ type: "error", message: "Failed to update profile." });
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setIsPhotoUploading(true);
      const updatedUser = await uploadPhoto(file);
      setUser(updatedUser);
      setStatus({ type: "success", message: "Photo uploaded!" });
    } catch (error) {
      setStatus({ type: "error", message: "Failed to upload photo." });
    } finally {
      setIsPhotoUploading(false);
    }
  };

  const handlePhotoRemove = async () => {
    try {
      const updatedUser = await removePhoto();
      setUser(updatedUser);
      setStatus({ type: "success", message: "Photo removed." });
    } catch (error) {
      setStatus({ type: "error", message: "Failed to remove photo." });
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm("Are you absolutely sure you want to delete your account? This action cannot be undone and will delete all your trips.")) {
      try {
        await deleteMe();
        logout(); // Automatically redirects to login via App.jsx
      } catch (error) {
        setStatus({ type: "error", message: "Failed to delete account." });
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500 pb-16">
      
      <div className="mb-6">
        <h1 className="text-3xl font-bold font-manrope text-text-primary">Profile & Settings</h1>
        <p className="text-text-secondary mt-1">Manage your personal information and application preferences.</p>
      </div>

      {status.message && (
        <div className={`px-4 py-3 rounded-xl mb-6 text-sm border ${status.type === 'success' ? 'bg-success-soft text-success border-success/30' : 'bg-error-soft text-error border-error/30'}`}>
          {status.message}
        </div>
      )}

      {/* Profile Photo Section */}
      <Card>
        <CardContent className="p-6 flex flex-col sm:flex-row items-center gap-6">
          <div className="relative w-24 h-24 rounded-full overflow-hidden bg-surface-muted border-2 border-border-default shrink-0">
            {user?.photo_url ? (
              <img src={user.photo_url} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-primary text-text-on-primary text-2xl font-bold">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
            )}
          </div>
          
          <div className="flex-1 text-center sm:text-left">
            <h3 className="text-lg font-semibold text-text-primary">Profile Picture</h3>
            <p className="text-sm text-text-secondary mb-3">Upload a new avatar. Max size 2MB.</p>
            <div className="flex justify-center sm:justify-start gap-3">
              <div className="relative">
                <Input type="file" accept="image/*" onChange={handlePhotoUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" disabled={isPhotoUploading} />
                <Button variant="secondary" className="gap-2 pointer-events-none" isLoading={isPhotoUploading}>
                  <Camera size={16} /> Change Photo
                </Button>
              </div>
              {user?.photo_url && (
                <Button variant="ghost" aria-label="Remove photo" className="text-error hover:text-error hover:bg-error-soft transition-colors" onClick={handlePhotoRemove}>
                  Remove
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Edit Form Section */}
      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-bold font-manrope text-text-primary mb-4">Personal Information</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="First Name" {...register('first_name')} error={errors.first_name?.message} />
              <Input label="Last Name" {...register('last_name')} error={errors.last_name?.message} />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Email Address" value={user?.email || ''} disabled className="bg-surface-muted opacity-70 cursor-not-allowed" />
              <Input label="Phone Number" {...register('phone_number')} error={errors.phone_number?.message} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="City" {...register('city')} error={errors.city?.message} />
              <Input label="Country" {...register('country')} error={errors.country?.message} />
            </div>

            <Input label="Preferred Language" {...register('language')} error={errors.language?.message} />
            <Input label="Additional Information" {...register('additional_info')} error={errors.additional_info?.message} />

            <div className="pt-4 flex justify-end">
              <Button type="submit" isLoading={isSubmitting}>Save Changes</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Application Preferences (Theme Toggle) */}
      <Card>
        <CardContent className="p-6 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold font-manrope text-text-primary">Appearance</h2>
            <p className="text-sm text-text-secondary mt-1">Toggle between Light and Dark mode.</p>
          </div>
          <Button aria-label="Toggle theme" variant="secondary" onClick={toggleTheme} className="gap-2 transition-all duration-500 ease-in-out">
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            {theme === 'light' ? 'Switch to Dark' : 'Switch to Light'}
          </Button>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-error/30">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold font-manrope text-error">Danger Zone</h2>
          <p className="text-sm text-text-secondary mt-1 mb-4">
            Once you delete your account, there is no going back. All your itineraries and budgets will be wiped.
          </p>
          <Button onClick={handleDeleteAccount} className="bg-error hover:bg-error-strong transition-colors text-white gap-2">
            <Trash2 size={16} /> Delete Account
          </Button>
        </CardContent>
      </Card>

    </div>
  );
};