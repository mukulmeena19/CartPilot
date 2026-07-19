import { ArrowUpRight, TrendingUp, Users, Target } from "lucide-react";

export function AdminDashboard() {
  const stats = [
    { label: "Recommendation CTR", value: "24.8%", icon: <Target className="w-5 h-5" />, trend: "+2.1%" },
    { label: "Acceptance Rate", value: "68.2%", icon: <Users className="w-5 h-5" />, trend: "+5.4%" },
    { label: "Avg Basket Size", value: "₹1,840", icon: <TrendingUp className="w-5 h-5" />, trend: "+12%" },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto w-full h-full bg-background text-foreground overflow-y-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">CartPilot Analytics</h1>
          <p className="text-secondary">Overview of AI performance and user engagement.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-card border border-border/50 p-6 rounded-3xl">
            <div className="flex items-center justify-between mb-4 text-secondary">
              <span className="font-medium text-sm uppercase tracking-wider">{stat.label}</span>
              {stat.icon}
            </div>
            <div className="flex items-baseline gap-3">
              <span className="text-4xl font-bold">{stat.value}</span>
              <span className="text-success text-sm font-medium flex items-center">
                <ArrowUpRight className="w-3 h-3 mr-0.5" />
                {stat.trend}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border/50 p-6 rounded-3xl min-h-[300px]">
          <h3 className="font-semibold mb-4 text-lg">Top Products Suggested</h3>
          <div className="space-y-4">
            {["Amul High Protein Milk", "Whole Wheat Pasta", "Greek Yogurt", "Chicken Breast", "Tofu"].map((p, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-border/30 last:border-0">
                <span className="text-secondary font-medium">{p}</span>
                <span className="text-foreground font-semibold">{Math.floor(Math.random() * 500 + 100)} views</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-card border border-border/50 p-6 rounded-3xl min-h-[300px]">
          <h3 className="font-semibold mb-4 text-lg">Trending Cuisines</h3>
          <div className="space-y-4">
            {["Italian", "Mexican", "North Indian", "Healthy", "Vegan"].map((p, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-border/30 last:border-0">
                <span className="text-secondary font-medium">{p}</span>
                <div className="w-1/2 bg-muted h-2 rounded-full overflow-hidden">
                  <div className="bg-primary h-full rounded-full" style={{ width: `${Math.random() * 60 + 20}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
