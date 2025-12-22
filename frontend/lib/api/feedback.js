import { API_BASE_URL } from './config';
import { getStoredToken } from '../auth-context';

/**
 * Feedback API Service
 * Handles user ratings and reviews for the app.
 */

/**
 * Helper function to make API requests
 */
async function feedbackRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Add auth header if token exists
    const token = getStoredToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return null;
    }

    return response.json();
}

/**
 * Submit new feedback (requires authentication)
 * @param {Object} feedbackData - Object containing rating, category, and review
 * @param {number} feedbackData.rating - Rating from 1-5
 * @param {string} feedbackData.category - Category: general, feature, bug, improvement
 * @param {string} feedbackData.review - Optional review text
 */
export async function submitFeedback(feedbackData) {
    return feedbackRequest('/feedback/', {
        method: 'POST',
        body: JSON.stringify({
            rating: feedbackData.rating,
            category: feedbackData.category || 'general',
            review: feedbackData.review || null,
        }),
    });
}

/**
 * Get all feedback from all users (public - no auth required)
 * @param {number} limit - Maximum number of feedback entries to return
 */
export async function getAllFeedback(limit = 50) {
    return feedbackRequest(`/feedback/all?limit=${limit}`);
}

/**
 * Get current user's feedback history (requires auth)
 * @param {number} limit - Maximum number of feedback entries to return
 */
export async function getUserFeedback(limit = 10) {
    return feedbackRequest(`/feedback/?limit=${limit}`);
}

/**
 * Get feedback statistics (public - no auth required)
 */
export async function getFeedbackStats() {
    return feedbackRequest('/feedback/stats');
}

/**
 * Delete a feedback entry (requires auth, only own feedback)
 * @param {number} feedbackId - ID of the feedback to delete
 */
export async function deleteFeedback(feedbackId) {
    return feedbackRequest(`/feedback/${feedbackId}`, {
        method: 'DELETE',
    });
}
