// Initial tasks for the backlog
export const initialTasks = [
  { 
    id: 1, 
    title: 'Finish quarterly report', 
    duration: 2, 
    difficulty: 'hard', 
    completed: false,
    scheduledAt: 9 // Scheduled at 9 AM
  },
  { 
    id: 2, 
    title: 'Review pull requests', 
    duration: 1, 
    difficulty: 'medium', 
    completed: false,
    scheduledAt: 14 // Scheduled at 2 PM
  },
  { 
    id: 3, 
    title: 'Update project documentation', 
    duration: 1.5, 
    difficulty: 'easy', 
    completed: false,
    scheduledAt: null // Not scheduled yet
  },
  { 
    id: 4, 
    title: 'Prepare presentation slides', 
    duration: 2, 
    difficulty: 'medium', 
    completed: false,
    scheduledAt: null // Not scheduled yet
  },
  { 
    id: 5, 
    title: 'Reply to client emails', 
    duration: 0.5, 
    difficulty: 'easy', 
    completed: true,
    scheduledAt: null
  },
];

// Fixed events that don't move (meetings, breaks, etc.)
export const initialSchedule = [
  { 
    id: 101, 
    title: 'Morning Routine', 
    start: 7, 
    duration: 1, 
    type: 'fixed' 
  },
  { 
    id: 102, 
    title: 'Team Standup', 
    start: 11, 
    duration: 0.5, 
    type: 'fixed' 
  },
  { 
    id: 103, 
    title: 'Lunch Break', 
    start: 12, 
    duration: 1, 
    type: 'break' 
  },
  { 
    id: 104, 
    title: 'Weekly Sync', 
    start: 16, 
    duration: 1, 
    type: 'fixed' 
  },
];

