import React from 'react';
import { useUIStore } from '../store/ui-store';
import { GoalInput } from './GoalInput';
import { PromptSuggestions } from './PromptSuggestions';
import { PipelineProgress } from './PipelineProgress';
import { ShoppingSummary } from './ShoppingSummary';
import { CartDisplay } from './CartDisplay';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';
import { ErrorState } from './ErrorState';

export function ShoppingLayout() {
  const { stage, loading, error, finalCart } = useUIStore();

  const isIdle = stage === 'IDLE' && !loading && !error && !finalCart;
  const isError = stage === 'ERROR' || error;
  const isLoading = loading && !isError;
  const isComplete = stage === 'COMPLETE' && finalCart;

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Hero / Input Section */}
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">AI Shopping Assistant</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Describe your grocery needs and let the AI build your perfect cart.</p>
        </div>
        <GoalInput />
        <PromptSuggestions />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-8">
        
        {/* Left Column: Progress Sidebar (only visible when active/completed) */}
        {(!isIdle && !isError) && (
          <div className="lg:col-span-4">
            <div className="sticky top-6">
              <PipelineProgress />
            </div>
          </div>
        )}

        {/* Right Column: Results Area */}
        <div className={isIdle || isError ? "lg:col-span-12" : "lg:col-span-8"}>
          <div className="space-y-8">
            {isIdle && <EmptyState />}
            
            {isError && <ErrorState />}
            
            {isLoading && <LoadingState />}
            
            {isComplete && (
              <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <ShoppingSummary />
                <CartDisplay />
              </div>
            )}
          </div>
        </div>
        
      </div>
    </div>
  );
}
