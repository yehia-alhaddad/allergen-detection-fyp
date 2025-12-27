import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import argon2 from 'argon2'
import { z } from 'zod'

const RegisterSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(1)
})

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const parsed = RegisterSchema.safeParse(body)
    if (!parsed.success) return NextResponse.json({ error: 'Invalid input' }, { status: 400 })

    const existing = await prisma.user.findUnique({ where: { email: parsed.data.email } })
    if (existing) return NextResponse.json({ error: 'Email already registered' }, { status: 409 })

    const hash = await argon2.hash(parsed.data.password)
    await prisma.user.create({ data: { email: parsed.data.email, name: parsed.data.name, passwordHash: hash } })
    return NextResponse.json({ ok: true })
  } catch (e) {
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
