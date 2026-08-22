import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export const Input = forwardRef(({ 
  className, 
  label, 
  error, 
  id,
  ...props 
}, ref) => {
  const inputId = id || Math.random().toString(36).substring(7);

  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-text-primary">
          {label}
        </label>
      )}
      <input
        id={inputId}
        ref={ref}
        className={cn(
          "flex h-10 w-full rounded-xl border border-border-strong bg-input-background px-3 py-2 text-sm text-text-primary transition-colors",
          "placeholder:text-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:border-border-focus",
          "disabled:cursor-not-allowed disabled:opacity-50",
          error && "border-error-soft focus-visible:ring-error-soft",
          className
        )}
        {...props}
      />
      {error && (
        <span className="text-sm text-error mt-1">{error}</span>
      )}
    </div>
  );
});

Input.displayName = 'Input';