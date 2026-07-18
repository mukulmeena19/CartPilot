import React from 'react';
import { useUIStore } from '../store/ui-store';
import { CategorySection } from './CategorySection';

export function CartDisplay() {
  const { finalCart, loading, stage } = useUIStore();

  if (!finalCart && (loading || stage !== 'IDLE')) return null;
  if (!finalCart) return null;

  const categories = finalCart.categories || [];

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-gray-50 tracking-tight">Your Optimized Cart</h2>
      
      {categories.length === 0 ? (
        <div className="p-8 text-center bg-white rounded-xl border border-gray-200 dark:bg-gray-950 dark:border-gray-800">
          <p className="text-gray-500">The AI could not find any products matching your constraints.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map((cat: any) => (
            <CategorySection key={cat.category_name} category={cat} />
          ))}
        </div>
      )}
    </div>
  );
}
