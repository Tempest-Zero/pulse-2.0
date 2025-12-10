import { useAppContext } from '../context/AppContext';
import styles from './MoodControl.module.css';

const moods = [
  { id: 'calm', label: 'Calm', emoji: '🌿', description: 'Peaceful & balanced' },
  { id: 'energized', label: 'Energized', emoji: '🔥', description: 'Ready to tackle anything' },
  { id: 'focused', label: 'Focused', emoji: '🎯', description: 'Deep work mode' },
  { id: 'tired', label: 'Tired', emoji: '🌙', description: 'Taking it easy' },
];

export default function MoodControl() {
  const { mood, setMood } = useAppContext();

  return (
    <div className={styles.container}>
      <p className={styles.label}>How are you feeling?</p>
      <div className={styles.moodGrid}>
        {moods.map((m) => (
          <button
            key={m.id}
            onClick={() => setMood(m.id)}
            className={`${styles.moodButton} ${
              mood === m.id ? styles.moodButtonActive : ''
            }`}
            title={m.description}
          >
            <span className={styles.moodEmoji}>{m.emoji}</span>
            <span className={styles.moodLabel}>{m.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
