/**
 * Hooks Index
 * Re-exports all custom hooks for convenient importing
 */

// Existing hooks
export { useIsMobile } from './use-mobile';
export { useToast, toast } from './use-toast';

// API hooks - Tasks
export {
    useTasks,
    useTask,
    useCreateTask,
    useUpdateTask,
    useDeleteTask,
    useToggleTask,
    TASKS_KEY,
} from './use-tasks';

// API hooks - Schedule
export {
    useSchedule,
    useScheduleBlock,
    useScheduleRange,
    useCreateScheduleBlock,
    useUpdateScheduleBlock,
    useDeleteScheduleBlock,
    useClearSchedule,
    SCHEDULE_KEY,
} from './use-schedule';

// API hooks - Mood
export {
    useCurrentMood,
    useMoodHistory,
    useMoodCounts,
    useMostCommonMood,
    useSetMood,
    useDeleteMoodEntry,
    useClearMoodHistory,
    MOOD_KEY,
} from './use-mood';

// API hooks - Reflections
export {
    useReflections,
    useReflection,
    useTodayReflection,
    useReflectionByDate,
    useMoodAverage,
    useCommonDistractions,
    useCreateReflection,
    useUpdateReflection,
    useDeleteReflection,
    REFLECTIONS_KEY,
} from './use-reflections';
