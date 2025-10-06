import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import { createMockTask, getMockTasks } from '@/lib/mock-tasks'
import type { Task } from '@/types/task'

const isSupabaseEnabled = Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL)

export async function GET() {
  if (isSupabaseEnabled) {
    return NextResponse.json({ error: 'Database integration is not configured in this environment.' }, { status: 501 })
  }

  return NextResponse.json(getMockTasks())
}

export async function POST(request: NextRequest) {
  if (isSupabaseEnabled) {
    return NextResponse.json({ error: 'Database integration is not configured in this environment.' }, { status: 501 })
  }

  try {
    const body = (await request.json()) as Partial<Task>
    const task = createMockTask(body)
    return NextResponse.json(task, { status: 201 })
  } catch (error) {
    console.error('Error creating mock task', error)
    return NextResponse.json({ error: 'Failed to create task' }, { status: 400 })
  }
}
