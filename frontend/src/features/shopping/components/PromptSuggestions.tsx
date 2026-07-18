import React from 'react';
import { useUIStore } from '../store/ui-store';
import { cn } from '@/shared/ui/primitives';

const SUGGESTIONS = [
  "Weekly Groceries",
  "Budget Shopping under ₹1000",
  "High Protein Meal Prep",
  "Vegetarian Family of 4",
  "Keto Snacks",
  "Quick Dinner Essentials"
];

export function PromptSuggestions() {
  const { setQuery, loading } = useUIStore();

  if (loading) return null;

  return (
    <div className="flex flex-wrap gap-2 pt-2">
      {SUGGESTIONS.map((suggestion) => (
        <button
          key={suggestion}
          onClick={() => setQuery(suggestion)}
          className={cn(
            "inline-flex items-center rounded-full border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm transition-all",
            "hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200",
            "dark:border-gray-800 dark:bg-gray-950 dark:text-gray-300 dark:hover:bg-indigo-900/30 dark:hover:text-indigo-300 dark:hover:border-indigo-800"
          )}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
