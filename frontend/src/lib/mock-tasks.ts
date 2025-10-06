import type { Task, TaskStatus } from '@/types/task'

type GlobalWithMockTasks = typeof globalThis & {
  __mockTasks__?: Task[]
}

const globalWithMock = globalThis as GlobalWithMockTasks

const createMockDate = (daysFromNow: number) =>
  new Date(Date.now() + daysFromNow * 24 * 60 * 60 * 1000).toISOString()

const seedTasks: Task[] = [
  {
    id: 'mock-task-1',
    title: 'Draft sprint kickoff agenda',
    description: 'Outline objectives, owners, and timeline for the next sprint kickoff meeting.',
    status: 'inbox',
    source: 'manual',
    requester: 'Product Team',
    ai_score: 72,
    value_score: 80,
    risk_score: 15,
    role_score: 60,
    haste_score: 40,
    created_at: createMockDate(-2),
    due_at: createMockDate(2),
  },
  {
    id: 'mock-task-2',
    title: 'Refine onboarding checklist',
    description: 'Update the onboarding SOP with the latest security and compliance steps.',
    status: 'todo',
    source: 'manual',
    requester: 'People Ops',
    ai_score: 65,
    value_score: 75,
    risk_score: 20,
    role_score: 55,
    haste_score: 35,
    created_at: createMockDate(-5),
    due_at: createMockDate(5),
  },
  {
    id: 'mock-task-3',
    title: 'Security review sign-off',
    description: 'Collect approvals from security stakeholders ahead of the release.',
    status: 'approved',
    source: 'manual',
    requester: 'Engineering',
    ai_score: 78,
    value_score: 82,
    risk_score: 25,
    role_score: 70,
    haste_score: 50,
    created_at: createMockDate(-3),
    due_at: createMockDate(1),
  },
  {
    id: 'mock-task-4',
    title: 'Implement analytics instrumentation',
    description: 'Add event tracking for the new dashboard widgets and validate in staging.',
    status: 'in_progress',
    source: 'manual',
    requester: 'Analytics',
    ai_score: 84,
    value_score: 90,
    risk_score: 30,
    role_score: 75,
    haste_score: 60,
    created_at: createMockDate(-1),
    due_at: createMockDate(3),
  },
  {
    id: 'mock-task-5',
    title: 'Publish September release notes',
    description: 'Finalize highlights and share with customers via the changelog.',
    status: 'done',
    source: 'manual',
    requester: 'Marketing',
    ai_score: 58,
    value_score: 62,
    risk_score: 10,
    role_score: 45,
    haste_score: 20,
    created_at: createMockDate(-10),
    due_at: createMockDate(-1),
  },
]

const ensureStore = (): Task[] => {
  if (!globalWithMock.__mockTasks__) {
    globalWithMock.__mockTasks__ = seedTasks.map((task) => ({ ...task }))
  }
  return globalWithMock.__mockTasks__
}

export const getMockTasks = (): Task[] => ensureStore().map((task) => ({ ...task }))

export const createMockTask = (data: Partial<Task>): Task => {
  const tasks = ensureStore()
  const now = new Date().toISOString()
  const status = (data.status ?? 'inbox') as TaskStatus
  const newTask: Task = {
    id: data.id ?? `mock-task-${Date.now()}`,
    title: data.title ?? 'Untitled Task',
    description: data.description ?? '',
    status,
    priority: data.priority,
    ai_score: data.ai_score ?? data.aiScore ?? Math.round(Math.random() * 40 + 50),
    value_score: data.value_score ?? undefined,
    risk_score: data.risk_score ?? undefined,
    role_score: data.role_score ?? undefined,
    haste_score: data.haste_score ?? undefined,
    requester: data.requester ?? 'Internal',
    source: data.source ?? 'manual',
    created_at: data.created_at ?? now,
    updated_at: now,
    due_at: data.due_at ?? undefined,
    est_minutes: data.est_minutes,
  }

  tasks.push(newTask)
  return { ...newTask }
}

export const updateMockTask = (
  id: Task['id'],
  updates: Partial<Task>
): Task | null => {
  const tasks = ensureStore()
  const index = tasks.findIndex((task) => String(task.id) === String(id))
  if (index === -1) {
    return null
  }

  const current = tasks[index]
  const updated: Task = {
    ...current,
    ...updates,
    status: (updates.status ?? current.status) as TaskStatus,
    updated_at: new Date().toISOString(),
  }

  tasks[index] = updated
  return { ...updated }
}

export const deleteMockTask = (id: Task['id']): boolean => {
  const tasks = ensureStore()
  const index = tasks.findIndex((task) => String(task.id) === String(id))
  if (index === -1) {
    return false
  }

  tasks.splice(index, 1)
  return true
}

export const resetMockTasks = () => {
  globalWithMock.__mockTasks__ = seedTasks.map((task) => ({ ...task }))
}

export const getMockTasksSeed = (): Task[] => seedTasks.map((task) => ({ ...task }))
