/**
 * Server Actions for Authentication
 *
 * These server-side functions integrate with NextAuth to support Microsoft Entra ID sign-in.
 * Follow Microsoft guidance for native authentication flows to ensure secure configuration:
 * https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-native-authentication-single-page-app-sdk-sign-in
 */

'use server'

import { signIn as nextAuthSignIn } from '@/auth'

export async function handleSignIn() {
  await nextAuthSignIn('microsoft-entra-id', { redirectTo: '/dashboard' })
}
