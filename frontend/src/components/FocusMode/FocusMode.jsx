import { useState, useEffect } from 'react';
import { useAppContext } from '../../context/AppContext';
import styles from './FocusMode.module.css';

export default function FocusMode() {
  const { focusTask, focusDuration, focusStartTime, endFocus, extendFocus } = useAppContext();
  const [timeLeft, setTimeLeft] = useState(focusDuration * 60); // seconds
  const [isPaused, setIsPaused] = useState(false);

  // Calculate total duration in seconds
  const totalSeconds = focusDuration * 60;

  // Timer countdown
  useEffect(() => {
    if (!focusTask || isPaused) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - focusStartTime) / 1000);
      const remaining = totalSeconds - elapsed;
      
      if (remaining <= 0) {
        setTimeLeft(0);
        clearInterval(interval);
      } else {
        setTimeLeft(remaining);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [focusTask, focusStartTime, totalSeconds, isPaused]);

  // Reset timeLeft when focusDuration changes (extend)
  useEffect(() => {
    if (focusStartTime) {
      const elapsed = Math.floor((Date.now() - focusStartTime) / 1000);
      setTimeLeft(totalSeconds - elapsed);
    }
  }, [focusDuration, focusStartTime, totalSeconds]);

  if (!focusTask) return null;

  // Format time as HH:MM:SS
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Progress percentage
  const progress = totalSeconds > 0 ? ((totalSeconds - timeLeft) / totalSeconds) * 100 : 0;

  // Handle complete
  const handleComplete = () => {
    endFocus(true);
  };

  // Handle exit without completing
  const handleExit = () => {
    endFocus(false);
  };

  // Handle extend
  const handleExtend = () => {
    extendFocus(15);
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.container}>
        {/* Task info */}
        <div className={styles.taskInfo}>
          <h1 className={styles.taskTitle}>{focusTask.title}</h1>
          <p className={styles.taskMeta}>
            {focusTask.difficulty} · {focusTask.duration}h
          </p>
        </div>

        {/* Timer circle */}
        <div className={styles.timerWrapper}>
          <div className={styles.timerCircle}>
            <svg className={styles.timerSvg} viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                className={styles.timerBg}
                cx="50"
                cy="50"
                r="45"
                fill="none"
                strokeWidth="4"
              />
              {/* Progress circle */}
              <circle
                className={styles.timerProgress}
                cx="50"
                cy="50"
                r="45"
                fill="none"
                strokeWidth="4"
                strokeDasharray={`${2 * Math.PI * 45}`}
                strokeDashoffset={`${2 * Math.PI * 45 * (1 - progress / 100)}`}
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div className={styles.timerContent}>
              <span className={styles.timerTime}>{formatTime(timeLeft)}</span>
              <span className={styles.timerLabel}>remaining</span>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill} 
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className={styles.progressText}>{Math.round(progress)}% complete</p>

        {/* Action buttons */}
        <div className={styles.actions}>
          <button 
            className={styles.completeButton}
            onClick={handleComplete}
          >
            Complete Early
          </button>
          <button 
            className={styles.extendButton}
            onClick={handleExtend}
          >
            +15 min
          </button>
          <button 
            className={styles.exitButton}
            onClick={handleExit}
          >
            Exit
          </button>
        </div>

        {/* Breathing indicator */}
        <div className={styles.breathingWrapper}>
          <div className={styles.breathingCircle} />
          <p className={styles.breathingText}>Stay focused, you've got this</p>
        </div>
      </div>
    </div>
  );
}



