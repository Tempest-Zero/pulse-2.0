'use client';

/**
 * Schedule Hooks
 * React Query hooks for schedule management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scheduleApi, ScheduleBlock, ScheduleBlockCreate, ScheduleBlockUpdate, BlockType } from '@/lib/api';

/** Query key for schedule */
export const SCHEDULE_KEY = ['schedule'] as const;

/**
 * Fetch all schedule blocks
 */
export function useSchedule(options?: { type?: BlockType }) {
    return useQuery({
        queryKey: [...SCHEDULE_KEY, options],
        queryFn: () => scheduleApi.getAll(options),
    });
}

/**
 * Fetch single schedule block by ID
 */
export function useScheduleBlock(id: number) {
    return useQuery({
        queryKey: [...SCHEDULE_KEY, id],
        queryFn: () => scheduleApi.getById(id),
        enabled: !!id,
    });
}

/**
 * Fetch blocks in time range
 */
export function useScheduleRange(startHour: number, endHour: number) {
    return useQuery({
        queryKey: [...SCHEDULE_KEY, 'range', startHour, endHour],
        queryFn: () => scheduleApi.getInRange(startHour, endHour),
        enabled: startHour !== undefined && endHour !== undefined,
    });
}

/**
 * Create new schedule block
 */
export function useCreateScheduleBlock() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ScheduleBlockCreate) => scheduleApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: SCHEDULE_KEY });
        },
    });
}

/**
 * Update existing schedule block
 */
export function useUpdateScheduleBlock() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ScheduleBlockUpdate }) =>
            scheduleApi.update(id, data),
        onSuccess: (updatedBlock) => {
            queryClient.setQueryData([...SCHEDULE_KEY, updatedBlock.id], updatedBlock);
            queryClient.invalidateQueries({ queryKey: SCHEDULE_KEY });
        },
    });
}

/**
 * Delete schedule block
 */
export function useDeleteScheduleBlock() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => scheduleApi.delete(id),
        onSuccess: (_, deletedId) => {
            queryClient.removeQueries({ queryKey: [...SCHEDULE_KEY, deletedId] });
            queryClient.invalidateQueries({ queryKey: SCHEDULE_KEY });
        },
    });
}

/**
 * Clear all schedule blocks
 */
export function useClearSchedule() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => scheduleApi.clearAll(),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: SCHEDULE_KEY });
        },
    });
}
