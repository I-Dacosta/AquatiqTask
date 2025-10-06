'use client'

import { motion } from 'motion/react'
import { useMemo } from 'react'
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Task } from '@/types/task'
import {
  Activity,
  Calendar,
  Clock,
  History,
  Sparkles,
  Tag,
  Target,
  User,
  X,
} from 'lucide-react'
import { TaskActions } from './task-actions'
import { StatusBadge } from '@/components/StatusBadge'

interface TaskModalProps {
  task: Task
  open: boolean
  onClose: () => void
  onEdit?: (task: Task) => void
}

const getPriorityTone = (priority?: Task['priority']) => {
  switch (priority) {
    case 'urgent':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-200'
    case 'high':
      return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-200'
    case 'medium':
      return 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-200'
    case 'low':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-200'
    default:
      return 'bg-muted text-muted-foreground'
  }
}

const toDate = (value?: string | Date | null) => {
  if (!value) return undefined
  if (value instanceof Date) return value
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? undefined : parsed
}

const formatDate = (value?: string | Date | null) => {
  const date = toDate(value)
  if (!date) return 'Not set'
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const formatRelative = (value?: string | Date | null) => {
  const date = toDate(value)
  if (!date) return ''
  const diff = Date.now() - date.getTime()
  const day = 1000 * 60 * 60 * 24
  const days = Math.floor(diff / day)
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  if (days < 30) return `${Math.ceil(days / 7)} weeks ago`
  return `${Math.ceil(days / 30)} months ago`
}

export function TaskModal({ task, open, onClose, onEdit }: TaskModalProps) {
  const aiScore = useMemo(() => task.ai_score ?? task.aiScore ?? 0, [task.aiScore, task.ai_score])
  const aiExplanation = task.aiExplanation ?? task.ai_reason
  const createdAt = task.created_at ?? task.createdAt
  const updatedAt = task.updated_at ?? task.updatedAt
  const dueDate = task.due_at ?? task.dueDate
  const tags = task.tags ?? []

  const aiTone = aiScore >= 80
    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-200'
    : aiScore >= 60
      ? 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-200'
      : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-200'

  const handleEdit = () => {
    onEdit?.(task)
  }

  return (
    <Dialog open={open} onOpenChange={(nextOpen) => !nextOpen && onClose()}>
      <DialogContent className="max-w-3xl overflow-hidden p-0">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0.95, scale: 0.98 }}
          transition={{ duration: 0.15 }}
          className="flex h-full flex-col"
        >
          <DialogHeader className="border-b border-border p-6 pb-4">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div className="min-w-0 flex-1 space-y-3">
                <DialogTitle className="truncate text-xl font-semibold text-foreground">
                  {task.title}
                </DialogTitle>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={(task.status ?? 'inbox') as Task['status']} />
                  <Badge className={cn('capitalize', getPriorityTone(task.priority))}>
                    Priority: {task.priority ?? 'not set'}
                  </Badge>
                  <Badge className={cn('flex items-center gap-1', aiTone)}>
                    <Sparkles className="h-3.5 w-3.5" />
                    AI score: {aiScore}
                  </Badge>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end">
                <TaskActions task={task} onEdit={handleEdit} />
                <DialogClose asChild>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={onClose}>
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                  </Button>
                </DialogClose>
              </div>
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-8">
              <section className="space-y-2">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <User className="h-4 w-4" />
                  Description
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {task.description || 'No description provided.'}
                </p>
              </section>

              {aiExplanation && (
                <section className="space-y-3">
                  <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Target className="h-4 w-4 text-primary" />
                    AI insights
                  </h3>
                  <div className="rounded-lg border border-primary/30 bg-primary/5 p-4 text-sm text-muted-foreground">
                    {aiExplanation}
                  </div>
                </section>
              )}

              {tags.length > 0 && (
                <section className="space-y-3">
                  <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Tag className="h-4 w-4" />
                    Tags
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag, index) => (
                      <motion.span
                        key={`${tag}-${index}`}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.04 }}
                        className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground"
                      >
                        {tag}
                      </motion.span>
                    ))}
                  </div>
                </section>
              )}

              <section className="space-y-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <Clock className="h-4 w-4" />
                  Timeline
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 rounded-lg bg-muted/50 p-3">
                    <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Created</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(createdAt)} • {formatRelative(createdAt)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 rounded-lg bg-muted/50 p-3">
                    <div className="mt-1 h-2 w-2 rounded-full bg-emerald-500" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Updated</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(updatedAt)} • {formatRelative(updatedAt)}
                      </p>
                    </div>
                  </div>
                  {dueDate && (
                    <div className="flex items-start gap-3 rounded-lg bg-muted/50 p-3">
                      <div className="mt-1 h-2 w-2 rounded-full bg-orange-500" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">Due</p>
                        <p className="text-xs text-muted-foreground">{formatDate(dueDate)}</p>
                      </div>
                      <Calendar className="h-4 w-4 text-orange-500" />
                    </div>
                  )}
                </div>
              </section>

              {Array.isArray(task.log) && task.log.length > 0 && (
                <section className="space-y-3">
                  <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <History className="h-4 w-4" />
                    Activity
                  </h3>
                  <div className="space-y-2">
                    {task.log
                      .slice()
                      .reverse()
                      .map((entry, index) => (
                        <motion.div
                          key={entry.id ?? `${entry.action}-${index}`}
                          initial={{ opacity: 0, x: -8 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-start gap-3 rounded-lg border border-border/60 bg-background/80 p-3"
                        >
                          <Activity className="mt-0.5 h-4 w-4 text-primary" />
                          <div className="space-y-1 text-xs text-muted-foreground">
                            <p className="font-medium text-foreground">{entry.action}</p>
                            {entry.details && <p>{entry.details}</p>}
                            {entry.timestamp && <p className="text-[10px] uppercase">{formatDate(entry.timestamp)}</p>}
                          </div>
                        </motion.div>
                      ))}
                  </div>
                </section>
              )}
            </div>
          </div>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
