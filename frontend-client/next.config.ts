import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
  },
  // Use relative paths for assets in production (Electron)
  assetPrefix: isProd ? '.' : undefined,
};

export default nextConfig;
