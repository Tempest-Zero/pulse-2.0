import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAppContext } from '../context/AppContext';
import MoodControl from './MoodControl';
import styles from './Layout.module.css';

export default function Layout({ children }) {
  const router = useRouter();
  const { mood, openReflection } = useAppContext();
  
  const navItems = [
    { href: '/', label: 'Today', icon: '☀️' },
    { href: '/plan', label: 'Plan', icon: '💬' },
    { href: '/backlog', label: 'Backlog', icon: '📋' },
  ];

  return (
    <div className={styles.container}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>⚡</span>
          <span className={styles.logoText}>PULSE</span>
        </div>
        
        <MoodControl />
        
        <nav className={styles.nav}>
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.navItem} ${
                router.pathname === item.href ? styles.navItemActive : ''
              }`}
            >
              <span className={styles.navIcon}>{item.icon}</span>
              <span className={styles.navLabel}>{item.label}</span>
            </Link>
          ))}
        </nav>
        
        <div className={styles.sidebarFooter}>
          <button className={styles.endDayButton} onClick={openReflection}>
            🌙 End Day
          </button>
          <p className={styles.tagline}>Your calm time coach</p>
        </div>
      </aside>
      
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
