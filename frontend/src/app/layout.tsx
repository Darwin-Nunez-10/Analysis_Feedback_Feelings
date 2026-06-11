import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
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
  title: "Análisis de Feedback y Sentimiento | EIF-4200",
  description:
    "Dashboard gerencial para analizar comentarios de clientes con PLN y análisis de sentimiento en español.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full`}
      style={{ backgroundColor: "#0b0f19", colorScheme: "dark" }}
    >
      <body
        className="min-h-full bg-background text-foreground antialiased"
        style={{ backgroundColor: "#0b0f19", color: "#e2e8f0" }}
      >
        {children}
      </body>
    </html>
  );
}
