"use client";

import { motion } from "framer-motion";
import { CheckCircle2, CircleDashed } from "lucide-react";

export interface ThinkingStep {
  id: string;
  label: string;
  status: "pending" | "active" | "completed";
}

export function ThinkingTimeline({ steps }: { steps: ThinkingStep[] }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="flex flex-col gap-3 py-2 px-1 text-sm text-secondary">
      {steps.map((step, idx) => (
        <motion.div 
          key={step.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
          className={`flex items-center gap-3 ${
            step.status === "active" ? "text-primary font-medium" : ""
          } ${step.status === "completed" ? "text-foreground" : ""}`}
        >
          {step.status === "completed" ? (
            <CheckCircle2 className="w-4 h-4 text-success" />
          ) : step.status === "active" ? (
            <CircleDashed className="w-4 h-4 text-primary animate-spin" />
          ) : (
            <div className="w-4 h-4 rounded-full border border-border/50" />
          )}
          <span>{step.label}</span>
        </motion.div>
      ))}
    </div>
  );
}
