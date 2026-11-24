import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "C9 Draft & Scout",
  description: "Cloud9 macro scouting and fearless draft coaching workspace",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}