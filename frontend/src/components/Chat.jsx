import { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import styles from './Chat.module.css';

// Mock AI responses
const mockResponses = [
  "I see you have a busy morning! I'd suggest scheduling your deep work session between 9-11 AM when your energy is typically highest.",
  "Based on your mood today, I recommend keeping meetings clustered together to protect your focus time.",
  "How about we block 2 hours for that project? I'll schedule it right after your lunch break when you've recharged.",
  "I notice you have a gap at 3 PM. Would you like me to add a 30-minute buffer there for unexpected tasks?",
  "Great! I've drafted a schedule that gives you 4 hours of focused work time. Want me to show you the preview?",
];

export default function Chat() {
  const { mood, tasks, scheduleTask } = useAppContext();
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'ai',
      content: "Hi there! I'm your scheduling assistant. Tell me about your tasks for today and I'll help you plan your time wisely. 🌟",
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Simulate AI typing
    setIsTyping(true);
    setTimeout(() => {
      const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
      const aiMessage = {
        id: Date.now() + 1,
        role: 'ai',
        content: randomResponse,
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Plan Your Day</h1>
        <p className={styles.subtitle}>Chat with PULSE to organize your schedule</p>
      </div>

      <div className={styles.chatWindow}>
        <div className={styles.messages}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${
                message.role === 'user' ? styles.messageUser : styles.messageAi
              }`}
            >
              {message.role === 'ai' && (
                <div className={styles.avatar}>⚡</div>
              )}
              <div className={styles.bubble}>
                {message.content}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className={`${styles.message} ${styles.messageAi}`}>
              <div className={styles.avatar}>⚡</div>
              <div className={`${styles.bubble} ${styles.typing}`}>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className={styles.inputArea}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tell me about your tasks..."
            className={styles.input}
          />
          <button type="submit" className={styles.sendButton}>
            Send
          </button>
        </form>
      </div>

      <div className={styles.suggestions}>
        <p className={styles.suggestionsLabel}>Try saying:</p>
        <div className={styles.suggestionChips}>
          <button 
            className={styles.chip}
            onClick={() => setInput("I need to finish a report by 5pm")}
          >
            I need to finish a report by 5pm
          </button>
          <button 
            className={styles.chip}
            onClick={() => setInput("Schedule some focus time for coding")}
          >
            Schedule focus time for coding
          </button>
          <button 
            className={styles.chip}
            onClick={() => setInput("What does my day look like?")}
          >
            What does my day look like?
          </button>
        </div>
      </div>
    </div>
  );
}

