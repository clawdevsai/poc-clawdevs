/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    async rewrites() {
        // Use K8s internal service as default if no env is set
        const apiUrl = process.env.INTERNAL_API_URL ||
            process.env.NEXT_PUBLIC_API_URL ||
            'http://kanban-api-service.ai-agents.svc.cluster.local:5001';

        return [
            {
                source: '/kanban-api/:path*',
                destination: `${apiUrl}/:path*`,
            },
        ];
    },
};

export default nextConfig;
