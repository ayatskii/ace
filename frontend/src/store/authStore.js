import { create } from 'zustand';
import { authApi } from '../api/auth';

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
  
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authApi.login(email, password);
      localStorage.setItem('access_token', data.access_token);
      
      const { data: user } = await authApi.getCurrentUser();
      set({ 
        user, 
        token: data.access_token, 
        isAuthenticated: true,
        isLoading: false 
      });
      return { success: true };
    } catch (error) {
      set({ 
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false 
      });
      return { success: false, error: error.response?.data?.detail };
    }
  },
  
  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.register(userData);
      // Auto-login after registration
      return await useAuthStore.getState().login(userData.email, userData.password);
    } catch (error) {
      set({ 
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false 
      });
      return { success: false, error: error.response?.data?.detail };
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  loadUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
      const { data: user } = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));
