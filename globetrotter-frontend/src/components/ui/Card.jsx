import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export const Card = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("rounded-2xl border border-border-default bg-surface shadow-sm transition-all", className)} {...props} />
));
Card.displayName = "Card";

export const CardHeader = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
));
CardHeader.displayName = "CardHeader";

export const CardTitle = forwardRef(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn("font-manrope text-lg font-semibold leading-none tracking-tight text-text-primary", className)} {...props} />
));
CardTitle.displayName = "CardTitle";

export const CardContent = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0 text-text-secondary", className)} {...props} />
));
CardContent.displayName = "CardContent";