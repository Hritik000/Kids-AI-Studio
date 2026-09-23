"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, getMeApi, loginApi, registerApi, updateProfileApi } from '@/lib/api';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (fullName: string, email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
  updateProfile: (fullName: string, avatarUrl?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const getInitialToken = () =>
    typeof window !== 'undefined' ? localStorage.getItem('kidsai_auth_token') : null;

  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(getInitialToken);
  // Only start in a loading state if there's a token to validate; otherwise
  // there's nothing to fetch and we can render immediately.
  const [isLoading, setIsLoading] = useState<boolean>(() => !!getInitialToken());

  useEffect(() => {
    // Session Recovery on Mount: token (if any) is already set via lazy initial state above.
    if (token) {
      getMeApi(token)
        .then((profile) => setUser(profile))
        .catch((error: unknown) => {
          console.error("Session recovery failed:", getErrorMessage(error));
          localStorage.removeItem('kidsai_auth_token');
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email: string, password: string, rememberMe: boolean = false) => {
    setIsLoading(true);
    try {
      const res = await loginApi(email, password, rememberMe);
      setToken(res.token);
      setUser(res.user);
      if (typeof window !== 'undefined') {
        localStorage.setItem('kidsai_auth_token', res.token);
      }
    } catch (error: unknown) {
      console.error("Login failed:", getErrorMessage(error));
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (fullName: string, email: string, password: string, confirmPassword: string) => {
    setIsLoading(true);
    try {
      const res = await registerApi(fullName, email, password, confirmPassword);
      setToken(res.token);
      setUser(res.user);
      if (typeof window !== 'undefined') {
        localStorage.setItem('kidsai_auth_token', res.token);
      }
    } catch (error: unknown) {
      console.error("Registration failed:", getErrorMessage(error));
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('kidsai_auth_token');
    }
  };

  const updateProfile = async (fullName: string, avatarUrl?: string) => {
    try {
      const updated = await updateProfileApi(fullName, avatarUrl);
      setUser(updated);
    } catch (error: unknown) {
      console.error("Profile update failed:", getErrorMessage(error));
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
