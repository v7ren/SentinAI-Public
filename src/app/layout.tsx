import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { FileProvider } from "../context/FileContext";
import { ThemeProvider } from "../context/ThemeContext";
import "./globals.css";
const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});
const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});
export const metadata: Metadata = {
    title: "SentinAI",
    description: "Instant vulnerability scanning for your projects.",
    icons: {
        icon: "/logo.svg",
        apple: "/logo.svg",
    },
};
export default function RootLayout({ children, }: Readonly<{
    children: React.ReactNode;
}>) {
    return (<html lang="en">
      
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#050505]`}>
        <ThemeProvider>
          <FileProvider>
            {children}
          </FileProvider>
        </ThemeProvider>
      </body>
    </html>);
}
