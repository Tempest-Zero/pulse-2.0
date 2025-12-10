import { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import styles from './Timeline.module.css';

const HOUR_HEIGHT = 60; // pixels per hour
const START_HOUR = 6;
const END_HOUR = 20;

export default function Timeline() {
  const { tasks, schedule, mood, startFocus } = useAppContext();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [hoveredBlock, setHoveredBlock] = useState(null);
  
  // Update current time every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const hours = [];
  for (let h = START_HOUR; h <= END_HOUR; h++) {
    hours.push(h);
  }

  const formatHour = (hour) => {
    const suffix = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour} ${suffix}`;
  };

  const getBlockStyle = (start, duration) => {
    const top = (start - START_HOUR) * HOUR_HEIGHT;
    const height = duration * HOUR_HEIGHT;
    return { top: `${top}px`, height: `${height}px` };
  };

  const getBlockClass = (type) => {
    switch (type) {
      case 'fixed': return styles.blockFixed;
      case 'focus': return styles.blockFocus;
      case 'break': return styles.blockBreak;
      case 'task': return styles.blockTask;
      default: return '';
    }
  };

  // Current time marker position
  const now = currentTime.getHours() + currentTime.getMinutes() / 60;
  const markerTop = (now - START_HOUR) * HOUR_HEIGHT;
  const showMarker = now >= START_HOUR && now <= END_HOUR;

  // Get scheduled tasks (tasks with scheduledAt set)
  const scheduledTasks = tasks.filter(t => t.scheduledAt !== null && !t.completed);
  
  // Get unscheduled tasks
  const unscheduledTasks = tasks.filter(t => t.scheduledAt === null && !t.completed);

  // Combine fixed schedule with scheduled tasks
  const allBlocks = [
    ...schedule.map(block => ({
      ...block,
      isTask: false,
    })),
    ...scheduledTasks.map(task => ({
      id: `task-${task.id}`,
      taskId: task.id,
      title: task.title,
      start: task.scheduledAt,
      duration: task.duration,
      type: 'task',
      difficulty: task.difficulty,
      isTask: true,
      originalTask: task,
    })),
  ];

  // Handle starting focus mode
  const handleStartFocus = (task) => {
    startFocus(task);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Today</h1>
        <p className={styles.date}>
          {currentTime.toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
          })}
        </p>
      </div>
      
      <div className={styles.timeline}>
        {/* Hour grid */}
        <div className={styles.hoursColumn}>
          {hours.map((hour) => (
            <div key={hour} className={styles.hourLabel} style={{ height: `${HOUR_HEIGHT}px` }}>
              {formatHour(hour)}
            </div>
          ))}
        </div>
        
        {/* Blocks area */}
        <div className={styles.blocksArea}>
          {/* Hour lines */}
          {hours.map((hour) => (
            <div 
              key={hour} 
              className={styles.hourLine} 
              style={{ top: `${(hour - START_HOUR) * HOUR_HEIGHT}px` }}
            />
          ))}
          
          {/* All blocks (fixed events + scheduled tasks) */}
          {allBlocks.map((block) => (
            <div
              key={block.id}
              className={`${styles.block} ${getBlockClass(block.type)}`}
              style={getBlockStyle(block.start, block.duration)}
              onMouseEnter={() => setHoveredBlock(block.id)}
              onMouseLeave={() => setHoveredBlock(null)}
            >
              <div className={styles.blockContent}>
                <span className={styles.blockTitle}>
                  {block.isTask && '📋 '}{block.title}
                </span>
                <span className={styles.blockTime}>
                  {block.duration >= 1 ? `${block.duration}h` : `${block.duration * 60}m`}
                  {block.difficulty && ` · ${block.difficulty}`}
                </span>
              </div>
              
              {/* Focus button for tasks */}
              {block.isTask && hoveredBlock === block.id && (
                <button 
                  className={styles.focusButton}
                  onClick={() => handleStartFocus(block.originalTask)}
                >
                  ▶ Focus
                </button>
              )}
            </div>
          ))}
          
          {/* Current time marker */}
          {showMarker && (
            <div className={styles.timeMarker} style={{ top: `${markerTop}px` }}>
              <div className={styles.timeMarkerDot} />
              <div className={styles.timeMarkerLine} />
            </div>
          )}
        </div>
      </div>

      {/* Unscheduled tasks section */}
      {unscheduledTasks.length > 0 && (
        <div className={styles.unscheduledSection}>
          <h3 className={styles.unscheduledTitle}>Unscheduled Tasks</h3>
          <div className={styles.unscheduledList}>
            {unscheduledTasks.map((task) => (
              <div key={task.id} className={styles.unscheduledTask}>
                <div className={styles.unscheduledTaskInfo}>
                  <span className={styles.unscheduledTaskTitle}>{task.title}</span>
                  <span className={styles.unscheduledTaskMeta}>
                    {task.duration >= 1 ? `${task.duration}h` : `${task.duration * 60}m`} · {task.difficulty}
                  </span>
                </div>
                <button 
                  className={styles.unscheduledFocusButton}
                  onClick={() => handleStartFocus(task)}
                >
                  ▶ Focus
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
