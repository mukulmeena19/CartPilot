import { create } from 'zustand';
import { PipelineStage, AIState } from '../types';

interface UIStore extends AIState {
  setQuery: (query: string) => void;
  setStage: (stage: PipelineStage) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setFinalCart: (cart: any) => void;
  reset: () => void;
}

const initialState: AIState = {
  query: "",
  stage: "IDLE",
  loading: false,
  error: null,
  finalCart: null,
};

export const useUIStore = create<UIStore>((set) => ({
  ...initialState,
  
  setQuery: (query) => set({ query }),
  setStage: (stage) => set({ stage }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false, stage: "ERROR" }),
  setFinalCart: (finalCart) => set({ finalCart, loading: false, stage: "COMPLETE" }),
  
  reset: () => set(initialState),
}));
