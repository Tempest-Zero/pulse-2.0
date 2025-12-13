/**
 * Reflections API Module
 * Operations for daily reflections
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

/** Reflection from backend */
export interface Reflection {
    id: number;
    date: string;
    moodScore: number;
    distractions: string[];
    note: string;
    completedTasks: number;
    totalTasks: number;
    createdAt: string;
}

/** Create reflection payload */
export interface ReflectionCreate {
    moodScore: number;
    distractions?: string[];
    note?: string;
    completedTasks: number;
    totalTasks: number;
}

/** Update reflection payload */
export interface ReflectionUpdate {
    moodScore?: number;
    distractions?: string[];
    note?: string;
}

/** Mood average response */
export interface MoodAverage {
    days: number;
    average_mood: number | null;
}

/** Common distractions response */
export interface CommonDistraction {
    tag: string;
    count: number;
}

export interface CommonDistractionsResponse {
    days: number;
    distractions: CommonDistraction[];
}

// ============ API Methods ============

export const reflectionsApi = {
    /**
     * Get all reflections
     */
    async getAll(limit?: number): Promise<Reflection[]> {
        let endpoint = '/reflections';
        if (limit !== undefined) {
            endpoint += `?limit=${limit}`;
        }
        return apiClient<Reflection[]>(endpoint);
    },

    /**
     * Get single reflection by ID
     */
    async getById(id: number): Promise<Reflection> {
        return apiClient<Reflection>(`/reflections/${id}`);
    },

    /**
     * Get today's reflection (returns null if not found)
     */
    async getToday(): Promise<Reflection | null> {
        try {
            return await apiClient<Reflection>('/reflections/today');
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                return null;
            }
            throw error;
        }
    },

    /**
     * Get reflection by date (returns null if not found)
     */
    async getByDate(date: string): Promise<Reflection | null> {
        try {
            return await apiClient<Reflection>(`/reflections/date/${date}`);
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                return null;
            }
            throw error;
        }
    },

    /**
     * Create new reflection
     */
    async create(data: ReflectionCreate): Promise<Reflection> {
        return apiClient<Reflection>('/reflections', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * Update existing reflection
     */
    async update(id: number, data: ReflectionUpdate): Promise<Reflection> {
        return apiClient<Reflection>(`/reflections/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    /**
     * Delete reflection
     */
    async delete(id: number): Promise<void> {
        await apiClient<void>(`/reflections/${id}`, {
            method: 'DELETE',
        });
    },

    /**
     * Get average mood score
     */
    async getMoodAverage(days?: number): Promise<MoodAverage> {
        let endpoint = '/reflections/analytics/mood-average';
        if (days !== undefined) {
            endpoint += `?days=${days}`;
        }
        return apiClient<MoodAverage>(endpoint);
    },

    /**
     * Get common distractions
     */
    async getCommonDistractions(days?: number): Promise<CommonDistractionsResponse> {
        let endpoint = '/reflections/analytics/common-distractions';
        if (days !== undefined) {
            endpoint += `?days=${days}`;
        }
        return apiClient<CommonDistractionsResponse>(endpoint);
    },
};

export default reflectionsApi;
