/**
 * Tasks Page Component - Task Management Dashboard
 * 
 * Features:
 * 1. Modern task table with keyboard shortcuts
 * 2. Command palette integration 
 * 3. Responsive design with shadcn/ui components
 * 4. Real-time task management with Redux
 */

'use client'

import { useMemo, useState } from 'react'
import { TaskCanvasBoard } from '@/components/task-canvas'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Plus, Download, Filter } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/lib/store'
import { useGlobalKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'
import { clearFilters, setStatusFilter } from '@/lib/features/tasks/tasksSlice'
import type { Task, TaskStatus } from '@/types/task'
import { STATUS_LABELS } from '@/types/task'
import { TaskModal } from '@/components/tasks/task-modal'
import { TaskForm } from '@/components/tasks/task-form'
import { useTaskStore } from '@/hooks/useTaskStore'

const statusOptions: (TaskStatus | 'all')[] = [
  'all',
  'inbox',
  'todo',
  'approved',
  'in_progress',
  'in-progress',
  'done',
]

export default function TasksPage() {
  const dispatch = useAppDispatch()
  const { filters } = useAppSelector((state) => state.tasks)
  const { selectedTask, selectTask } = useTaskStore()
  const [formState, setFormState] = useState<{
    open: boolean
    mode: 'create' | 'edit'
    task: Task | null
  }>({ open: false, mode: 'create', task: null })
  
  // Enable global keyboard shortcuts
  useGlobalKeyboardShortcuts()

  const activeStatusLabel = useMemo(() => {
    if (filters.status === 'all') {
      return 'All Status'
    }
    return STATUS_LABELS[filters.status] ?? filters.status.replace('_', ' ')
  }, [filters.status])

  const handleStatusSelect = (status: TaskStatus | 'all') => {
    if (status === 'all') {
      dispatch(clearFilters())
      return
    }
    dispatch(setStatusFilter(status))
  }

  const openCreateTask = () => {
    setFormState({ open: true, mode: 'create', task: null })
  }

  const openEditTask = (task: Task) => {
    setFormState({ open: true, mode: 'edit', task })
    selectTask(null)
  }

  const closeForm = () => {
    setFormState((state) => ({ ...state, open: false }))
  }

  const closeModal = () => selectTask(null)

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Tasks</h2>
          <p className="text-muted-foreground">
            AI-powered task prioritization and management dashboard
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button size="sm" variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm" variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                {activeStatusLabel}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              {statusOptions.map((statusOption) => (
                <DropdownMenuItem
                  key={statusOption}
                  onClick={() => handleStatusSelect(statusOption === 'all' ? 'all' : statusOption)}
                  className="capitalize"
                >
                  {statusOption === 'all'
                    ? 'All Status'
                    : STATUS_LABELS[statusOption as TaskStatus] ?? statusOption.replace('_', ' ')}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <Button size="sm" onClick={openCreateTask}>
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Button>
        </div>
      </div>

      <TaskCanvasBoard onTaskEdit={openEditTask} />

      {selectedTask && (
        <TaskModal task={selectedTask} open={Boolean(selectedTask)} onClose={closeModal} onEdit={openEditTask} />
      )}

      <TaskForm open={formState.open} onClose={closeForm} mode={formState.mode} task={formState.task} />

      {/* Keyboard Shortcuts Hint */}
      <div className="flex justify-center">
        <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-2 rounded-md">
          <kbd className="px-1.5 py-0.5 bg-background rounded border">⌘K</kbd> to open command palette •{' '}
          <kbd className="px-1.5 py-0.5 bg-background rounded border">J</kbd>/<kbd className="px-1.5 py-0.5 bg-background rounded border">K</kbd> to navigate •{' '}
          <kbd className="px-1.5 py-0.5 bg-background rounded border">Enter</kbd> to select
        </div>
      </div>
    </div>
  )
}
