import { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import styles from './Reflection.module.css';

const distractionTags = [
  { id: 'meetings', label: 'Meetings', emoji: '📅' },
  { id: 'fatigue', label: 'Fatigue', emoji: '😴' },
  { id: 'notifications', label: 'Notifications', emoji: '🔔' },
  { id: 'adhoc', label: 'Ad-hoc requests', emoji: '💬' },
  { id: 'personal', label: 'Personal', emoji: '🏠' },
  { id: 'unclear', label: 'Unclear priorities', emoji: '❓' },
];

const moodEmojis = ['😫', '😕', '😐', '🙂', '😊'];

export default function Reflection() {
  const { closeReflection, saveReflection, tasks } = useAppContext();
  const [moodScore, setMoodScore] = useState(3); // 1-5 scale
  const [selectedTags, setSelectedTags] = useState([]);
  const [note, setNote] = useState('');

  // Calculate stats
  const completedTasks = tasks.filter(t => t.completed).length;
  const totalTasks = tasks.length;

  const toggleTag = (tagId) => {
    setSelectedTags(prev => 
      prev.includes(tagId) 
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleSave = () => {
    saveReflection({
      moodScore,
      distractions: selectedTags,
      note,
      completedTasks,
      totalTasks,
    });
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        {/* Scrollable Content Area */}
        <div className={styles.modalContent}>
          {/* Header */}
          <div className={styles.header}>
            <span className={styles.headerEmoji}>🌙</span>
            <h2 className={styles.headerTitle}>Day Complete</h2>
            <p className={styles.headerSubtitle}>
              You completed {completedTasks} of {totalTasks} tasks
            </p>
          </div>

          {/* Mood Slider */}
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>How did today feel?</h3>
            <div className={styles.moodSlider}>
              <span className={styles.moodLabel}>Drained</span>
              <div className={styles.sliderWrapper}>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={moodScore}
                  onChange={(e) => setMoodScore(Number(e.target.value))}
                  className={styles.slider}
                />
                <div className={styles.moodEmojis}>
                  {moodEmojis.map((emoji, index) => (
                    <span 
                      key={index}
                      className={`${styles.moodEmoji} ${moodScore === index + 1 ? styles.moodEmojiActive : ''}`}
                    >
                      {emoji}
                    </span>
                  ))}
                </div>
              </div>
              <span className={styles.moodLabel}>Energized</span>
            </div>
          </div>

          {/* Distraction Tags */}
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>What got in the way?</h3>
            <div className={styles.tags}>
              {distractionTags.map((tag) => (
                <button
                  key={tag.id}
                  className={`${styles.tag} ${selectedTags.includes(tag.id) ? styles.tagActive : ''}`}
                  onClick={() => toggleTag(tag.id)}
                >
                  <span>{tag.emoji}</span>
                  <span>{tag.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Note */}
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Anything to note?</h3>
            <textarea
              className={styles.textarea}
              placeholder="Optional thoughts about today..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        {/* Actions - Fixed at bottom */}
        <div className={styles.actions}>
          <button className={styles.cancelButton} onClick={closeReflection}>
            Skip
          </button>
          <button className={styles.saveButton} onClick={handleSave}>
            Save & Close Day
          </button>
        </div>
      </div>
    </div>
  );
}



