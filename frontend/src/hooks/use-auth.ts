import { useState, useEffect, useCallback } from 'react';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isReady, setIsReady] = useState<boolean>(false);
  
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsReady(true);
    
    const handleUnauthorized = () => {
      logout();
    };
    
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);
  
  const login = useCallback((token: string) => {
    localStorage.setItem('auth_token', token);
    setIsAuthenticated(true);
  }, []);
  
  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    window.location.href = '/'; 
  }, []);
  
  return { isAuthenticated, isReady, login, logout };
}
