import React, { createContext, useContext, ReactNode } from 'react';
import { theme, Theme } from './theme';

const ThemeContext = createContext<Theme>(theme);

export const useTheme = () => useContext(ThemeContext);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
