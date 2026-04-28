import { useState } from 'react';
import Login from './Login';
import Register from './Register';
import Dashboard from './Dashboard';

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [currentScreen, setCurrentScreen] = useState<'login' | 'register'>('login');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
  };

  const handleLoginSuccess = (newToken: string) => {
    localStorage.setItem('access_token', newToken);
    setToken(newToken);
  };

  if (token && token !== "null" && token !== "undefined") {
    return <Dashboard onLogout={handleLogout} />;
  }

  return (
    <div>
      {currentScreen === 'login' ? (
        <Login 
          onLoginSuccess={handleLoginSuccess} 
          onNavigateToRegister={() => setCurrentScreen('register')} 
        />
      ) : (
        <Register onNavigateToLogin={() => setCurrentScreen('login')} />
      )}
    </div>
  );
}