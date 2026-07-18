import React from 'react';
import { useUIStore } from '../store/ui-store';
import { PipelineStage } from '../types';
import { cn, Card } from '@/shared/ui/primitives';

const STAGES: { id: PipelineStage; title: string; description: string }[] = [
  { id: 'UNDERSTANDING', title: 'Understanding Goal', description: 'Analyzing your shopping request...' },
  { id: 'PLANNING', title: 'Planning Budget', description: 'Allocating your grocery budget...' },
  { id: 'RETRIEVAL', title: 'Finding Products', description: 'Searching local catalogs...' },
  { id: 'VERIFICATION', title: 'Verifying Inventory', description: 'Checking stock and availability...' },
  { id: 'MEMORY', title: 'Applying Preferences', description: 'Loading your brand and dietary history...' },
  { id: 'OPTIMIZATION', title: 'Optimizing Cart', description: 'Calculating the perfect combinations...' },
  { id: 'EXPLAINABILITY', title: 'Generating Explanations', description: 'Writing reasoning for selections...' }
];

export function PipelineProgress() {
  const { stage, loading } = useUIStore();

  if (!loading && stage !== 'COMPLETE') return null;

  const currentStageIndex = STAGES.findIndex(s => s.id === stage);
  const isComplete = stage === 'COMPLETE';

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-6">AI Pipeline Progress</h3>
      <div className="space-y-4">
        {STAGES.map((s, index) => {
          const isPast = isComplete || (currentStageIndex > -1 && index < currentStageIndex);
          const isCurrent = !isComplete && currentStageIndex === index;
          
          return (
            <div key={s.id} className="flex items-start gap-4">
              <div className="flex flex-col items-center mt-1">
                <div className={cn(
                  "flex items-center justify-center w-6 h-6 rounded-full border-2 transition-colors duration-300",
                  isPast ? "bg-emerald-500 border-emerald-500 text-white" :
                  isCurrent ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30" :
                  "border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950"
                )}>
                  {isPast ? (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : isCurrent ? (
                    <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  ) : null}
                </div>
                {index < STAGES.length - 1 && (
                  <div className={cn(
                    "w-0.5 h-8 mt-2 transition-colors duration-300",
                    isPast ? "bg-emerald-500" : "bg-gray-200 dark:bg-gray-800"
                  )} />
                )}
              </div>
              <div className="flex-1 pb-2">
                <p className={cn(
                  "text-sm font-medium transition-colors duration-300",
                  isPast ? "text-gray-900 dark:text-gray-200" :
                  isCurrent ? "text-indigo-600 dark:text-indigo-400" :
                  "text-gray-400 dark:text-gray-600"
                )}>
                  {s.title}
                </p>
                <p className={cn(
                  "text-xs mt-0.5 transition-colors duration-300",
                  isCurrent ? "text-indigo-500/80 dark:text-indigo-400/80" : "text-gray-500 dark:text-gray-500"
                )}>
                  {s.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
