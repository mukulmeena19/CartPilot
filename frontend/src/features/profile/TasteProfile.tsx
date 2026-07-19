import { Activity, Apple, Banknote, HeartPulse, Flame } from "lucide-react";

export function TasteProfile() {
  return (
    <div className="p-6 h-full flex flex-col gap-8 text-sm bg-background">
      <div>
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
          <HeartPulse className="w-6 h-6 text-primary" />
          Your Taste Profile
        </h2>
        
        <div className="space-y-6">
          {/* Diet */}
          <div>
            <h3 className="text-secondary font-medium uppercase tracking-widest text-xs mb-3">Diet</h3>
            <div className="flex gap-2">
              <span className="px-3 py-1.5 bg-success/10 text-success border border-success/20 rounded-full font-medium">
                🟢 Vegetarian
              </span>
            </div>
          </div>

          {/* Cuisine */}
          <div>
            <h3 className="text-secondary font-medium uppercase tracking-widest text-xs mb-3">Cuisine</h3>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1.5 bg-muted rounded-full">🍝 Italian</span>
              <span className="px-3 py-1.5 bg-muted rounded-full">🥘 North Indian</span>
              <span className="px-3 py-1.5 bg-muted rounded-full">🌮 Mexican</span>
            </div>
          </div>

          {/* Allergies */}
          <div>
            <h3 className="text-secondary font-medium uppercase tracking-widest text-xs mb-3">Allergies</h3>
            <div className="flex gap-2">
              <span className="px-3 py-1.5 bg-destructive/10 text-destructive border border-destructive/20 rounded-full font-medium">
                ❌ Peanuts
              </span>
            </div>
          </div>
          
          {/* Budget */}
          <div>
            <h3 className="text-secondary font-medium uppercase tracking-widest text-xs mb-3">Budget</h3>
            <div className="flex items-center gap-2 px-4 py-3 bg-muted rounded-2xl">
              <Banknote className="w-5 h-5 text-warning" />
              <span className="font-semibold text-lg">₹2500 <span className="text-secondary text-sm font-normal">/ order</span></span>
            </div>
          </div>

          {/* Goal */}
          <div>
            <h3 className="text-secondary font-medium uppercase tracking-widest text-xs mb-3">Goal</h3>
            <div className="flex items-center gap-2 px-4 py-3 bg-primary/10 border border-primary/20 rounded-2xl text-primary font-medium">
              <Activity className="w-5 h-5" />
              Muscle Gain
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
