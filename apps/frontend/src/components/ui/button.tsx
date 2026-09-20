import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  leftIcon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  rightIcon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  loading?: boolean;
  className?: string;
  asChild?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  loading = false,
  asChild = false,
  ...props
}) => {
  const BaseComponent = asChild ? React.Fragment : 'button';

  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-medium rounded-md
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
  `;

  const variantClasses = {
    primary: `
      bg-primary text-primary-foreground
      hover:bg-primary/90
      focus-visible:ring-primary/50
    `,
    secondary: `
      bg-secondary text-secondary-foreground
      hover:bg-secondary/90
      focus-visible:ring-secondary/50
    `,
    outline: `
      border border-input
      bg-background
      hover:bg-accent
      focus-visible:ring-primary/50
    `,
    ghost: `
      hover:bg-accent hover:text-accent-foreground
      focus-visible:ring-primary/50
    `,
  }[variant];

  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 text-base',
    lg: 'h-11 px-5 text-lg',
  }[size];

  return (
    <BaseComponent
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
      {...props}
      disabled={loading}
    >
      {loading ? (
        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : (
        <>
          {props.leftIcon && <props.leftIcon className="w-4 h-4 shrink-0" />}
          {children}
          {props.rightIcon && <props.rightIcon className="w-4 h-4 shrink-0" />}
        </>
      )}
    </BaseComponent>
  );
};