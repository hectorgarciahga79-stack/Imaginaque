import "./globals.css";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "AMAZON SNIPER",
  description: "Motor autónomo de detección de errores de precio en Amazon.es",
  robots: { index: false, follow: false },
};
export const viewport: Viewport = { themeColor: "#07080a", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen font-sans">{children}</body>
    </html>
  );
}
