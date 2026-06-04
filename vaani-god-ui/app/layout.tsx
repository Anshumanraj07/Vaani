import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Image from "next/image";
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
  title: "Vaani | Cognitive AI",
  description: "Real-time cognitive telemetry.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <body className="bg-gray-50 text-gray-900">
        
        {/* 🌟 GLOBAL NAVBAR / HEADER */}
        <header className="w-full bg-white border-b border-gray-200 py-3 px-6 flex items-center gap-3 shadow-sm sticky top-0 z-50">
          <Image 
            src="/logo.png" 
            alt="Vaani Logo" 
            width={40} 
            height={40} 
            className="rounded-lg border border-gray-100"
          />
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight text-black leading-tight">
              Vaani
            </h1>
            <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-widest">
              Cognitive Diagnostic System
            </p>
          </div>
        </header>

        {/* 🌟 MAIN APP CONTENT */}
        <main className="w-full max-w-7xl mx-auto p-4 md:p-8">
          {children}
        </main>

      </body>
    </html>
  );
}