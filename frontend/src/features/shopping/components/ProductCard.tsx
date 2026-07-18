import React from 'react';
import { Card, Badge, Button } from '@/shared/ui/primitives';

export function ProductCard({ product }: { product: any }) {
  // Extracting data gracefully
  const pName = product.product_name;
  const pId = product.product_id;
  const explanation = product.explanation_text;
  const rules = product.supporting_rules || [];
  
  // Try to parse out the bullets from the explanation string safely
  // The backend explanation_builder outputs lines, we can split them
  const explanationLines = explanation ? explanation.split('\n').filter((l: string) => l.trim().startsWith('•')) : [];

  return (
    <Card className="flex flex-col md:flex-row overflow-hidden transition-all hover:shadow-md">
      {/* Image Placeholder */}
      <div className="w-full md:w-48 h-48 md:h-auto bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-6 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-800">
        <div className="text-center">
          <div className="text-4xl mb-2 opacity-50">🛒</div>
          <div className="text-xs text-gray-400 font-medium tracking-wide">NO IMAGE</div>
        </div>
      </div>
      
      <div className="flex-1 p-6 flex flex-col">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h4 className="text-lg font-bold text-gray-900 dark:text-gray-50 leading-tight">{pName}</h4>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              {product.verification_status && <Badge variant="success">In Stock</Badge>}
              {product.preference_applied && <Badge variant="warning">Preferred Match</Badge>}
              <Badge variant="secondary">Score: {product.optimization_score?.toFixed(2)}</Badge>
            </div>
          </div>
        </div>

        <div className="mt-4 flex-1">
          <h5 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Why AI selected this</h5>
          <ul className="space-y-1.5">
            {explanationLines.map((line: string, i: number) => (
              <li key={i} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
                <span className="text-emerald-500 mt-0.5">✓</span>
                <span>{line.replace('• ', '')}</span>
              </li>
            ))}
            {explanationLines.length === 0 && (
              <li className="text-sm text-gray-500 italic">Optimized by constraint engine.</li>
            )}
          </ul>
        </div>
        
        <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-800/50">
          <Button variant="ghost" className="text-xs">Replace Product</Button>
          <Button variant="outline" className="text-xs">View Details</Button>
        </div>
      </div>
    </Card>
  );
}
