/**
 * API Configuration
 * Environment-based configuration for API client
 */

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
}

/**
 * Validates that a URL is properly formatted
 */
function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// Get configuration from environment variables with fallbacks
const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const timeout = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000', 10);

// Validate configuration
if (!validateUrl(baseUrl)) {
  throw new Error(`Invalid API URL: ${baseUrl}`);
}

/**
 * API Configuration object
 * - baseUrl: Railway production URL or localhost for dev
 * - timeout: Request timeout in milliseconds
 */
export const API_CONFIG: ApiConfig = {
  baseUrl,
  timeout,
} as const;

export default API_CONFIG;
