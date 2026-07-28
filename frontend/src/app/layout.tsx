import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Vynetra - AI Presentation Creator',
  description: 'One Prompt. A Complete Presentation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
