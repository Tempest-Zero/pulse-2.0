# Pulse Frontend Guidelines

> Next.js 16 + React 19 + shadcn/ui patterns for the Pulse 2.0 frontend.

## Purpose

Provides guidance for working with the Next.js frontend: pages, components, API integration, and authentication.

## When to Use

- [ ] Adding/modifying pages in `app/`
- [ ] Creating/updating components in `components/`
- [ ] Working with API calls via `lib/api/config.js`
- [ ] Managing auth state via `lib/auth-context.js`
- [ ] Debugging build failures or SSR issues
- [ ] Styling with Tailwind CSS

## Quick Rules

### Project Structure
```
frontend/
├── app/                  # Next.js App Router pages
│   ├── layout.jsx        # Root layout (with AuthProvider)
│   ├── page.jsx          # Landing page (/)
│   ├── auth/page.jsx     # Login/Signup
│   ├── dashboard/page.jsx
│   ├── schedule/page.jsx
│   ├── checkin/page.jsx
│   ├── insights/page.jsx
│   └── settings/page.jsx
├── components/           # React components
│   ├── auth-form.jsx     # Client-only auth form
│   ├── ui/               # shadcn/ui components
│   └── ...
├── lib/
│   ├── api/config.js     # API_BASE_URL, apiRequest helper
│   └── auth-context.js   # AuthProvider, useAuth hook
└── styles/globals.css
```

### Commands (from package.json)
```bash
npm run dev      # Development server (localhost:3000)
npm run build    # Production build
npm run start    # Start production server
npm run lint     # ESLint
```

### Environment Variables
| Variable | Purpose | Location |
|----------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `.env.production` |

**Current value**: `https://back-end-304.up.railway.app`

### API Client
```javascript
// lib/api/config.js
import { apiRequest } from '@/lib/api/config';

// Authenticated request
const data = await apiRequest('/tasks', { method: 'GET' });

// With body
await apiRequest('/tasks', {
    method: 'POST',
    body: { title: 'New task' }
});
```

### Auth Context
```javascript
import { useAuth } from '@/lib/auth-context';

const { user, login, signup, logout, isAuthenticated } = useAuth();
```

## Common Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| "useAuth must be used within AuthProvider" | SSR trying to render client-only hook | Use `next/dynamic` with `ssr: false` |
| CORS error | Backend CORS_ORIGINS missing frontend URL | Add URL to backend env vars |
| Wrong API URL | Env var not set at build time | Update `.env.production`, rebuild |
| Build fails with 404 | Router not found during static generation | Add `export const dynamic = 'force-dynamic'` |

## Client-Only Component Pattern

For pages using `useAuth`:
```jsx
'use client';

import dynamic from 'next/dynamic';

const AuthForm = dynamic(() => import('@/components/auth-form'), {
    ssr: false,
    loading: () => <div>Loading...</div>,
});

export default function AuthPage() {
    return <AuthForm />;
}
```

## Resources

- [patterns.md](resources/patterns.md) - Component and page patterns
- [routing.md](resources/routing.md) - App Router route structure
