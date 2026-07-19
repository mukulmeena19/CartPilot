"use client";

import { useAuth } from "@/components/providers/auth-provider";
import { ChatInterface } from "@/components/chat/chat-interface";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
        Welcome back, {user?.full_name || "Shopper"}!
      </h1>
      
      {/* The main AI Agent Chat Interface */}
      <div className="mt-8">
        <ChatInterface />
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-2 mt-12">
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">Recent Carts</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            View and manage your recently generated carts. (Coming soon)
          </p>
        </div>
        
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">Shopping Memory</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Manage your brand preferences and dietary restrictions. (Coming soon)
          </p>
        </div>
      </div>
    </div>
  );
}
