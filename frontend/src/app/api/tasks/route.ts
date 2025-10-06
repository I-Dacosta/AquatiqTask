import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import taskOperations from '@/lib/postgres-tasks'
import type { Task } from '@/types/task'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const status = searchParams.get('status')
    const source = searchParams.get('source')
    const search = searchParams.get('search')
    const urgency_level = searchParams.get('urgency_level')

    const filters: any = {}
    if (status) filters.status = status
    if (source) filters.source = source
    if (search) filters.search = search
    if (urgency_level) filters.urgency_level = urgency_level

    const tasks = await taskOperations.getTasks(filters)
    return NextResponse.json(tasks)
  } catch (error) {
    console.error('Error fetching tasks:', error)
    return NextResponse.json(
      { error: 'Failed to fetch tasks from database' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as Partial<Task>
    
    // Forward to n8n webhook for AI processing
    const n8nWebhookUrl = process.env.N8N_WEBHOOK_URL || 'http://31.97.38.31:5678/webhook/prioai-tasks'
    
    const webhookPayload = {
      title: body.title || 'Untitled Task',
      description: body.description || '',
      requester: body.requester || 'frontend@prioai.com',
      est_minutes: body.est_minutes,
      due_text: body.due_at || body.dueDate,
      role_hint: body.role_hint || 'employee'
    }

    const webhookResponse = await fetch(n8nWebhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(webhookPayload)
    })

    if (!webhookResponse.ok) {
      throw new Error(`n8n webhook failed: ${webhookResponse.statusText}`)
    }

    const result = await webhookResponse.json()
    return NextResponse.json(result, { status: 202 })
  } catch (error) {
    console.error('Error creating task:', error)
    return NextResponse.json(
      { error: 'Failed to create task' },
      { status: 500 }
    )
  }
}
