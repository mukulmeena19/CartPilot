import { ChatContainer } from "@/features/chat/ChatContainer";
import { SmartCart } from "@/features/cart/SmartCart";
import { TasteProfile } from "@/features/profile/TasteProfile";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ShoppingBag } from "lucide-react";

export default function Home() {
  return (
    <main className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      {/* Sidebar for profile */}
      <div className="w-[280px] border-r border-border/50 hidden md:block bg-muted/10 overflow-y-auto shrink-0">
        <TasteProfile />
      </div>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 relative h-full">
        <div className="absolute top-4 right-4 z-50">
          <Sheet>
            <SheetTrigger>
              <button className="p-3 bg-card border border-border rounded-full shadow-sm hover:shadow text-primary transition-all">
                <ShoppingBag className="w-5 h-5" />
              </button>
            </SheetTrigger>
            <SheetContent className="w-[400px] sm:w-[400px] p-0 border-l border-border/50">
              <SmartCart />
            </SheetContent>
          </Sheet>
        </div>
        <ChatContainer />
      </div>
    </main>
  );
}
