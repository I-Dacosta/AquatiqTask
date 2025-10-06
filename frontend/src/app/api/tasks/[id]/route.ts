import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import taskOperations from '@/lib/postgres-tasks'
import type { Task, TaskStatus } from '@/types/task'

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

const parseNumericTaskId = (rawId: string) => {
    const numericId = Number(rawId)
    return Number.isNaN(numericId) ? null : numericId
}

const buildUnexpectedErrorResponse = (error: unknown) => {
    console.error('Task API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}

export async function GET(
    _request: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    const params = await props.params
    const numericId = parseNumericTaskId(params.id)
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

export async function PUT(
    request: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    const params = await props.params
    const numericId = parseNumericTaskId(params.id)
    if (numericId === null) {
        return invalidIdResponse
    }

    let body: Partial<Task> = {}
    try {
        body = (await request.json()) as Partial<Task>
    } catch (error) {
        return NextResponse.json({ error: 'Invalid JSON payload' }, { status: 400 })
    }

    try {
        // Handle status update
        if (body.status) {
            if (!validateStatus(body.status)) {
                return NextResponse.json({ error: 'Invalid status' }, { status: 400 })
            }
            const normalized = normalizeStatus(body.status) as TaskStatus | undefined
            await taskOperations.updateTaskStatus(numericId, normalized as any)
        }

        // Handle priority override update
        if (body.override_priority !== undefined || body.override_locked !== undefined) {
            const priority = body.override_priority ?? 50
            const locked = body.override_locked ?? false
            await taskOperations.updateTaskPriority(numericId, priority, locked)
        }

        // Fetch updated task
        const updated = await taskOperations.getTask(numericId)
        if (!updated) {
            return taskNotFoundResponse
        }
        return NextResponse.json(updated)
    } catch (error) {
        return buildUnexpectedErrorResponse(error)
    }
}

export async function PATCH(
    request: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    return PUT(request, props)
}

export async function DELETE(
    _request: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    const params = await props.params
    const numericId = parseNumericTaskId(params.id)
    if (numericId === null) {
        return invalidIdResponse
    }

    try {
        await taskOperations.deleteTask(numericId)
        return NextResponse.json({ success: true })
    } catch (error) {
        return buildUnexpectedErrorResponse(error)
    }
}
