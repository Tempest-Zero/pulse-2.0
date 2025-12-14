'use client';

import dynamic from 'next/dynamic';

// Dynamically import AuthForm with SSR disabled
// This prevents the useAuth hook from running during server-side rendering
const AuthForm = dynamic(() => import('@/components/auth-form'), {
    ssr: false,
    loading: () => (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        }}>
            <div style={{
                color: 'rgba(255, 255, 255, 0.6)',
                fontSize: '1rem',
            }}>
                Loading...
            </div>
        </div>
    ),
});

/**
 * Authentication Page - Login and Signup
 */
export default function AuthPage() {
    return <AuthForm />;
}
