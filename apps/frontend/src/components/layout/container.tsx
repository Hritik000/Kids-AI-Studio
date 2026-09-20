import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  fluid?: boolean;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
  fluid = false
}) => {
  return (
    <div
      className={`${className}
        ${fluid
          ? 'w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-10'
          : 'w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'}
      `}
    >
      {children}
    </div>
  );
};