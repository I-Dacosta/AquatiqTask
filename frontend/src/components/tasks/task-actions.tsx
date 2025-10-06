'use client'

import { useState, type ComponentType, type MouseEvent, type SVGProps } from 'react'
import { motion } from 'motion/react'
import { cn } from '@/lib/utils'
import { useTaskStore } from '@/hooks/useTaskStore'
import type { Task, TaskPriority, TaskStatus } from '@/types/task'
import {
  AlertCircle,
  ArrowDown,
  ArrowUp,
  CheckCircle,
  Clock,
  Edit,
  Eye,
  Inbox,
  Minus,
  MoreHorizontal,
  Play,
  Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

const STATUS_ACTIONS: Array<{
  status: TaskStatus
  label: string
  icon: ComponentType<SVGProps<SVGSVGElement>>
  tone: string
  description: string
}> = [
  {
    status: 'inbox',
    label: 'Move to Inbox',
    icon: Inbox,
    tone: 'hover:bg-slate-100 text-slate-600 dark:text-slate-200 dark:hover:bg-slate-700/60',
    description: 'Send task back to triage.',
  },
  {
    status: 'todo',
    label: 'Mark as To Do',
    icon: Clock,
    tone: 'hover:bg-blue-100/70 text-blue-600 dark:text-blue-300 dark:hover:bg-blue-900/30',
    description: 'Add task to actionable queue.',
  },
  {
    status: 'in_progress',
    label: 'Start Working',
    icon: Play,
    tone: 'hover:bg-amber-100/70 text-amber-600 dark:text-amber-300 dark:hover:bg-amber-900/30',
    description: 'Mark task as in progress.',
  },
  {
    status: 'done',
    label: 'Mark Complete',
    icon: CheckCircle,
    tone: 'hover:bg-emerald-100/70 text-emerald-600 dark:text-emerald-300 dark:hover:bg-emerald-900/30',
    description: 'Complete this task.',
  },
]

const PRIORITY_ACTIONS: Array<{
  priority: TaskPriority
  label: string
  icon: ComponentType<SVGProps<SVGSVGElement>>
  tone: string
}> = [
  {
    priority: 'low',
    label: 'Low Priority',
    icon: ArrowDown,
    tone: 'hover:bg-emerald-100/60 text-emerald-600 dark:text-emerald-300 dark:hover:bg-emerald-900/30',
  },
  {
    priority: 'medium',
    label: 'Medium Priority',
    icon: Minus,
    tone: 'hover:bg-sky-100/60 text-sky-600 dark:text-sky-300 dark:hover:bg-sky-900/30',
  },
  {
    priority: 'high',
    label: 'High Priority',
    icon: ArrowUp,
    tone: 'hover:bg-orange-100/60 text-orange-600 dark:text-orange-300 dark:hover:bg-orange-900/30',
  },
  {
    priority: 'urgent',
    label: 'Urgent',
    icon: AlertCircle,
    tone: 'hover:bg-rose-100/60 text-rose-600 dark:text-rose-300 dark:hover:bg-rose-900/30',
  },
]

const alignStatus = (status: TaskStatus) => (status === 'in-progress' ? 'in_progress' : status)

type TaskActionsProps = {
  task: Task
  className?: string
  onViewDetails?: (task: Task) => void
  onEdit?: (task: Task) => void
}

export function TaskActions({ task, className, onViewDetails, onEdit }: TaskActionsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const { updateTask, deleteTask } = useTaskStore()

  const handleStatusChange = async (status: TaskStatus) => {
    setIsProcessing(true)
    try {
      await updateTask(task.id, { status })
    } finally {
      setIsProcessing(false)
      setIsOpen(false)
    }
  }

  const handlePriorityChange = async (priority: TaskPriority) => {
    setIsProcessing(true)
    try {
      await updateTask(task.id, { priority })
    } finally {
      setIsProcessing(false)
      setIsOpen(false)
    }
  }

  const handleDelete = async () => {
    setIsProcessing(true)
    try {
      await deleteTask(task.id)
    } finally {
      setIsProcessing(false)
      setIsOpen(false)
    }
  }

  const handleViewDetails = () => {
    onViewDetails?.(task)
    setIsOpen(false)
  }

  const handleEdit = () => {
    onEdit?.(task)
    setIsOpen(false)
  }

  return (
    <TooltipProvider>
      <Popover open={isOpen} onOpenChange={(open: boolean) => !isProcessing && setIsOpen(open)}>
        <Tooltip>
          <TooltipTrigger asChild>
            <PopoverTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'h-8 w-8 p-0 transition-opacity hover:bg-muted',
                  isOpen && 'bg-muted opacity-100',
                  className
                )}
                onClick={(event: MouseEvent<HTMLButtonElement>) => event.stopPropagation()}
                disabled={isProcessing}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
          </TooltipTrigger>
          <TooltipContent>
            <p>Task actions</p>
          </TooltipContent>
        </Tooltip>

        <PopoverContent
          className="w-64 p-0"
          align="end"
          onClick={(event: MouseEvent<HTMLDivElement>) => event.stopPropagation()}
        >
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.12 }}>
            <section className="space-y-1 p-2">
              <h3 className="px-2 text-xs font-semibold text-muted-foreground">Change status</h3>
              {STATUS_ACTIONS.filter((action) => action.status !== task.status && alignStatus(task.status) !== alignStatus(action.status)).map((action) => {
                const Icon = action.icon
                const isDisabled = isProcessing
                return (
                  <Tooltip key={action.status}>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        disabled={isDisabled}
                        onClick={() => handleStatusChange(action.status)}
                        className={cn(
                          'flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50',
                          action.tone
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0" />
                        <span className="flex-1">{action.label}</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{action.description}</p>
                    </TooltipContent>
                  </Tooltip>
                )
              })}
            </section>

            <div className="mx-2 h-px bg-border" />

            <section className="space-y-1 p-2">
              <h3 className="px-2 text-xs font-semibold text-muted-foreground">Change priority</h3>
              {PRIORITY_ACTIONS.filter((action) => action.priority !== task.priority).map((action) => {
                const Icon = action.icon
                return (
                  <button
                    key={action.priority}
                    type="button"
                    disabled={isProcessing}
                    onClick={() => handlePriorityChange(action.priority)}
                    className={cn(
                      'flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50',
                      action.tone
                    )}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    <span className="flex-1">{action.label}</span>
                  </button>
                )
              })}
            </section>

            <div className="mx-2 h-px bg-border" />

            <section className="space-y-1 p-2">
              <h3 className="px-2 text-xs font-semibold text-muted-foreground">More actions</h3>
              <button
                type="button"
                onClick={handleViewDetails}
                className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-muted"
              >
                <Eye className="h-4 w-4 shrink-0" />
                <span className="flex-1">View details</span>
              </button>
              <button
                type="button"
                onClick={handleEdit}
                className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-muted"
              >
                <Edit className="h-4 w-4 shrink-0" />
                <span className="flex-1">Edit task</span>
              </button>
            </section>

            <div className="mx-2 h-px bg-border" />

            <section className="p-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    disabled={isProcessing}
                    onClick={handleDelete}
                    className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-destructive transition-colors hover:bg-destructive/10 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4 shrink-0" />
                    <span className="flex-1">Delete task</span>
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Permanently delete this task</p>
                </TooltipContent>
              </Tooltip>
            </section>
          </motion.div>
        </PopoverContent>
      </Popover>
    </TooltipProvider>
  )
}
