export type PipelineStage = 
  | "IDLE"
  | "UNDERSTANDING"
  | "PLANNING"
  | "RETRIEVAL"
  | "VERIFICATION"
  | "MEMORY"
  | "OPTIMIZATION"
  | "EXPLAINABILITY"
  | "COMPLETE"
  | "ERROR";

export interface AIState {
  query: string;
  stage: PipelineStage;
  loading: boolean;
  error: string | null;
  finalCart: any | null; // Will type properly once we have the shared types
}
