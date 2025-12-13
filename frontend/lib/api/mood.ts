/**
 * Mood API Module
 * Operations for mood tracking
 */

import { apiClient } from './client';

// ============ Types ============

/** Valid mood values (expanded for frontend compatibility) */
export type MoodValue =
    | 'calm'
    | 'energized'
    | 'focused'
    | 'tired'
    | 'good'
    | 'neutral'
    | 'low'
    | 'exhausted';

/** Mood entry from backend */
export interface MoodEntry {
    id: number;
    mood: MoodValue;
    timestamp: string;
}

/** Create mood payload */
export interface MoodCreate {
    mood: MoodValue;
}

/** Mood counts response */
export interface MoodCounts {
    total_entries: number;
    counts: Record<MoodValue, number>;
}

/** Most common mood response */
export interface MostCommonMood {
    most_common: MoodValue | null;
    count: number;
    total_entries: number;
}

/** Current mood response */
export interface CurrentMood {
    mood: MoodValue;
    timestamp: string | null;
}

// ============ API Methods ============

export const moodApi = {
    /**
     * Get current mood
     */
    async getCurrent(): Promise<CurrentMood> {
        return apiClient<CurrentMood>('/mood/current');
    },

    /**
     * Set current mood
     */
    async set(mood: MoodValue): Promise<MoodEntry> {
        return apiClient<MoodEntry>('/mood', {
            method: 'POST',
            body: JSON.stringify({ mood }),
        });
    },

    /**
     * Get mood history
     */
    async getHistory(limit?: number): Promise<MoodEntry[]> {
        let endpoint = '/mood/history';
        if (limit !== undefined) {
            endpoint += `?limit=${limit}`;
        }
        return apiClient<MoodEntry[]>(endpoint);
    },

    /**
     * Get mood counts
     */
    async getCounts(limit?: number): Promise<MoodCounts> {
        let endpoint = '/mood/analytics/counts';
        if (limit !== undefined) {
            endpoint += `?limit=${limit}`;
        }
        return apiClient<MoodCounts>(endpoint);
    },

    /**
     * Get most common mood
     */
    async getMostCommon(limit?: number): Promise<MostCommonMood> {
        let endpoint = '/mood/analytics/most-common';
        if (limit !== undefined) {
            endpoint += `?limit=${limit}`;
        }
        return apiClient<MostCommonMood>(endpoint);
    },

    /**
     * Delete mood entry
     */
    async delete(id: number): Promise<void> {
        await apiClient<void>(`/mood/${id}`, {
            method: 'DELETE',
        });
    },

    /**
     * Clear all mood history
     */
    async clearHistory(): Promise<void> {
        await apiClient<void>('/mood/history/clear', {
            method: 'DELETE',
        });
    },
};

export default moodApi;
