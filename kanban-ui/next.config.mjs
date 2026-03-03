/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    async rewrites() {
        const apiUrl = process.env.INTERNAL_API_URL ||
            'http://kanban-api-service.ai-agents.svc.cluster.local:5001/api';

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/:path*`,
            },
        ];
    },
};

export default nextConfig;
