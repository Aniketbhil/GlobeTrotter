import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('globeTrotter_token') || null,
  user: null,
  isUserLoading: false,
  
  setToken: (token) => {
    localStorage.setItem('globeTrotter_token', token);
    set({ token });
  },
  
  logout: () => {
    localStorage.removeItem('globeTrotter_token');
    set({ token: null, user: null });
  },
  
  setUser: (user) => set({ user }),
  setLoading: (isLoading) => set({ isUserLoading: isLoading }),
}));