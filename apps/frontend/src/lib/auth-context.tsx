"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, getMeApi, loginApi, registerApi, updateProfileApi } from '@/lib/api';

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
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Session Recovery on Mount
    const savedToken = typeof window !== 'undefined' ? localStorage.getItem('kidsai_auth_token') : null;
    if (savedToken) {
      setToken(savedToken);
      getMeApi(savedToken)
        .then((profile) => setUser(profile))
        .catch(() => {
          localStorage.removeItem('kidsai_auth_token');
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
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
    const updated = await updateProfileApi(fullName, avatarUrl);
    setUser(updated);
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
