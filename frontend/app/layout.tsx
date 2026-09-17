import './globals.css';

export const metadata = {
  title: 'AgentGuard Console',
  description: 'Agent evaluation and deployment risk console',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
