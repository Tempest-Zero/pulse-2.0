import { AppProvider, useAppContext } from '../context/AppContext';
import Layout from '../components/Layout';
import FocusMode from '../components/FocusMode/FocusMode';
import Reflection from '../components/Reflection/Reflection';
import '../styles/globals.css';

// Inner component that uses the context
function AppContent({ Component, pageProps }) {
  const { mood, focusTask, showReflection } = useAppContext();

  return (
    <div data-mood={mood}>
      <Layout>
        <Component {...pageProps} />
      </Layout>
      
      {/* Focus Mode Overlay */}
      {focusTask && <FocusMode />}
      
      {/* Reflection Modal */}
      {showReflection && <Reflection />}
    </div>
  );
}

// Main App wrapped with provider
export default function App({ Component, pageProps }) {
  return (
    <AppProvider>
      <AppContent Component={Component} pageProps={pageProps} />
    </AppProvider>
  );
}
