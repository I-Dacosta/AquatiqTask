import { ReduxProvider } from '@/lib/redux-provider'
import { ThemeProvider } from '@/components/theme-provider'
import { CommandMenu } from '@/components/command-menu'
import { SiteHeader } from '@/components/site-header'
import { SessionProvider } from 'next-auth/react'
import './globals.css'
import type { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'TaskPriority - Intelligent Task Management',
  description: 'AI-powered task prioritization and management dashboard with Microsoft authentication',
  keywords: 'task management, AI, prioritization, productivity, dashboard, microsoft',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <SessionProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <ReduxProvider>
              <div className="relative flex min-h-screen flex-col">
                <SiteHeader />
                <main className="flex-1">
                  {children}
                </main>
              </div>
              <CommandMenu />
            </ReduxProvider>
          </ThemeProvider>
        </SessionProvider>
      </body>
    </html>
  )
}
