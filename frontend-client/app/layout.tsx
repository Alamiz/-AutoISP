"use client"

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "@/providers";
import { Toaster } from "@/components/ui/sonner";
import Titlebar from "@/components/title-bar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full overflow-hidden">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-full overflow-hidden flex flex-col`}
      >
        <Titlebar />
        <div className="flex-1 overflow-hidden">
          <Providers>
            {children}
            <Toaster />
          </Providers>
        </div>
      </body>
    </html>
  );
}