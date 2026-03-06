/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.KANBAN_API_URL || "http://kanban-api-service.ai-agents.svc.cluster.local:5001"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
