import React from 'react';
import { Card, Button } from '@/shared/ui/primitives';
import { useCartStream } from '../hooks/useCartStream';
import { useUIStore } from '../store/ui-store';

export function ErrorState() {
  const { error, query } = useUIStore();
  const { generateCart } = useCartStream();

  return (
    <Card className="flex flex-col items-center justify-center p-8 text-center border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-900/10">
      <div className="rounded-full bg-red-100 p-3 dark:bg-red-900/30 mb-4">
        <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-red-900 dark:text-red-400 mb-2">Something went wrong</h3>
      <p className="text-red-600 dark:text-red-300 max-w-md mb-6 text-sm">
        {error || "An unexpected error occurred during cart generation."}
      </p>
      <Button 
        variant="outline" 
        className="border-red-200 hover:bg-red-100 dark:border-red-800 dark:hover:bg-red-900/50"
        onClick={() => generateCart(query)}
      >
        Retry Optimization
      </Button>
    </Card>
  );
}
