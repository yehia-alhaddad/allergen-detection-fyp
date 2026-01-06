import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function POST() {
  try {
    const cookieStore = await cookies()
    cookieStore.delete({ name: 'next-auth.session-token', path: '/' })
    const res = NextResponse.json({ ok: true })
    res.cookies.set('next-auth.session-token', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 0,
      path: '/',
    })
    return res
  } catch (err) {
    return NextResponse.json({ error: 'Logout failed' }, { status: 500 })
  }
}
