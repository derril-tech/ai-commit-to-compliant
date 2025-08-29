'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { notifications } from '@mantine/notifications';
import { api } from './api';

interface User {
  id: string;
  email: string;
  name: string;
  org_id: string;
  workspace_id: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (provider: 'github' | 'google') => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await api.get('/auth/me');
        setUser(response.data);
      }
    } catch (error) {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (provider: 'github' | 'google') => {
    try {
      // In a real implementation, this would redirect to OAuth provider
      // For now, we'll simulate a successful login
      const mockResponse = {
        access_token: 'mock_token_' + Date.now(),
        user: {
          id: 'user-123',
          email: 'user@example.com',
          name: 'Test User',
          org_id: 'org-123',
          workspace_id: 'workspace-123',
        },
      };

      localStorage.setItem('auth_token', mockResponse.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${mockResponse.access_token}`;
      setUser(mockResponse.user);

      notifications.show({
        title: 'Welcome!',
        message: 'Successfully signed in',
        color: 'green',
      });
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to sign in',
        color: 'red',
      });
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
      
      notifications.show({
        title: 'Signed out',
        message: 'You have been signed out',
        color: 'blue',
      });
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
