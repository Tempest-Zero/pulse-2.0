'use client';

/**
 * Mood Hooks
 * React Query hooks for mood tracking
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { moodApi, MoodValue, MoodEntry, CurrentMood } from '@/lib/api';

/** Query key for mood */
export const MOOD_KEY = ['mood'] as const;

/**
 * Get current mood
 */
export function useCurrentMood() {
    return useQuery({
        queryKey: [...MOOD_KEY, 'current'],
        queryFn: () => moodApi.getCurrent(),
    });
}

/**
 * Get mood history
 */
export function useMoodHistory(limit?: number) {
    return useQuery({
        queryKey: [...MOOD_KEY, 'history', limit],
        queryFn: () => moodApi.getHistory(limit),
    });
}

/**
 * Get mood counts (analytics)
 */
export function useMoodCounts(limit?: number) {
    return useQuery({
        queryKey: [...MOOD_KEY, 'counts', limit],
        queryFn: () => moodApi.getCounts(limit),
    });
}

/**
 * Get most common mood
 */
export function useMostCommonMood(limit?: number) {
    return useQuery({
        queryKey: [...MOOD_KEY, 'most-common', limit],
        queryFn: () => moodApi.getMostCommon(limit),
    });
}

/**
 * Set current mood
 */
export function useSetMood() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (mood: MoodValue) => moodApi.set(mood),
        onSuccess: (newEntry) => {
            // Update current mood in cache
            queryClient.setQueryData<CurrentMood>([...MOOD_KEY, 'current'], {
                mood: newEntry.mood,
                timestamp: newEntry.timestamp,
            });
            // Invalidate history and analytics
            queryClient.invalidateQueries({ queryKey: [...MOOD_KEY, 'history'] });
            queryClient.invalidateQueries({ queryKey: [...MOOD_KEY, 'counts'] });
            queryClient.invalidateQueries({ queryKey: [...MOOD_KEY, 'most-common'] });
        },
    });
}

/**
 * Delete mood entry
 */
export function useDeleteMoodEntry() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => moodApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: MOOD_KEY });
        },
    });
}

/**
 * Clear mood history
 */
export function useClearMoodHistory() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => moodApi.clearHistory(),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: MOOD_KEY });
        },
    });
}
