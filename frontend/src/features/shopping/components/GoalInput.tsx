import React, { useRef, useEffect } from 'react';
import { useUIStore } from '../store/ui-store';
import { useCartStream } from '../hooks/useCartStream';
import { Button, cn } from '@/shared/ui/primitives';

export function GoalInput() {
  const { query, setQuery, loading } = useUIStore();
  const { generateCart } = useCartStream();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [query]);

  const handleSubmit = () => {
    if (query.trim() && !loading) {
      generateCart(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative group">
      <textarea
        ref={textareaRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="I need groceries for a week of high-protein vegetarian meals under ₹2500..."
        disabled={loading}
        rows={1}
        className={cn(
          "w-full resize-none overflow-hidden rounded-xl border border-gray-200 bg-white px-6 py-4 pr-24 text-base shadow-sm",
          "focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
          "dark:border-gray-800 dark:bg-gray-950 dark:text-gray-50 dark:focus:border-indigo-400 dark:focus:ring-indigo-400",
          "transition-all duration-200 disabled:opacity-50",
          query ? "min-h-[100px]" : "min-h-[60px]"
        )}
      />
      <div className="absolute bottom-3 right-3 flex items-center gap-2">
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {query.length > 0 && `${query.length} chars`}
        </span>
        <Button 
          onClick={handleSubmit} 
          disabled={!query.trim() || loading}
          className="rounded-full shadow-sm"
        >
          {loading ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          )}
        </Button>
      </div>
    </div>
  );
}
