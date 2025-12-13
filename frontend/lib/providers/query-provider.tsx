'use client';

/**
 * React Query Provider
 * Wraps the app with QueryClientProvider for data fetching
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

interface QueryProviderProps {
    children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
    // Create query client with default options
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        // Stale time: 1 minute (data is fresh for 1 minute)
                        staleTime: 60 * 1000,
                        // Retry failed requests 3 times
                        retry: 3,
                        // Retry delay: exponential backoff
                        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
                        // Refetch on window focus
                        refetchOnWindowFocus: true,
                    },
                    mutations: {
                        // Retry mutations once
                        retry: 1,
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}

export default QueryProvider;
