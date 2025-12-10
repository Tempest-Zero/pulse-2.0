import { createContext, useContext, useState } from 'react';
import { initialTasks, initialSchedule } from '../data/initialData';

// Create the context
const AppContext = createContext(null);

// Provider component
export function AppProvider({ children }) {
  // Mood state
  const [mood, setMood] = useState('calm');
  
  // Tasks state (backlog items)
  const [tasks, setTasks] = useState(initialTasks);
  
  // Schedule state (fixed events)
  const [schedule, setSchedule] = useState(initialSchedule);

  // Focus Mode state
  const [focusTask, setFocusTask] = useState(null); // The task currently in focus
  const [focusStartTime, setFocusStartTime] = useState(null); // When focus started
  const [focusDuration, setFocusDuration] = useState(0); // Duration in minutes

  // Reflection state
  const [showReflection, setShowReflection] = useState(false);
  const [reflections, setReflections] = useState([]); // History of reflections

  // Task functions
  const addTask = (title, duration = 1, difficulty = 'medium') => {
    const newTask = {
      id: Date.now(),
      title,
      duration,
      difficulty,
      completed: false,
      scheduledAt: null,
    };
    setTasks(prev => [...prev, newTask]);
    return newTask;
  };

  const deleteTask = (id) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  const toggleTask = (id) => {
    setTasks(prev => prev.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  const updateTask = (id, updates) => {
    setTasks(prev => prev.map(task =>
      task.id === id ? { ...task, ...updates } : task
    ));
  };

  const scheduleTask = (taskId, startTime) => {
    setTasks(prev => prev.map(task =>
      task.id === taskId ? { ...task, scheduledAt: startTime } : task
    ));
  };

  const unscheduleTask = (taskId) => {
    setTasks(prev => prev.map(task =>
      task.id === taskId ? { ...task, scheduledAt: null } : task
    ));
  };

  // Schedule functions (for fixed events)
  const addBlock = (title, start, duration, type = 'fixed') => {
    const newBlock = {
      id: Date.now(),
      title,
      start,
      duration,
      type,
    };
    setSchedule(prev => [...prev, newBlock]);
    return newBlock;
  };

  const removeBlock = (id) => {
    setSchedule(prev => prev.filter(block => block.id !== id));
  };

  const updateBlock = (id, updates) => {
    setSchedule(prev => prev.map(block =>
      block.id === id ? { ...block, ...updates } : block
    ));
  };

  // Focus Mode functions
  const startFocus = (task) => {
    setFocusTask(task);
    setFocusStartTime(Date.now());
    setFocusDuration(task.duration * 60); // Convert hours to minutes
  };

  const endFocus = (completed = false) => {
    if (completed && focusTask) {
      toggleTask(focusTask.id); // Mark as completed
    }
    setFocusTask(null);
    setFocusStartTime(null);
    setFocusDuration(0);
  };

  const extendFocus = (minutes = 15) => {
    setFocusDuration(prev => prev + minutes);
  };

  // Reflection functions
  const openReflection = () => {
    setShowReflection(true);
  };

  const closeReflection = () => {
    setShowReflection(false);
  };

  const saveReflection = (reflection) => {
    const newReflection = {
      id: Date.now(),
      date: new Date().toISOString(),
      ...reflection,
    };
    setReflections(prev => [...prev, newReflection]);
    setShowReflection(false);
  };

  // Context value
  const value = {
    // Mood
    mood,
    setMood,
    
    // Tasks
    tasks,
    addTask,
    deleteTask,
    toggleTask,
    updateTask,
    scheduleTask,
    unscheduleTask,
    
    // Schedule
    schedule,
    addBlock,
    removeBlock,
    updateBlock,

    // Focus Mode
    focusTask,
    focusStartTime,
    focusDuration,
    startFocus,
    endFocus,
    extendFocus,

    // Reflection
    showReflection,
    reflections,
    openReflection,
    closeReflection,
    saveReflection,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use the context
export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export default AppContext;
