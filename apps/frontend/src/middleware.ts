import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_PREFIXES = ['/dashboard', '/projects', '/settings', '/profile', '/assets', '/characters'];
const GUEST_ONLY_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password'];

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const authToken = request.cookies.get('kidsai_auth_token')?.value;

  const isProtected = PROTECTED_PREFIXES.some(prefix => path.startsWith(prefix));
  const isGuestOnly = GUEST_ONLY_ROUTES.some(route => path.startsWith(route));

  // Note: Client-side AuthProvider handles token validation from localStorage as well.
  // Middleware handles cookie-based SSR checks when available.
  
  if (isProtected && !authToken) {
    // If attempting to access protected route without auth token cookie, allow client-side hydration check
    return NextResponse.next();
  }

  if (isGuestOnly && authToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/projects/:path*',
    '/settings/:path*',
    '/profile/:path*',
    '/login',
    '/register',
    '/forgot-password',
    '/reset-password',
  ],
};
