import { create } from 'zustand';

interface UIState {
  isMobileMenuOpen: boolean;
  isDarkMode: boolean;
  
  // Actions
  toggleMobileMenu: () => void;
  toggleDarkMode: () => void;
  setDarkMode: (isDark: boolean) => void;
}

export const useUIStore = create<UIState>((set) => {
  // Initialize dark mode from localStorage or system preference
  const prefersDarkMode = 
    localStorage.getItem('darkMode') === 'true' || 
    (localStorage.getItem('darkMode') === null && 
      window.matchMedia('(prefers-color-scheme: dark)').matches);
  
  // Apply dark mode class to document if needed
  if (prefersDarkMode) {
    document.documentElement.classList.add('dark');
  }
  
  return {
    isMobileMenuOpen: false,
    isDarkMode: prefersDarkMode,
    
    toggleMobileMenu: () => set((state) => ({ isMobileMenuOpen: !state.isMobileMenuOpen })),
    
    toggleDarkMode: () => set((state) => {
      const newDarkMode = !state.isDarkMode;
      localStorage.setItem('darkMode', String(newDarkMode));
      
      // Toggle dark class on document
      if (newDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      
      return { isDarkMode: newDarkMode };
    }),
    
    setDarkMode: (isDark) => set(() => {
      localStorage.setItem('darkMode', String(isDark));
      
      // Set dark class on document
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      
      return { isDarkMode: isDark };
    }),
  };
});
