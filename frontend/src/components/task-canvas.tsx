"use client"

import { useCallback, useEffect, useMemo } from "react"
import { DndProvider, useDrag, useDrop } from "react-dnd"
import type { DragSourceMonitor, DropTargetMonitor } from "react-dnd"
import { HTML5Backend } from "react-dnd-html5-backend"
import { useAppDispatch, useAppSelector } from "@/lib/store"
import { fetchTasks, setTaskStatus } from "@/lib/features/tasks/tasksSlice"
import type { Task, TaskStatus } from "@/types/task"
import { cn } from "@/lib/utils"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Calendar,
  Clock,
  ListTodo,
  Inbox,
  Play,
  CheckCircle2,
  Archive,
  Sparkles,
  ShieldCheck,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { TaskActions } from "@/components/tasks/task-actions"
import { useTaskStore } from "@/hooks/useTaskStore"

const DRAGGABLE_TASK_TYPE = "task-card"

interface DragItem {
  id: string
  status: TaskStatus
}

interface BoardColumn {
  key: string
  label: string
  helper?: string
  statuses: TaskStatus[]
  dropStatus: TaskStatus
  tone: string
  icon: LucideIcon
}

const BOARD_COLUMNS: BoardColumn[] = [
  {
    key: "inbox",
    label: "Inbox",
    helper: "Unsorted work",
    statuses: ["inbox"],
    dropStatus: "inbox",
    tone: "from-slate-100 to-white border-slate-200",
    icon: Inbox,
  },
  {
    key: "todo",
    label: "To Do",
    helper: "Planned next",
    statuses: ["todo"],
    dropStatus: "todo",
    tone: "from-blue-100/70 to-white border-blue-200",
    icon: ListTodo,
  },
  {
    key: "approved",
    label: "Approved",
    helper: "Ready to start",
    statuses: ["approved"],
    dropStatus: "approved",
    tone: "from-sky-100/70 to-white border-sky-200",
    icon: ShieldCheck,
  },
  {
    key: "progress",
    label: "In Progress",
    helper: "Currently active",
    statuses: ["in_progress", "in-progress"],
    dropStatus: "in_progress",
    tone: "from-amber-100/70 to-white border-amber-200",
    icon: Play,
  },
  {
    key: "done",
    label: "Completed",
    helper: "Finished work",
    statuses: ["done"],
    dropStatus: "done",
    tone: "from-emerald-100/70 to-white border-emerald-200",
    icon: CheckCircle2,
  },
]

const columnStatusLookup = BOARD_COLUMNS.reduce<Record<TaskStatus, string>>((acc, column) => {
  column.statuses.forEach((status) => {
    acc[status] = column.key
  })
  return acc
}, {} as Record<TaskStatus, string>)

const getTaskPriorityBadge = (task: Task) => {
  if (!task.priority && typeof task.ai_score !== "number") {
    return {
      label: "",
      className: "",
    }
  }

  if (task.priority) {
    const priorityMap: Record<string, { label: string; className: string }> = {
      low: { label: "Low", className: "bg-emerald-100 text-emerald-700" },
      medium: { label: "Medium", className: "bg-amber-100 text-amber-700" },
      high: { label: "High", className: "bg-orange-100 text-orange-700" },
      urgent: { label: "Urgent", className: "bg-red-100 text-red-700" },
    }
    const fallback = { label: "Priority", className: "bg-slate-100 text-slate-700" }
    return priorityMap[task.priority] ?? fallback
  }

  return {
    label: `AI ${Math.round(task.ai_score ?? 0)}`,
    className: "bg-indigo-100 text-indigo-700",
  }
}

const formatDate = (dateString?: string | Date | null) => {
  if (!dateString) return null
  const date = dateString instanceof Date ? dateString : new Date(dateString)
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  })
}

function TaskCard({
  task,
  onSelect,
  onEdit,
}: {
  task: Task
  onSelect?: (task: Task) => void
  onEdit?: (task: Task) => void
}) {
  const { selectTask } = useTaskStore()
  const priority = getTaskPriorityBadge(task)
  const dueDate = formatDate(task.due_at ?? task.dueDate)

  const viewTask = useCallback(
    (nextTask: Task) => {
      if (onSelect) {
        onSelect(nextTask)
      } else {
        selectTask(nextTask)
      }
    },
    [onSelect, selectTask]
  )

  const editTask = useCallback(
    (nextTask: Task) => {
      if (onEdit) {
        onEdit(nextTask)
      } else {
        viewTask(nextTask)
      }
    },
    [onEdit, viewTask]
  )

  const [{ isDragging }, dragRef] = useDrag<DragItem, void, { isDragging: boolean }>(
    () => ({
      type: DRAGGABLE_TASK_TYPE,
      item: { id: String(task.id), status: task.status },
      collect: (monitor: DragSourceMonitor<DragItem, void>) => ({
        isDragging: monitor.isDragging(),
      }),
      end: (_item: DragItem | undefined, monitor: DragSourceMonitor<DragItem, void>) => {
        if (!monitor.didDrop()) {
          selectTask(null)
        }
      },
    }),
    [task.id, task.status, selectTask]
  )

  const setDragSourceRef = useCallback(
    (node: HTMLDivElement | null) => {
      void dragRef(node)
    },
    [dragRef]
  )

  return (
    <div
      ref={setDragSourceRef}
      role="button"
      tabIndex={0}
      onClick={() => viewTask(task)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          viewTask(task)
        }
      }}
      className={cn(
        "group cursor-grab rounded-lg border bg-background/80 p-4 shadow-sm transition hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary",
        isDragging && "opacity-60"
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-sm leading-tight text-foreground">{task.title}</p>
          {task.description && (
            <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{task.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {priority.label && (
            <Badge className={cn("text-[10px] font-medium", priority.className)}>
              {priority.label}
            </Badge>
          )}
          <TaskActions task={task} onViewDetails={viewTask} onEdit={editTask} />
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {task.source && (
          <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
            <Archive className="h-3 w-3" />
            {task.source}
          </span>
        )}
        {task.est_minutes && (
          <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
            <Clock className="h-3 w-3" />
            {task.est_minutes}m
          </span>
        )}
        {dueDate && (
          <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
            <Calendar className="h-3 w-3" />
            {dueDate}
          </span>
        )}
        {typeof task.ai_score === "number" && (
          <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
            <Sparkles className="h-3 w-3" />
            {Math.round(task.ai_score)}
          </span>
        )}
      </div>
    </div>
  )
}

function TaskColumn({
  column,
  columnTasks,
  allTasks,
  onTaskSelect,
  onTaskEdit,
}: {
  column: BoardColumn
  columnTasks: Task[]
  allTasks: Task[]
  onTaskSelect?: (task: Task) => void
  onTaskEdit?: (task: Task) => void
}) {
  const dispatch = useAppDispatch()
  const { selectTask, updateTask } = useTaskStore()
  const Icon = column.icon

  const [{ isOver, canDrop }, dropRef] = useDrop<DragItem, void, { isOver: boolean; canDrop: boolean }>(
    () => ({
      accept: DRAGGABLE_TASK_TYPE,
      collect: (monitor: DropTargetMonitor<DragItem, void>) => ({
        isOver: monitor.isOver({ shallow: true }),
        canDrop: monitor.canDrop(),
      }),
      canDrop: (item: DragItem, _monitor: DropTargetMonitor<DragItem, void>) => {
        if (!item) return false
        if (column.statuses.includes(item.status)) {
          return column.dropStatus !== item.status
        }
        return true
      },
      drop: (item: DragItem, _monitor: DropTargetMonitor<DragItem, void>) => {
        const currentTask = allTasks.find((task) => String(task.id) === item.id)
        if (!currentTask) return

        const nextStatus = column.statuses.includes(currentTask.status)
          ? currentTask.status
          : column.dropStatus

        if (currentTask.status === nextStatus) {
          return
        }

        const previousStatus = currentTask.status

        dispatch(setTaskStatus({ id: currentTask.id, status: nextStatus }))
        selectTask(null)
        item.status = nextStatus

        void updateTask(currentTask.id, { status: nextStatus })
          .catch(() => {
            dispatch(setTaskStatus({ id: currentTask.id, status: previousStatus }))
            item.status = previousStatus
          })
      },
    }),
    [allTasks, column.statuses, column.dropStatus]
  )

  const isHighlighted = canDrop && isOver

  const setDropTargetRef = useCallback(
    (node: HTMLDivElement | null) => {
      void dropRef(node)
    },
    [dropRef]
  )

  return (
    <div className="flex-1 min-w-[280px]" ref={setDropTargetRef}>
      <Card
        className={cn(
          "flex h-full min-h-[calc(100vh-260px)] flex-col border bg-gradient-to-b transition",
          column.tone,
          isHighlighted && "border-primary shadow-[0_0_0_3px_rgba(59,130,246,0.3)]"
        )}
      >
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-base font-semibold">
                <Icon className="h-4 w-4 text-muted-foreground" />
                {column.label}
              </CardTitle>
              {column.helper && <CardDescription>{column.helper}</CardDescription>}
            </div>
            <Badge variant="secondary" className="rounded-full px-2 py-1 text-xs">
              {columnTasks.length}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pr-1">
          <div className="flex flex-col gap-3">
            {columnTasks.length === 0 && (
              <div className="rounded-lg border border-dashed border-muted-foreground/30 bg-background/40 p-6 text-center text-xs text-muted-foreground">
                Drop tasks here
              </div>
            )}
            {columnTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onSelect={onTaskSelect}
                onEdit={onTaskEdit}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export function TaskCanvasBoard({
  onTaskSelect,
  onTaskEdit,
}: {
  onTaskSelect?: (task: Task) => void
  onTaskEdit?: (task: Task) => void
}) {
  const dispatch = useAppDispatch()
  const { tasks, loading, selectTask } = useTaskStore()
  const { filters } = useAppSelector((state) => state.tasks)

  const handleTaskSelect = useCallback(
    (task: Task) => {
      if (onTaskSelect) {
        onTaskSelect(task)
      } else {
        selectTask(task)
      }
    },
    [onTaskSelect, selectTask]
  )

  const handleTaskEdit = useCallback(
    (task: Task) => {
      if (onTaskEdit) {
        onTaskEdit(task)
      } else {
        handleTaskSelect(task)
      }
    },
    [handleTaskSelect, onTaskEdit]
  )

  useEffect(() => {
    dispatch(fetchTasks())
  }, [dispatch])

  const groupedTasks = useMemo(() => {
    const searchTerm = filters.search.trim().toLowerCase()
    const searchFilterActive = searchTerm.length > 0

    const buckets: Record<string, Task[]> = {}
    BOARD_COLUMNS.forEach((column) => {
      buckets[column.key] = []
    })

    const matchesSearch = (task: Task) => {
      if (!searchFilterActive) return true
      return (
        task.title.toLowerCase().includes(searchTerm) ||
        (task.description?.toLowerCase().includes(searchTerm) ?? false) ||
        (task.source?.toLowerCase().includes(searchTerm) ?? false)
      )
    }

    tasks.filter(matchesSearch).forEach((task) => {
      const columnKey = columnStatusLookup[task.status]
      if (columnKey && buckets[columnKey]) {
        buckets[columnKey].push(task)
      } else {
        if (!buckets.inbox) buckets.inbox = []
        buckets.inbox.push(task)
      }
    })

    if (filters.status !== "all") {
      const focusColumn = columnStatusLookup[filters.status] ?? filters.status
      return Object.entries(buckets).reduce<Record<string, Task[]>>((acc, [columnKey, columnTasks]) => {
        if (columnKey === focusColumn) {
          acc[columnKey] = columnTasks
        } else {
          acc[columnKey] = []
        }
        return acc
      }, {})
    }

    return buckets
  }, [tasks, filters.status, filters.search])

  if (loading) {
    return (
      <div className="flex h-[480px] items-center justify-center rounded-xl border border-dashed">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="w-full overflow-x-auto">
        <div className="flex w-full gap-4 pb-6 pr-2 min-h-[calc(100vh-220px)]">
          {BOARD_COLUMNS.map((column) => (
            <TaskColumn
              key={column.key}
              column={column}
              columnTasks={groupedTasks[column.key] ?? []}
              allTasks={tasks}
              onTaskSelect={handleTaskSelect}
              onTaskEdit={handleTaskEdit}
            />
          ))}
        </div>
      </div>
    </DndProvider>
  )
}
