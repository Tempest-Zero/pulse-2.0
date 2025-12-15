# CLAUDE.md - Frontend (Next.js)

> **Purpose**: Frontend-specific commands, structure, and gotchas.

## Folder Structure

```
frontend/
├── app/                  # Next.js App Router pages
│   ├── layout.jsx        # Root layout
│   ├── page.jsx          # Landing page (/)
│   ├── auth/page.jsx     # Login/Signup (/auth)
│   ├── dashboard/page.jsx
│   ├── schedule/page.jsx
│   ├── checkin/page.jsx
│   ├── insights/page.jsx
│   └── settings/page.jsx
├── components/           # React components
│   ├── auth-form.jsx     # Auth form (client-only)
│   ├── ai-recommendation.jsx
│   ├── navigation.jsx
│   └── ui/               # shadcn/ui components
├── lib/
│   ├── api/config.js     # API_BASE_URL, apiRequest helper
│   ├── auth-context.js   # AuthProvider, useAuth hook
│   └── utils.js
├── hooks/                # Custom React hooks
├── styles/
│   └── globals.css
└── .env.production       # Production env vars (baked at build)
```

## Commands

From `package.json`:

```bash
# Install dependencies
npm install
# or: pnpm install

# Development server
npm run dev
# → http://localhost:3000

# Production build
npm run build

# Start production server
npm run start

# Lint
npm run lint
```

**Note**: Node 20.x required (`engines` in package.json).

## Environment Variables

| Variable | Purpose | Where |
|----------|---------|-------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `.env.production` |

**Current value** (from `.env.production`):
```
NEXT_PUBLIC_API_URL=https://back-end-304.up.railway.app
```

**Important**: This is baked at build time. Changing it requires a rebuild.

## API Configuration

Location: `lib/api/config.js`

```javascript
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

- `apiRequest(endpoint, options)` - authenticated requests
- `publicApiRequest(endpoint, options)` - public endpoints
- Handles 401 by clearing auth and redirecting to `/auth`

## Auth Context

Location: `lib/auth-context.js`

```javascript
// In components:
import { useAuth } from '@/lib/auth-context';

const { user, login, signup, logout, isAuthenticated } = useAuth();
```

Token stored in `localStorage` as `pulse_auth_token`.

## Route Structure

| Route | File | Description |
|-------|------|-------------|
| `/` | `app/page.jsx` | Landing page |
| `/auth` | `app/auth/page.jsx` | Login/Signup (client-only) |
| `/dashboard` | `app/dashboard/page.jsx` | Main dashboard with AI recs |
| `/schedule` | `app/schedule/page.jsx` | Schedule management |
| `/checkin` | `app/checkin/page.jsx` | Daily reflections |
| `/insights` | `app/insights/page.jsx` | Analytics |
| `/settings` | `app/settings/page.jsx` | User settings |

## Common Gotchas

### SSR with Auth Hooks
- `useAuth` hook requires `AuthProvider` context
- Pages using `useAuth` must be client components
- For auth page: use `next/dynamic` with `ssr: false`

```javascript
// app/auth/page.jsx
'use client';
import dynamic from 'next/dynamic';

const AuthForm = dynamic(() => import('@/components/auth-form'), {
    ssr: false,
});
```

### CORS Errors
- Usually means backend `CORS_ORIGINS` doesn't include frontend URL
- Check Network tab → look at the actual request URL
- Ensure no trailing slash in `CORS_ORIGINS`

### Wrong API URL
- Check browser console for actual `API_BASE_URL`
- If localhost, the env var wasn't set at build time
- Fix: update `.env.production`, push, force rebuild on Railway

### Build Failures
- "useAuth must be used within AuthProvider" → SSR issue, see above
- TypeScript errors → check `tsconfig.json`, may need to fix types
