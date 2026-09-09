import type { NextConfig } from "next";
const config: NextConfig = {
 output: "export",
 images: { unoptimized: true },
 env: { NEXT_PUBLIC_ATLAS_ONLY: process.env.VERCEL === '1' ? 'true' : 'false' },
 // Keep development hydration compatible with proxies that do not forward
 // React's optional debug WebSocket. Production rendering is unaffected.
 experimental: {reactDebugChannel: false},
};
export default config;
