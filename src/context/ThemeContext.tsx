"use client";
import React, { createContext, useContext, useEffect, useState } from 'react';
export const THEMES = {
    onyx: {
        name: "Onyx",
        type: "dark",
        colors: {
            bg: "#0A0A0A",
            surface: "#171717",
            border: "#262626",
            textMain: "#EDEDED",
            textMuted: "#737373",
            accent: "#EDEDED",
            accentBg: "#EDEDED",
            accentText: "#000000"
        }
    },
    titanium: {
        name: "Titanium",
        type: "light",
        colors: {
            bg: "#F1F5F9",
            surface: "#E2E8F0",
            border: "#CBD5E1",
            textMain: "#0F172A",
            textMuted: "#64748B",
            accent: "#334155",
            accentBg: "#334155",
            accentText: "#FFFFFF"
        }
    },
    ghost: {
        name: "Ghost",
        type: "light",
        colors: {
            bg: "#F8F9FA",
            surface: "#E9ECEF",
            border: "#DEE2E6",
            textMain: "#212529",
            textMuted: "#ADB5BD",
            accent: "#212529",
            accentBg: "#212529",
            accentText: "#FFFFFF"
        }
    },
    royalVoid: {
        name: "Royal Void",
        type: "dark",
        colors: {
            bg: "#0B0014",
            surface: "#18002E",
            border: "#2E1065",
            textMain: "#FAF5FF",
            textMuted: "#A78BFA",
            accent: "#C084FC",
            accentBg: "#C084FC",
            accentText: "#000000"
        }
    },
    ceramicGrey: {
        name: "Ceramic Grey",
        type: "light",
        colors: {
            bg: "#F8FAFC",
            surface: "#F1F5F9",
            border: "#E2E8F0",
            textMain: "#0F172A",
            textMuted: "#64748B",
            accent: "#475569",
            accentBg: "#475569",
            accentText: "#FFFFFF"
        }
    },
    matteGraphite: {
        name: "Matte Graphite",
        type: "light",
        colors: {
            bg: "#F3F4F6",
            surface: "#E5E7EB",
            border: "#D1D5DB",
            textMain: "#111827",
            textMuted: "#6B7280",
            accent: "#111827",
            accentBg: "#111827",
            accentText: "#FFFFFF"
        }
    },
    ashWhite: {
        name: "Ash White",
        type: "light",
        colors: {
            bg: "#FAFAFA",
            surface: "#F4F4F5",
            border: "#E4E4E7",
            textMain: "#18181B",
            textMuted: "#A1A1AA",
            accent: "#18181B",
            accentBg: "#18181B",
            accentText: "#FFFFFF"
        }
    }
};
type ThemeKey = keyof typeof THEMES;
type ThemeConfig = typeof THEMES['onyx'];
interface ThemeContextType {
    activeTheme: ThemeKey;
    theme: ThemeConfig;
    setTheme: (key: ThemeKey) => void;
    isDark: boolean;
}
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);
export const ThemeProvider = ({ children }: {
    children: React.ReactNode;
}) => {
    const [activeTheme, setActiveTheme] = useState<ThemeKey>('onyx');
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
        const saved = localStorage.getItem('sentinel-theme');
        if (saved && saved in THEMES) {
            setActiveTheme(saved as ThemeKey);
        }
    }, []);
    const handleSetTheme = (key: ThemeKey) => {
        setActiveTheme(key);
        localStorage.setItem('sentinel-theme', key);
    };
    return (<ThemeContext.Provider value={{
            activeTheme,
            theme: THEMES[activeTheme],
            setTheme: handleSetTheme,
            isDark: THEMES[activeTheme].type === 'dark'
        }}>
      
      <div style={{ visibility: mounted ? 'visible' : 'hidden' }}>
        {children}
      </div>
    </ThemeContext.Provider>);
};
export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
