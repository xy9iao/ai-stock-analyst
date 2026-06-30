import type { NextConfig } from "next";

// Proxy /api/* to the backend so the frontend can use same-origin relative URLs.
// BACKEND_URL is the backend's reachable address from the Next server:
//   - local dev:       http://localhost:8000 (default)
//   - docker compose:  http://backend:8000  (set in docker-compose.yml)
const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
