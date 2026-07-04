import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "LearnFlow — IT карьера начинается здесь",
  description:
    "Профессиональная LMS платформа с живыми менторами, автоматической проверкой кода и верифицируемыми сертификатами. Узбекистан.",
  keywords: ["LearnFlow", "курсы программирования", "Узбекистан", "IT обучение"],
  openGraph: {
    title: "LearnFlow",
    description: "IT карьера начинается здесь",
    locale: "ru_RU",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className="dark">
      <head>
        {/*
         * Preconnect for Google Fonts — fonts are loaded via @import in globals.css.
         * These <link> tags speed up the DNS + TLS handshake.
         */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </head>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
