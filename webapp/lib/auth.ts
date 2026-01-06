import NextAuth, { type AuthOptions, getServerSession } from 'next-auth'
import Credentials from 'next-auth/providers/credentials'
import { prisma } from '@/lib/db'
import argon2 from 'argon2'

export const authOptions: AuthOptions = {
  session: { strategy: 'jwt' },
  pages: {
    // Align with the actual sign-in route we expose in app/signin
    signIn: '/signin'
  },
  providers: [
    Credentials({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null
        const user = await prisma.user.findUnique({ where: { email: credentials.email } })
        if (!user) return null
        const ok = await argon2.verify(user.passwordHash, credentials.password)
        if (!ok) return null
        return { id: user.id, email: user.email, name: user.name }
      }
    })
  ]
}

// NextAuth v4 - NextAuth() returns { handlers: { GET, POST }, ... }
const { handlers: authHandlers, auth: auth_deprecated } = NextAuth(authOptions)
export { authHandlers }

// Server-side session helper (v4-compatible)
export async function auth() {
  return getServerSession(authOptions)
}
