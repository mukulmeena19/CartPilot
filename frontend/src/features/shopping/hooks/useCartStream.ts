import { useCallback } from 'react';
import { useUIStore } from '../store/ui-store';
import { generateCartStream } from '../api/generateCart';
// Note: Depending on your auth setup, you may need a token hook here.

export const useCartStream = () => {
  const { 
    setQuery, 
    setStage, 
    setLoading, 
    setError, 
    setFinalCart 
  } = useUIStore();

  const generateCart = useCallback(async (query: string, token?: string) => {
    // Reset state for a new run
    setQuery(query);
    setLoading(true);
    setError(null);
    setStage('IDLE');
    setFinalCart(null);

    await generateCartStream({
      query,
      token,
      onProgress: (stage) => {
        setStage(stage);
      },
      onComplete: (cart) => {
        setFinalCart(cart);
      },
      onError: (err) => {
        setError(err.message || 'An unknown error occurred.');
      }
    });
  }, [setQuery, setLoading, setError, setStage, setFinalCart]);

  return { generateCart };
};
