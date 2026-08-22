import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export const Badge = forwardRef(({ className, variant = "default", ...props }, ref) => {
  const variants = {
    default: "bg-surface-hover text-text-secondary",
    primary: "bg-primary-soft text-primary",
    success: "bg-success-soft text-success",
    warning: "bg-warning-soft text-warning",
    error: "bg-error-soft text-error",
  };

  return (
    <div 
      ref={ref} 
      className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className)} 
      {...props} 
    />
  );
});
Badge.displayName = "Badge";