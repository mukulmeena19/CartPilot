import React from 'react';
import { Card } from '@/shared/ui/primitives';

export function EmptyState() {
  return (
    <Card className="flex flex-col items-center justify-center p-12 text-center border-dashed bg-gray-50/50 dark:bg-gray-900/50">
      <div className="rounded-full bg-indigo-100 p-4 dark:bg-indigo-900/20 mb-4">
        <svg className="w-8 h-8 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-2">Ready to plan your groceries?</h3>
      <p className="text-gray-500 dark:text-gray-400 max-w-sm mb-6">
        Describe what you need, your budget, and any dietary preferences. Our AI will optimize the perfect cart for you.
      </p>
    </Card>
  );
}
