/**
 * API Client
 * Base HTTP client with error handling and timeout support
 */

import { API_CONFIG } from './config';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
    status: number;
    statusText: string;
    data?: unknown;

    constructor(status: number, statusText: string, data?: unknown) {
        super(`API Error: ${status} ${statusText}`);
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
        this.data = data;
    }
}

/**
 * Generic API client function
 * @param endpoint - API endpoint (e.g., '/tasks')
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Promise with typed response
 */
export async function apiClient<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;

    // Set up abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    // Default headers
    const defaultHeaders: HeadersInit = {
        'Content-Type': 'application/json',
    };

    // Merge headers
    const headers = {
        ...defaultHeaders,
        ...options.headers,
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle non-ok responses
        if (!response.ok) {
            let errorData: unknown;
            try {
                errorData = await response.json();
            } catch {
                errorData = null;
            }
            throw new ApiError(response.status, response.statusText, errorData);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return undefined as T;
        }

        // Parse and return JSON
        const data: T = await response.json();
        return data;
    } catch (error) {
        clearTimeout(timeoutId);

        // Handle abort (timeout)
        if (error instanceof Error && error.name === 'AbortError') {
            throw new ApiError(408, 'Request Timeout', { message: 'Request timed out' });
        }

        // Re-throw ApiError
        if (error instanceof ApiError) {
            throw error;
        }

        // Handle network errors
        if (error instanceof Error) {
            throw new ApiError(0, 'Network Error', { message: error.message });
        }

        throw error;
    }
}

export default apiClient;
