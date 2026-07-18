import React, { useState } from 'react';
import { ProductCard } from './ProductCard';

export function CategorySection({ category }: { category: any }) {
  const [expanded, setExpanded] = useState(true);
  
  const name = category.category_name;
  const budget = category.allocation?.estimated_budget || 0;
  const spent = category.total_cost || 0;
  const items = category.selected_items || [];
  const itemCount = items.length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden dark:border-gray-800 dark:bg-gray-950">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 bg-gray-50/50 hover:bg-gray-50 dark:bg-gray-900/50 dark:hover:bg-gray-900 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">📦</span>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50">{name}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{itemCount} Product{itemCount !== 1 ? 's' : ''}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="hidden sm:flex flex-col items-end">
            <span className="text-xs font-medium text-gray-500 uppercase">Budget</span>
            <span className="text-sm font-semibold text-gray-900 dark:text-gray-300">₹{budget.toFixed(2)}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-xs font-medium text-gray-500 uppercase">Spent</span>
            <span className={`text-sm font-semibold ${spent > budget ? 'text-red-500' : 'text-indigo-600 dark:text-indigo-400'}`}>
              ₹{spent.toFixed(2)}
            </span>
          </div>
          <div className={`transform transition-transform ${expanded ? 'rotate-180' : ''}`}>
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>
      
      {expanded && items.length > 0 && (
        <div className="p-4 bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800 space-y-4">
          {items.map((item: any) => (
            <ProductCard key={item.product_id} product={item} />
          ))}
        </div>
      )}
      
      {expanded && items.length === 0 && (
        <div className="p-8 text-center text-gray-500 bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
          <p className="text-sm">No products found for this category within budget constraints.</p>
        </div>
      )}
    </div>
  );
}
