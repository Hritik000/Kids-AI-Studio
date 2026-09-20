import React from 'react';
import Link from 'next/link';

export const SkipToContent: React.FC = () => {
  return (
    <Link href="#main-content" className="skip-to-content">
      Skip to main content
    </Link>
  );
};