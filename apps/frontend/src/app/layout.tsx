import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/lib/theme-provider-client";
import { SkipToContent } from "@/components/layout/skip-to-content";

const GeistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const GeistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KidsAI Studio — Autonomous YouTube Kids Video Generator",
  description: "Generate complete, original, educational YouTube Kids videos from a single prompt.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AuthProvider>
        <html
          lang={typeof window !== 'undefined' ? undefined : 'en'}
          className={`${GeistSans.variable} ${GeistMono.variable} h-full antialiased`}
        >
          <body className="min-h-full flex flex-col bg-background-primary text-foreground-primary bg-background-primary font-sans">
            <SkipToContent />
            <main id="main-content" className="flex-1">
              <ThemeProvider>
                {children}
              </ThemeProvider>
            </main>
          </body>
        </html>
      </AuthProvider>
    </>
  );
}