'use client';

/**
 * Tasks Hooks
 * React Query hooks for task management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi, Task, TaskCreate, TaskUpdate } from '@/lib/api';

/** Query key for tasks */
export const TASKS_KEY = ['tasks'] as const;

/**
 * Fetch all tasks
 */
export function useTasks(options?: { completed?: boolean }) {
    return useQuery({
        queryKey: [...TASKS_KEY, options],
        queryFn: () => tasksApi.getAll(options),
    });
}

/**
 * Fetch single task by ID
 */
export function useTask(id: number) {
    return useQuery({
        queryKey: [...TASKS_KEY, id],
        queryFn: () => tasksApi.getById(id),
        enabled: !!id,
    });
}

/**
 * Create new task
 */
export function useCreateTask() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: TaskCreate) => tasksApi.create(data),
        onSuccess: () => {
            // Invalidate tasks list to refetch
            queryClient.invalidateQueries({ queryKey: TASKS_KEY });
        },
    });
}

/**
 * Update existing task
 */
export function useUpdateTask() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: TaskUpdate }) =>
            tasksApi.update(id, data),
        onSuccess: (updatedTask) => {
            // Update the specific task in cache
            queryClient.setQueryData([...TASKS_KEY, updatedTask.id], updatedTask);
            // Invalidate list to refetch
            queryClient.invalidateQueries({ queryKey: TASKS_KEY });
        },
    });
}

/**
 * Delete task
 */
export function useDeleteTask() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => tasksApi.delete(id),
        onSuccess: (_, deletedId) => {
            // Remove from cache
            queryClient.removeQueries({ queryKey: [...TASKS_KEY, deletedId] });
            // Invalidate list
            queryClient.invalidateQueries({ queryKey: TASKS_KEY });
        },
    });
}

/**
 * Toggle task completion
 */
export function useToggleTask() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => tasksApi.toggle(id),
        onSuccess: (updatedTask) => {
            // Update cache
            queryClient.setQueryData([...TASKS_KEY, updatedTask.id], updatedTask);
            queryClient.invalidateQueries({ queryKey: TASKS_KEY });
        },
    });
}
