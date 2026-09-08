import type { Metadata } from 'next';
import './globals.css';
import 'maplibre-gl/dist/maplibre-gl.css';
import 'katex/dist/katex.min.css';
import './studio.css';
import './globe.css';

export const metadata: Metadata = { title: 'SWITCH Workbench', description: 'Ali’s local workspace for power-system models, scenarios and results.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
