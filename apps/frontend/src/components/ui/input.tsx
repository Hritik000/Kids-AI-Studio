import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'outline' | 'filled';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  inputMode?: 'none' | 'text' | 'decimal' | 'numeric' | 'tel' | 'search' | 'email' | 'url';
}

export const Input: React.FC<InputProps> = ({
  className = '',
  variant = 'default',
  size = 'md',
  ...props
}) => {
  const baseClasses = `
    flex w-full min-w-0
    rounded-md border
    bg-background px-3 py-2
    text-sm ring-offset-background
    placeholder:text-muted-foreground
    focus:outline-none focus:ring-2 focus:ring-primary
    focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50
  `;

  const variantClasses = {
    default: 'border-input',
    outline: 'border-input',
    filled: 'bg-accent/5 border-accent/50',
  }[variant];

  const sizeClasses = {
    sm: 'h-9 px-2 text-sm',
    md: 'h-10 px-3 text-base',
    lg: 'h-11 px-4 text-lg',
  }[size];

  return (
    <input
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
      {...props}
    />
  );
};