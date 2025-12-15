# Frontend Code Patterns

## Page Component Pattern

```jsx
// app/example/page.jsx
'use client';

import { useState, useEffect } from 'react';
import { apiRequest } from '@/lib/api/config';

export default function ExamplePage() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const result = await apiRequest('/examples');
                setData(result);
            } catch (error) {
                console.error('Failed to fetch:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Examples</h1>
            {/* Content */}
        </div>
    );
}
```

## Protected Page Pattern

```jsx
'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProtectedPage() {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push('/auth');
        }
    }, [isAuthenticated, loading, router]);

    if (loading) return <div>Loading...</div>;
    if (!isAuthenticated) return null;

    return <div>Protected content</div>;
}
```

## Form Component Pattern

```jsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function ExampleForm({ onSubmit }) {
    const [value, setValue] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        try {
            await onSubmit(value);
            setValue('');
        } finally {
            setLoading(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Enter value..."
                disabled={loading}
            />
            <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : 'Submit'}
            </Button>
        </form>
    );
}
```

## API Request Pattern

```javascript
import { apiRequest } from '@/lib/api/config';

// GET request
const items = await apiRequest('/tasks');

// POST request
const newItem = await apiRequest('/tasks', {
    method: 'POST',
    body: { title: 'New Task', priority: 3 }
});

// PUT request
await apiRequest(`/tasks/${id}`, {
    method: 'PUT',
    body: { completed: true }
});

// DELETE request
await apiRequest(`/tasks/${id}`, { method: 'DELETE' });
```

## Dynamic Import Pattern (SSR-safe)

```jsx
'use client';

import dynamic from 'next/dynamic';

// Load component only on client
const ClientOnlyComponent = dynamic(
    () => import('@/components/client-only'),
    { ssr: false }
);

// With loading state
const HeavyComponent = dynamic(
    () => import('@/components/heavy'),
    {
        ssr: false,
        loading: () => <div className="animate-pulse">Loading...</div>
    }
);
```

## shadcn/ui Component Usage

```jsx
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

<Card>
    <CardHeader>
        <CardTitle>Example Card</CardTitle>
    </CardHeader>
    <CardContent>
        <div className="space-y-4">
            <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Enter name" />
            </div>
            <Button>Submit</Button>
        </div>
    </CardContent>
</Card>
```
