import Link from "next/link";
import { ArrowRight, ShoppingBag } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-white font-sans selection:bg-indigo-500/30">
      {/* Navbar */}
      <header className="flex items-center justify-between px-8 py-6 border-b border-zinc-800/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="bg-indigo-500 p-2 rounded-xl">
            <ShoppingBag className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">CartPilot</span>
        </div>
        <div className="flex items-center gap-4">
          <Link 
            href="/login" 
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors"
          >
            Sign in
          </Link>
          <Link 
            href="/signup" 
            className="text-sm font-medium bg-white text-black px-4 py-2 rounded-full hover:bg-zinc-200 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 relative overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/20 rounded-full blur-[120px] -z-10" />
        
        <div className="max-w-3xl space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-sm text-zinc-400 mb-4">
            <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Powered by Autonomous AI
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white to-zinc-500">
            Your personal AI <br /> shopping concierge.
          </h1>
          
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            Tell CartPilot what you need, and our autonomous agents will research, compare, and assemble the perfect cart for your exact budget.
          </p>
          
          <div className="flex items-center justify-center pt-8">
            <Link 
              href="/signup"
              className="group flex items-center gap-2 bg-indigo-600 text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-indigo-500 transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_-10px_rgba(99,102,241,0.5)]"
            >
              Start Shopping
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
