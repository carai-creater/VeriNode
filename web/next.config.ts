import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [{ source: "/tokushoho", destination: "/law", permanent: true }];
  },
};

export default nextConfig;
