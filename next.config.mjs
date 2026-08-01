/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/api/:path*`,
      },
      {
        source: '/output/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/output/:path*`,
      },
      {
        source: '/uploads/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/uploads/:path*`,
      },
      {
        source: '/datasets/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/datasets/:path*`,
      },
      {
        source: '/previews/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/previews/:path*`,
      },
      {
        source: '/thumbnails/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/thumbnails/:path*`,
      },
      {
        source: '/confidence/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/confidence/:path*`,
      },
      {
        source: '/masks/:path*',
        destination: `${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/masks/:path*`,
      },
    ]
  },
}

export default nextConfig
