'use client'

import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { useTaskStore } from '@/hooks/useTaskStore'
import type { Task, TaskPriority, TaskStatus } from '@/types/task'
import { Calendar, FileText, Plus, Tag, Target, X } from 'lucide-react'

interface TaskFormProps {
  task?: Task | null
  open: boolean
  mode?: 'create' | 'edit'
  onClose: () => void
}

const defaultFormState = () => ({
  title: '',
  description: '',
  priority: 'medium' as TaskPriority,
  status: 'inbox' as TaskStatus,
  tags: '',
  dueDate: '',
})

const parseInitialState = (task?: Task | null) => {
  if (!task) return defaultFormState()

  const createdState = defaultFormState()
  createdState.title = task.title ?? ''
  createdState.description = task.description ?? ''
  createdState.priority = (task.priority ?? 'medium') as TaskPriority
  createdState.status = (task.status ?? 'inbox') as TaskStatus
  createdState.tags = (task.tags ?? []).join(', ')

  const dueValue = task.dueDate ?? task.due_at
  if (dueValue) {
    const date = typeof dueValue === 'string' ? dueValue : dueValue.toISOString()
    createdState.dueDate = date.slice(0, 16)
  }

  return createdState
}

export function TaskForm({ task, open, onClose, mode = 'create' }: TaskFormProps) {
  const { addTask, updateTask } = useTaskStore()
  const [formData, setFormData] = useState(parseInitialState(task))
  const [errors, setErrors] = useState<Record<string, string>>({})
  const dialogTitle = useMemo(() => (mode === 'edit' ? 'Edit task' : 'Create task'), [mode])

  useEffect(() => {
    if (open) {
      setFormData(parseInitialState(task))
      setErrors({})
    }
  }, [open, task])

  const validate = () => {
    const nextErrors: Record<string, string> = {}
    if (!formData.title.trim()) {
      nextErrors.title = 'A title is required.'
    }
    if (!formData.description.trim()) {
      nextErrors.description = 'Add a short description.'
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!validate()) return

    const tags = formData.tags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)

    const payload: Partial<Task> = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      priority: formData.priority,
      status: formData.status,
      tags,
      dueDate: formData.dueDate ? new Date(formData.dueDate) : undefined,
      aiScore: Math.floor(Math.random() * 20 + 75),
      aiExplanation:
        'Task prioritized automatically based on selected priority and content characteristics.',
    }

    if (mode === 'edit' && task) {
      await updateTask(task.id, payload)
    } else {
      await addTask(payload)
    }

    onClose()
  }

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl overflow-hidden p-0">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0.9, scale: 0.97 }}
          transition={{ duration: 0.18 }}
          className="flex h-full flex-col"
        >
          <DialogHeader className="border-b border-border p-6 pb-4">
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2 text-lg font-semibold">
                <Plus className="h-4 w-4" />
                {dialogTitle}
              </DialogTitle>
              <DialogClose asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <X className="h-4 w-4" />
                  <span className="sr-only">Close</span>
                </Button>
              </DialogClose>
            </div>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
            <div className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="task-title" className="flex items-center gap-2 text-sm font-medium">
                  <FileText className="h-4 w-4" />
                  Title
                </Label>
                <Input
                  id="task-title"
                  value={formData.title}
                  onChange={(event) => setFormData((state) => ({ ...state, title: event.target.value }))}
                  placeholder="Name your task"
                />
                {errors.title && <p className="text-xs text-destructive">{errors.title}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="task-description" className="text-sm font-medium">
                  Description
                </Label>
                <textarea
                  id="task-description"
                  value={formData.description}
                  onChange={(event) =>
                    setFormData((state) => ({ ...state, description: event.target.value }))
                  }
                  rows={4}
                  className={cn(
                    'min-h-[120px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-sm transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
                    errors.description && 'border-destructive focus:ring-destructive'
                  )}
                  placeholder="Describe what needs to be done"
                />
                {errors.description && <p className="text-xs text-destructive">{errors.description}</p>}
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="task-priority" className="flex items-center gap-2 text-sm font-medium">
                    <Target className="h-4 w-4" />
                    Priority
                  </Label>
                  <select
                    id="task-priority"
                    value={formData.priority}
                    onChange={(event) =>
                      setFormData((state) => ({ ...state, priority: event.target.value as TaskPriority }))
                    }
                    className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="task-status" className="text-sm font-medium">
                    Status
                  </Label>
                  <select
                    id="task-status"
                    value={formData.status}
                    onChange={(event) =>
                      setFormData((state) => ({ ...state, status: event.target.value as TaskStatus }))
                    }
                    className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  >
                    <option value="inbox">Inbox</option>
                    <option value="todo">To do</option>
                    <option value="in_progress">In progress</option>
                    <option value="in-progress">In progress (legacy)</option>
                    <option value="approved">Approved</option>
                    <option value="done">Done</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="task-tags" className="flex items-center gap-2 text-sm font-medium">
                    <Tag className="h-4 w-4" />
                    Tags
                  </Label>
                  <Input
                    id="task-tags"
                    value={formData.tags}
                    onChange={(event) => setFormData((state) => ({ ...state, tags: event.target.value }))}
                    placeholder="marketing, product, design"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="task-due-date" className="flex items-center gap-2 text-sm font-medium">
                    <Calendar className="h-4 w-4" />
                    Due date
                  </Label>
                  <Input
                    id="task-due-date"
                    type="datetime-local"
                    value={formData.dueDate}
                    onChange={(event) =>
                      setFormData((state) => ({ ...state, dueDate: event.target.value }))
                    }
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2 border-t border-border pt-4">
              <Button type="button" variant="ghost" onClick={() => onClose()}>
                Cancel
              </Button>
              <Button type="submit" className="bg-primary text-primary-foreground hover:bg-primary/90">
                {mode === 'edit' ? 'Update task' : 'Create task'}
              </Button>
            </div>
          </form>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
