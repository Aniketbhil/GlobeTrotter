import { create } from 'zustand';

export const useThemeStore = create((set) => ({
  theme: localStorage.getItem('globetrotter_theme') || 'light',
  
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('globetrotter_theme', newTheme);
    
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    return { theme: newTheme };
  }),

  // Call this once in App.jsx to set initial state
  initTheme: () => {
    const theme = localStorage.getItem('globetrotter_theme') || 'light';
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    set({ theme });
  }
}));