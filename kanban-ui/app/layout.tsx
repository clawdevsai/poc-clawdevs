import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClawDevs | Agent Kanban",
  description: "Monitoramento em tempo real do pipeline de agentes ClawDevs no Minikube.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="antialiased dark">
        {children}
      </body>
    </html>
  );
}
