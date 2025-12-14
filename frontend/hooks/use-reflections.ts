'use client';

/**
 * Reflections Hooks
 * React Query hooks for daily reflections
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reflectionsApi, Reflection, ReflectionCreate, ReflectionUpdate } from '@/lib/api';

/** Query key for reflections */
export const REFLECTIONS_KEY = ['reflections'] as const;

/**
 * Fetch all reflections
 */
export function useReflections(limit?: number) {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, { limit }],
        queryFn: () => reflectionsApi.getAll(limit),
    });
}

/**
 * Fetch single reflection by ID
 */
export function useReflection(id: number) {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, id],
        queryFn: () => reflectionsApi.getById(id),
        enabled: !!id,
    });
}

/**
 * Fetch today's reflection
 */
export function useTodayReflection() {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, 'today'],
        queryFn: () => reflectionsApi.getToday(),
    });
}

/**
 * Fetch reflection by date
 */
export function useReflectionByDate(date: string) {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, 'date', date],
        queryFn: () => reflectionsApi.getByDate(date),
        enabled: !!date,
    });
}

/**
 * Get mood average analytics
 */
export function useMoodAverage(days?: number) {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, 'analytics', 'mood-average', days],
        queryFn: () => reflectionsApi.getMoodAverage(days),
    });
}

/**
 * Get common distractions analytics
 */
export function useCommonDistractions(days?: number) {
    return useQuery({
        queryKey: [...REFLECTIONS_KEY, 'analytics', 'common-distractions', days],
        queryFn: () => reflectionsApi.getCommonDistractions(days),
    });
}

/**
 * Create new reflection
 */
export function useCreateReflection() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ReflectionCreate) => reflectionsApi.create(data),
        onSuccess: (newReflection) => {
            // Set today's reflection
            queryClient.setQueryData([...REFLECTIONS_KEY, 'today'], newReflection);
            // Invalidate lists and analytics
            queryClient.invalidateQueries({ queryKey: REFLECTIONS_KEY });
        },
    });
}

/**
 * Update existing reflection
 */
export function useUpdateReflection() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ReflectionUpdate }) =>
            reflectionsApi.update(id, data),
        onSuccess: (updatedReflection) => {
            queryClient.setQueryData([...REFLECTIONS_KEY, updatedReflection.id], updatedReflection);
            queryClient.invalidateQueries({ queryKey: REFLECTIONS_KEY });
        },
    });
}

/**
 * Delete reflection
 */
export function useDeleteReflection() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => reflectionsApi.delete(id),
        onSuccess: (_, deletedId) => {
            queryClient.removeQueries({ queryKey: [...REFLECTIONS_KEY, deletedId] });
            queryClient.invalidateQueries({ queryKey: REFLECTIONS_KEY });
        },
    });
}
