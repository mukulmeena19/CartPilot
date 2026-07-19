import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output is great for Docker but Vercel also supports it.
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
