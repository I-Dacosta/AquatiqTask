const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable TypeScript support for config
  typescript: {
    ignoreBuildErrors: false,
  },

  outputFileTracingRoot: path.join(__dirname, '..'),
  
  // Enable experimental features
  experimental: {
    // Additional experimental features can be enabled here.
  },
  
  // Enable typed routes for type safety
  typedRoutes: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  // Enhanced security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
