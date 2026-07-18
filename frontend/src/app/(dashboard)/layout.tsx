"use client";

import { useAuth } from "@/components/providers/auth-provider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex h-screen flex-col bg-gray-100 dark:bg-gray-900">
      {/* Navbar */}
      <nav className="border-b bg-white px-6 py-4 shadow-sm dark:border-gray-800 dark:bg-gray-950 flex justify-between items-center">
        <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">CartPilot</div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-700 dark:text-gray-300">
            {user.full_name || user.email}
          </span>
          <button
            onClick={logout}
            className="text-sm font-medium text-red-600 hover:text-red-500"
          >
            Logout
          </button>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r bg-white p-4 hidden md:block dark:border-gray-800 dark:bg-gray-950">
          <ul className="space-y-2">
            <li>
              <Link href="/dashboard" className="block rounded-md px-4 py-2 font-medium text-gray-900 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800">
                Dashboard
              </Link>
            </li>
            <li>
              <Link href="/dashboard/shopping" className="block rounded-md px-4 py-2 font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800">
                AI Shopping
              </Link>
            </li>
            <li>
              <Link href="/dashboard/history" className="block rounded-md px-4 py-2 font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800">
                History
              </Link>
            </li>
          </ul>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
