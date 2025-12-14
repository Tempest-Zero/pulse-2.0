"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from './api/config';

/**
 * Auth Context for managing user authentication state.
 */

const AuthContext = createContext(null);

const TOKEN_KEY = 'pulse_auth_token';
const USER_KEY = 'pulse_user';

/**
 * Auth Provider Component
 * Wraps the app to provide authentication state and methods.
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Initialize auth state from localStorage on mount
    useEffect(() => {
        const storedToken = localStorage.getItem(TOKEN_KEY);
        const storedUser = localStorage.getItem(USER_KEY);

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
            // Optionally validate token with /auth/me
            validateToken(storedToken);
        }

        setLoading(false);
    }, []);

    /**
     * Validate token by calling /auth/me
     */
    const validateToken = async (authToken) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                // Token is invalid, clear auth state
                logout();
            }
        } catch (err) {
            console.error('Token validation failed:', err);
            // Keep user logged in if network error (offline support)
        }
    };

    /**
     * Sign up a new user
     */
    const signup = async (email, password, username) => {
        setError(null);
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, username }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Signup failed');
            }

            // Store auth data
            localStorage.setItem(TOKEN_KEY, data.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user));
            setToken(data.access_token);
            setUser(data.user);

            return { success: true };
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    /**
     * Log in an existing user
     */
    const login = async (email, password) => {
        setError(null);
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Store auth data
            localStorage.setItem(TOKEN_KEY, data.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user));
            setToken(data.access_token);
            setUser(data.user);

            return { success: true };
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    /**
     * Log out the current user
     */
    const logout = () => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setToken(null);
        setUser(null);
    };

    /**
     * Get authorization headers for API requests
     */
    const getAuthHeaders = () => {
        if (!token) return {};
        return { 'Authorization': `Bearer ${token}` };
    };

    const value = {
        user,
        token,
        loading,
        error,
        isAuthenticated: !!token,
        signup,
        login,
        logout,
        getAuthHeaders,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

/**
 * Hook to access auth context
 */
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

/**
 * Get stored token (for use outside React components)
 */
export function getStoredToken() {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
}
