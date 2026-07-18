"use client";

import { useAuth } from "@/components/providers/auth-provider";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
        Welcome back, {user?.full_name || "Shopper"}!
      </h1>
      
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Placeholder cards for future milestones */}
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">AI Shopping Goals</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Start a new shopping session by describing your goals.
          </p>
        </div>
        
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">Recent Carts</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            View and manage your recently generated carts.
          </p>
        </div>
        
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">Shopping Memory</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Manage your brand preferences and dietary restrictions.
          </p>
        </div>
      </div>
    </div>
  );
}
