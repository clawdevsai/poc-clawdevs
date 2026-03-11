import type { Metadata } from "next";
import { Space_Grotesk } from "next/font/google";

import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ui"
});

export const metadata: Metadata = {
  title: "ClawDevs Director Console",
  description: "Painel executivo para acompanhamento do runtime de agentes."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body className={spaceGrotesk.variable}>{children}</body>
    </html>
  );
}
