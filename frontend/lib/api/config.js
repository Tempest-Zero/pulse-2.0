/**
 * API Configuration with Authentication Support
 */

import { getStoredToken } from '../auth-context';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Format API error detail into a readable string
 * Handles FastAPI validation errors which come as arrays of objects
 */
function formatErrorDetail(detail) {
  if (!detail) return null;

  // If it's a string, return as-is
  if (typeof detail === 'string') {
    return detail;
  }

  // If it's an array (FastAPI validation errors)
  if (Array.isArray(detail)) {
    return detail
      .map(err => {
        if (typeof err === 'string') return err;
        // FastAPI validation error format: { loc: [...], msg: "...", type: "..." }
        if (err.msg) {
          const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
          return `${field}: ${err.msg}`;
        }
        return JSON.stringify(err);
      })
      .join('; ');
  }

  // If it's an object with a message property
  if (typeof detail === 'object') {
    if (detail.message) return detail.message;
    if (detail.msg) return detail.msg;
    return JSON.stringify(detail);
  }

  return String(detail);
}

/**
 * Get authorization headers if user is logged in
 */
function getAuthHeaders() {
  const token = getStoredToken();
  if (token) {
    return { 'Authorization': `Bearer ${token}` };
  }
  return {};
}

/**
 * Helper function to make API requests with automatic auth headers
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers,
    },
    ...options,
  };

  // Stringify body if it's an object
  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      // Clear stored auth and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('pulse_auth_token');
        localStorage.removeItem('pulse_user');
        // Only redirect if not already on auth page
        if (!window.location.pathname.includes('/auth')) {
          window.location.href = '/auth';
        }
      }
      throw new Error('Session expired. Please log in again.');
    }

    // Handle 204 No Content (for DELETE requests)
    if (response.status === 204) {
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMessage = formatErrorDetail(data.detail) || `API Error: ${response.status}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`API Request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * API request without auth (for public endpoints)
 */
export async function publicApiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);

    if (response.status === 204) {
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMessage = formatErrorDetail(data.detail) || `API Error: ${response.status}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`Public API Request failed: ${endpoint}`, error);
    throw error;
  }
}
