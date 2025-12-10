import { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import styles from './TaskList.module.css';

export default function TaskList() {
  const { tasks, addTask, deleteTask, toggleTask, scheduleTask, unscheduleTask } = useAppContext();
  const [newTask, setNewTask] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleAddTask = (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    
    addTask(newTask, 1, 'medium');
    setNewTask('');
    setShowForm(false);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return styles.difficultyEasy;
      case 'medium': return styles.difficultyMedium;
      case 'hard': return styles.difficultyHard;
      default: return '';
    }
  };

  const pendingTasks = tasks.filter(t => !t.completed);
  const completedTasks = tasks.filter(t => t.completed);
  const totalHours = pendingTasks.reduce((sum, t) => sum + t.duration, 0);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Backlog</h1>
          <p className={styles.subtitle}>
            {pendingTasks.length} tasks · {totalHours}h estimated
          </p>
        </div>
        <button 
          className={styles.addButton}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Add Task'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAddTask} className={styles.form}>
          <input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="What needs to be done?"
            className={styles.input}
            autoFocus
          />
          <button type="submit" className={styles.submitButton}>
            Add
          </button>
        </form>
      )}

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>To Do</h2>
        <div className={styles.taskGrid}>
          {pendingTasks.map((task) => (
            <div key={task.id} className={styles.taskCard}>
              <div className={styles.taskHeader}>
                <button 
                  className={styles.checkbox}
                  onClick={() => toggleTask(task.id)}
                />
                <h3 className={styles.taskTitle}>{task.title}</h3>
                <button 
                  className={styles.deleteButton}
                  onClick={() => deleteTask(task.id)}
                >
                  ×
                </button>
              </div>
              <div className={styles.taskMeta}>
                <span className={styles.duration}>
                  {task.duration >= 1 ? `${task.duration}h` : `${task.duration * 60}m`}
                </span>
                <span className={`${styles.difficulty} ${getDifficultyColor(task.difficulty)}`}>
                  {task.difficulty}
                </span>
                {task.scheduledAt !== null ? (
                  <button 
                    className={styles.scheduledBadge}
                    onClick={() => unscheduleTask(task.id)}
                    title="Click to unschedule"
                  >
                    📅 {task.scheduledAt > 12 ? `${task.scheduledAt - 12} PM` : `${task.scheduledAt} AM`}
                  </button>
                ) : (
                  <span className={styles.unscheduledBadge}>Not scheduled</span>
                )}
              </div>
            </div>
          ))}
          {pendingTasks.length === 0 && (
            <p className={styles.emptyState}>No pending tasks. Nice work! 🎉</p>
          )}
        </div>
      </div>

      {completedTasks.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Completed</h2>
          <div className={styles.taskGrid}>
            {completedTasks.map((task) => (
              <div key={task.id} className={`${styles.taskCard} ${styles.taskCompleted}`}>
                <div className={styles.taskHeader}>
                  <button 
                    className={`${styles.checkbox} ${styles.checkboxChecked}`}
                    onClick={() => toggleTask(task.id)}
                  >
                    ✓
                  </button>
                  <h3 className={styles.taskTitle}>{task.title}</h3>
                  <button 
                    className={styles.deleteButton}
                    onClick={() => deleteTask(task.id)}
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
