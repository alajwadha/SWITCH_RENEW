import type { NextConfig } from "next";
const config: NextConfig = { output: "export", images: { unoptimized: true }, env: { NEXT_PUBLIC_ATLAS_ONLY: process.env.VERCEL === '1' ? 'true' : 'false' } };
export default config;
