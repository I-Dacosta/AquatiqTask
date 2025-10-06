/**
 * Landing Screen Component - Adapted for NextAuth with Microsoft Entra ID
 *
 * This component serves as the application's landing screen with the following features:
 * 1. Displays a welcome message with the user's name if they're logged in
 * 2. Shows navigation options to dashboard for authenticated users
 * 3. Provides Microsoft sign-in for unauthenticated users
 * 4. Includes smooth animations for a polished user experience
 * 5. Shows setup instructions if Microsoft credentials aren't configured
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { handleSignIn } from './actions'

export function LandingPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  // Check if Microsoft credentials are configured
  const hasCredentials = typeof window !== 'undefined' &&
    process.env.NEXT_PUBLIC_AUTH_CONFIGURED === 'true'

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => setIsLoading(false), 800)
    return () => clearTimeout(timer)
  }, [])

  // Animation variants for elements
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6, ease: 'easeOut' as const }
    }
  }

  // Animation for the loading spinner
  const spinnerVariants = {
    animate: {
      rotate: 360,
      transition: {
        repeat: Infinity,
        duration: 1.5,
        ease: 'linear' as const
      }
    }
  }

  // Show welcome and dashboard button if authenticated
  if (status === 'authenticated' && session?.user) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background z-50">
        {/* Gradient background with theme support */}
        <div className="fixed inset-0 z-0 opacity-15 dark:opacity-20 bg-gradient-to-br from-indigo-500/10 via-purple-500/15 to-pink-500/10" />
        <motion.div
          className="flex flex-col items-center relative z-10"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={itemVariants} className="mb-6 text-4xl font-bold">
            <span className="text-primary">Prioriti</span>
            <span className="text-foreground">AI</span>
          </motion.div>
          <motion.div variants={itemVariants} className="mb-8 text-center">
            <h2 className="text-2xl font-medium text-foreground">
              Welcome, <span className="text-primary font-semibold">{session.user.name?.split(' ')[0] || 'User'}</span>
            </h2>
            <p className="text-muted-foreground mt-2">You are signed in.</p>
          </motion.div>
          <motion.button
            variants={itemVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => router.push('/dashboard')}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
          >
            Go to Dashboard
          </motion.button>
        </motion.div>
      </div>
    )
  }

  // Not authenticated: show welcome and sign in button
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background z-50">
      {/* Gradient background with theme support */}
      <div className="fixed inset-0 z-0 opacity-15 dark:opacity-20 bg-gradient-to-br from-indigo-500/10 via-purple-500/15 to-pink-500/10" />
      <motion.div
        className="flex flex-col items-center relative z-10 max-w-4xl mx-auto px-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="mb-6 text-4xl font-bold">
          <span className="text-primary">Prioriti</span>
          <span className="text-foreground">AI</span>
        </motion.div>
        <motion.div variants={itemVariants} className="mb-8 text-center">
          <h2 className="text-2xl font-medium text-foreground">
            Welcome to PrioritiAI
          </h2>
          <p className="text-muted-foreground mt-2">
            Sign in with Microsoft to get started.
          </p>
        </motion.div>

        {/* Show setup notice if credentials aren't configured */}
        {!hasCredentials ? (
          <motion.div variants={itemVariants} className="w-full max-w-2xl">
            <Card className="border-yellow-500/50">
              <CardHeader>
                <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-500">
                  <AlertCircle className="h-5 w-5" />
                  <CardTitle>Setup Required</CardTitle>
                </div>
                <CardDescription className="text-left">
                  To use Microsoft authentication, you need to configure your Azure credentials:
                </CardDescription>
              </CardHeader>
              <CardContent className="text-left space-y-3">
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>Follow the guide in <code className="bg-muted px-2 py-1 rounded">AUTHENTICATION.md</code></li>
                  <li>Set up your Azure app registration</li>
                  <li>Add credentials to <code className="bg-muted px-2 py-1 rounded">.env.local</code></li>
                  <li>Restart the development server</li>
                </ol>
                <p className="text-xs text-muted-foreground pt-2">
                  See <code className="bg-muted px-1.5 py-0.5 rounded">QUICKSTART.md</code> for a 5-minute setup guide.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <>
            <motion.form
              variants={itemVariants}
              className="mb-8"
              action={handleSignIn}
            >
              <motion.button
                type="submit"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
              >
                Sign In with Microsoft
              </motion.button>
            </motion.form>
            {/* Loading Spinner */}
            {(status === 'loading' || isLoading) && (
              <motion.div
                variants={spinnerVariants}
                animate="animate"
                className="w-16 h-16"
              >
                <svg className="w-full h-full" viewBox="0 0 50 50">
                  <circle
                    cx="25"
                    cy="25"
                    r="20"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                    className="text-muted"
                  />
                  <circle
                    cx="25"
                    cy="25"
                    r="20"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray="80"
                    strokeDashoffset="60"
                    className="text-primary"
                  />
                </svg>
              </motion.div>
            )}
          </>
        )}
      </motion.div>
    </div>
  )
}
