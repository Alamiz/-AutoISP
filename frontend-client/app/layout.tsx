import type { Metadata } from "next";
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

export const metadata: Metadata = {
  title: "Gmail Automation",
  description: "Streamline your Gmail workflow",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full overflow-hidden">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-full overflow-hidden `}
      >
        <div className="flex flex-col h-screen w-screen overflow-hidden">
          <Titlebar />
          <div className="flex-1 overflow-y-auto overflow-x-hidden">
            <Providers>
              {children}
            </Providers>
          </div>
        </div>
        <Toaster />
      </body>
    </html>
  );
}