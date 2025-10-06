import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import { updateTask as updateTaskInDatabase } from '@/lib/tasks'
import { taskOperations } from '@/lib/supabase'
import { deleteMockTask, getMockTasks, updateMockTask } from '@/lib/mock-tasks'
import type { Task, TaskStatus } from '@/types/task'

const isSupabaseEnabled = Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL)

const allowedStatuses: TaskStatus[] = ['inbox', 'todo', 'approved', 'in_progress', 'in-progress', 'done']

const normalizeStatus = (status?: TaskStatus) => {
    if (!status) return undefined
    return status === 'in-progress' ? 'in_progress' : status
}

const validateStatus = (status?: TaskStatus) => {
    if (!status) return true
    return allowedStatuses.includes(status)
}

const invalidIdResponse = NextResponse.json({ error: 'Invalid task identifier' }, { status: 400 })

const taskNotFoundResponse = NextResponse.json({ error: 'Task not found' }, { status: 404 })

const notImplementedResponse = NextResponse.json(
    { error: 'Operation requires a configured database backend' },
    { status: 501 }
)

const parseTaskId = (rawId: string) => rawId.trim()

const parseNumericTaskId = (rawId: string) => {
    const numericId = Number(rawId)
    return Number.isNaN(numericId) ? null : numericId
}

const buildUnexpectedErrorResponse = (error: unknown) => {
    console.error('Task API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}

const updateSupabaseTask = async (taskId: string, body: Partial<Task>) => {
    const numericId = parseNumericTaskId(taskId)
    if (numericId === null) {
        return invalidIdResponse
    }

    try {
        if (body.status) {
            if (!validateStatus(body.status)) {
                return NextResponse.json({ error: 'Invalid status' }, { status: 400 })
            }
            const normalized = normalizeStatus(body.status) as TaskStatus | undefined
            const updated = await taskOperations.updateTaskStatus(numericId, normalized as any)
            if (!updated) {
                return taskNotFoundResponse
            }
            return NextResponse.json(updated)
        }

            if (body.override_priority !== undefined || body.override_locked !== undefined) {
                const priority = body.override_priority ?? 50
                const locked = body.override_locked ?? false
            const updated = await taskOperations.updateTaskPriority(numericId, priority, locked)
            if (!updated) {
                return taskNotFoundResponse
            }
            return NextResponse.json(updated)
        }

        const updated = await updateTaskInDatabase(taskId, body)
        if (!updated) {
            return taskNotFoundResponse
        }
        return NextResponse.json(updated)
    } catch (error) {
        return buildUnexpectedErrorResponse(error)
    }
}

const updateMockTaskResponse = (taskId: string, body: Partial<Task>) => {
    if (body.status && !validateStatus(body.status)) {
        return NextResponse.json({ error: 'Invalid status' }, { status: 400 })
    }

    const payload: Partial<Task> = {
        ...body,
        status: normalizeStatus(body.status) as TaskStatus | undefined,
    }

    const updated = updateMockTask(taskId, payload)
    if (!updated) {
        return taskNotFoundResponse
    }
    return NextResponse.json(updated)
}

export async function GET(_request: NextRequest, context: { params: { id: string } }) {
    const taskId = parseTaskId(context.params.id)

    if (isSupabaseEnabled) {
        const numericId = parseNumericTaskId(taskId)
        if (numericId === null) {
            return invalidIdResponse
        }

        try {
            const task = await taskOperations.getTask(numericId)
            if (!task) {
                return taskNotFoundResponse
            }
            return NextResponse.json(task)
        } catch (error) {
            return buildUnexpectedErrorResponse(error)
        }
    }

    const task = getMockTasks().find((item) => String(item.id) === taskId)
    if (!task) {
        return taskNotFoundResponse
    }
    return NextResponse.json(task)
}

export async function PUT(request: NextRequest, context: { params: { id: string } }) {
    const taskId = parseTaskId(context.params.id)
    let body: Partial<Task> = {}

    try {
        body = (await request.json()) as Partial<Task>
    } catch (error) {
        return NextResponse.json({ error: 'Invalid JSON payload' }, { status: 400 })
    }

    if (isSupabaseEnabled) {
        return updateSupabaseTask(taskId, body)
    }

    return updateMockTaskResponse(taskId, body)
}

export async function PATCH(request: NextRequest, context: { params: { id: string } }) {
    return PUT(request, context)
}

export async function DELETE(_request: NextRequest, context: { params: { id: string } }) {
    const taskId = parseTaskId(context.params.id)

    if (isSupabaseEnabled) {
        return notImplementedResponse
    }

    const removed = deleteMockTask(taskId)
    if (!removed) {
        return taskNotFoundResponse
    }

    return NextResponse.json({ success: true })
}
