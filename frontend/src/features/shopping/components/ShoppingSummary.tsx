import React from 'react';
import { Card } from '@/shared/ui/primitives';
import { useUIStore } from '../store/ui-store';

export function ShoppingSummary() {
  const { finalCart } = useUIStore();

  if (!finalCart) return null;

  const totalBudget = finalCart.total_budget_allocated || 0;
  const totalSpent = finalCart.total_budget_used || 0;
  const savings = totalBudget - totalSpent;
  
  const numCategories = finalCart.categories?.length || 0;
  const numProducts = finalCart.categories?.reduce((acc: number, cat: any) => acc + (cat.selected_items?.length || 0), 0) || 0;
  const confidence = finalCart.optimization_success_rate || 0;

  const metrics = [
    { label: "Budget", value: `₹${totalBudget.toFixed(2)}`, color: "text-gray-900 dark:text-gray-50" },
    { label: "Spent", value: `₹${totalSpent.toFixed(2)}`, color: "text-indigo-600 dark:text-indigo-400" },
    { label: "Saved", value: `₹${Math.max(0, savings).toFixed(2)}`, color: "text-emerald-600 dark:text-emerald-400" },
    { label: "Products", value: numProducts.toString(), color: "text-gray-900 dark:text-gray-50" },
    { label: "Categories", value: numCategories.toString(), color: "text-gray-900 dark:text-gray-50" },
    { label: "Confidence", value: `${confidence.toFixed(0)}%`, color: "text-blue-600 dark:text-blue-400" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {metrics.map((m) => (
        <Card key={m.label} className="p-4 flex flex-col justify-center items-start">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{m.label}</span>
          <span className={`text-2xl font-bold mt-1 ${m.color}`}>{m.value}</span>
        </Card>
      ))}
    </div>
  );
}
