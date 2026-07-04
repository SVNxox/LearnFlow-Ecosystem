import { InputHTMLAttributes, forwardRef as fRef, TextareaHTMLAttributes } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
}

export const Input = fRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, icon, className = '', ...props }, ref) => (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {icon}
          </span>
        )}
        <input
          ref={ref}
          className={`
            input
            ${icon ? 'pl-9' : ''}
            ${error ? 'border-destructive/50 focus:border-destructive' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {error && <p className="mt-1 text-xs text-destructive font-body">{error}</p>}
      {hint && !error && <p className="mt-1 text-xs text-muted-foreground font-body">{hint}</p>}
    </div>
  )
);
Input.displayName = 'Input';

// Textarea variant
interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = fRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', ...props }, ref) => (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        className={`
          input resize-none
          ${error ? 'border-destructive/50 focus:border-destructive' : ''}
          ${className}
        `}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-destructive font-body">{error}</p>}
    </div>
  )
);
Textarea.displayName = 'Textarea';