'use client'

import * as React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useAppSelector, useAppDispatch } from '@/lib/store'
import { 
  setSelectedTask,
  setStatusFilter,
  setSearchFilter,
  fetchTasks,
  updateTask,
  deleteTask
} from '@/lib/features/tasks/tasksSlice'
import type { Task, TaskStatus } from '@/types/task'
import type { LucideIcon } from 'lucide-react'
import {
  MoreHorizontal,
  Search,
  Filter,
  ArrowUpDown,
  Calendar,
  Clock,
  User,
  AlertCircle,
  CheckCircle,
  Play,
  Inbox,
  ListTodo,
} from 'lucide-react'
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'

type StatusDisplay = {
  label: string
  variant: 'secondary' | 'default' | 'destructive' | 'outline'
  icon: LucideIcon
  color: string
}

const statusConfig: Record<TaskStatus, StatusDisplay> = {
  inbox: {
    label: 'Inbox',
    variant: 'secondary',
    icon: Inbox,
    color: 'bg-gray-100 text-gray-800',
  },
  todo: {
    label: 'To Do',
    variant: 'default',
    icon: ListTodo,
    color: 'bg-blue-100 text-blue-800',
  },
  'in-progress': {
    label: 'In Progress',
    variant: 'destructive',
    icon: Play,
    color: 'bg-yellow-100 text-yellow-800',
  },
  done: {
    label: 'Done',
    variant: 'outline',
    icon: CheckCircle,
    color: 'bg-green-100 text-green-800',
  },
  approved: {
    label: 'Approved',
    variant: 'default',
    icon: CheckCircle,
    color: 'bg-blue-100 text-blue-800',
  },
  in_progress: {
    label: 'In Progress',
    variant: 'destructive',
    icon: Play,
    color: 'bg-yellow-100 text-yellow-800',
  },
}

export function ModernTaskTable() {
  const dispatch = useAppDispatch()
  const { tasks, loading, filters, selectedTask } = useAppSelector((state) => state.tasks)
  const [sortField, setSortField] = React.useState<keyof Task>('created_at')
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('desc')

  // Keyboard shortcuts for task management
  useKeyboardShortcuts([
    {
      key: 'j',
      action: () => selectNextTask(),
      description: 'Select next task',
    },
    {
      key: 'k', 
      action: () => selectPrevTask(),
      description: 'Select previous task',
    },
    {
      key: 'Enter',
      action: () => selectedTask && openTaskDetails(selectedTask),
      description: 'Open selected task',
    },
    {
      key: 'd',
      action: () => selectedTask && handleDeleteTask(selectedTask.id),
      description: 'Delete selected task',
    },
  ])

  React.useEffect(() => {
    dispatch(fetchTasks())
  }, [dispatch])

  const filteredAndSortedTasks = React.useMemo(() => {
    let filtered = tasks.filter((task) => {
      const matchesStatus = filters.status === 'all' || task.status === filters.status
  const searchTerm = filters.search.toLowerCase()
  const matchesSearch = task.title.toLowerCase().includes(searchTerm) ||
           task.description?.toLowerCase().includes(searchTerm) ||
           task.source?.toLowerCase().includes(searchTerm)
      return matchesStatus && matchesSearch
    })

    return filtered.sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]
      
      if (aValue === null || aValue === undefined) return 1
      if (bValue === null || bValue === undefined) return -1
      
      const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0
      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [tasks, filters, sortField, sortDirection])

  const handleSort = (field: keyof Task) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const handleStatusChange = (taskId: Task['id'], newStatus: TaskStatus) => {
    dispatch(updateTask({ id: String(taskId), status: newStatus }))
  }

  const handleDeleteTask = (taskId: Task['id']) => {
    if (confirm('Are you sure you want to delete this task?')) {
      dispatch(deleteTask(String(taskId)))
    }
  }

  const selectNextTask = () => {
    if (!filteredAndSortedTasks.length) return
    const currentIndex = filteredAndSortedTasks.findIndex(t => t.id === selectedTask?.id)
    const nextIndex = currentIndex < filteredAndSortedTasks.length - 1 ? currentIndex + 1 : 0
    dispatch(setSelectedTask(filteredAndSortedTasks[nextIndex]))
  }

  const selectPrevTask = () => {
    if (!filteredAndSortedTasks.length) return
    const currentIndex = filteredAndSortedTasks.findIndex(t => t.id === selectedTask?.id)
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : filteredAndSortedTasks.length - 1
    dispatch(setSelectedTask(filteredAndSortedTasks[prevIndex]))
  }

  const openTaskDetails = (task: Task) => {
    console.log('Opening task details:', task.id)
    // Implement task details modal or navigation
  }

  const getPriorityScore = (task: Task) => {
    if (typeof task.ai_score === 'number') return task.ai_score
    const value = task.value_score ?? 0
    const role = task.role_score ?? 0
    const haste = task.haste_score ?? 0
    const risk = task.risk_score ?? 0
    return value + role + haste - risk
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '—'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              className="pl-8 w-[300px]"
              value={filters.search}
              onChange={(e) => dispatch(setSearchFilter(e.target.value))}
            />
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="mr-2 h-4 w-4" />
                {filters.status === 'all' ? 'All Status' : statusConfig[filters.status].label}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => dispatch(setStatusFilter('all'))}>
                All Status
              </DropdownMenuItem>
              {Object.entries(statusConfig).map(([status, config]) => (
                <DropdownMenuItem
                  key={status}
                  onClick={() => dispatch(setStatusFilter(status as TaskStatus))}
                >
                  <config.icon className="mr-2 h-4 w-4" />
                  {config.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        <div className="text-sm text-muted-foreground">
          Showing {filteredAndSortedTasks.length} of {tasks.length} tasks
        </div>
      </div>

      {/* Task Table */}
      <Card>
        <CardHeader>
          <CardTitle>Tasks</CardTitle>
          <CardDescription>
            Manage and prioritize your tasks with AI-powered scoring
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('ai_score')}
                    className="h-8 p-0 font-semibold"
                  >
                    Score
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('title')}
                    className="h-8 p-0 font-semibold"
                  >
                    Task
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('due_at')}
                    className="h-8 p-0 font-semibold"
                  >
                    Due Date
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('created_at')}
                    className="h-8 p-0 font-semibold"
                  >
                    Created
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedTasks.map((task) => {
                const StatusIcon = statusConfig[task.status].icon
                const isSelected = selectedTask?.id === task.id
                
                return (
                  <TableRow 
                    key={task.id}
                    className={`cursor-pointer hover:bg-muted/50 ${
                      isSelected ? 'bg-muted' : ''
                    }`}
                    onClick={() => dispatch(setSelectedTask(task))}
                  >
                    <TableCell>
                      <div className="flex items-center">
                        <div className={`text-sm font-medium px-2 py-1 rounded ${
                          getPriorityScore(task) >= 80 ? 'bg-red-100 text-red-800' :
                          getPriorityScore(task) >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {getPriorityScore(task)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="font-medium">{task.title}</div>
                        {task.description && (
                          <div className="text-sm text-muted-foreground line-clamp-1">
                            {task.description}
                          </div>
                        )}
                        {task.est_minutes && (
                          <div className="flex items-center text-xs text-muted-foreground">
                            <Clock className="mr-1 h-3 w-3" />
                            {task.est_minutes}m
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8">
                            <StatusIcon className="mr-2 h-4 w-4" />
                            {statusConfig[task.status].label}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          {Object.entries(statusConfig).map(([status, config]) => (
                            <DropdownMenuItem 
                              key={status}
                              onClick={(e) => {
                                e.stopPropagation()
                                handleStatusChange(task.id, status as TaskStatus)
                              }}
                            >
                              <config.icon className="mr-2 h-4 w-4" />
                              {config.label}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{task.source}</Badge>
                        {task.requester && (
                          <div className="flex items-center text-sm text-muted-foreground">
                            <User className="mr-1 h-3 w-3" />
                            {task.requester}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {task.due_at ? (
                        <div className="flex items-center text-sm">
                          <Calendar className="mr-1 h-3 w-3 text-muted-foreground" />
                          {formatDate(task.due_at)}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">No due date</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-muted-foreground">
                        {formatDate(task.created_at)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openTaskDetails(task)}>
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => console.log('Edit task:', task.id)}>
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteTask(task.id)
                            }}
                            className="text-destructive"
                          >
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
          
          {filteredAndSortedTasks.length === 0 && (
            <div className="text-center py-12">
              <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground" />
              <div className="mt-4">
                <h3 className="text-lg font-semibold">No tasks found</h3>
                <p className="text-muted-foreground">
                  {filters.search || filters.status !== 'all' 
                    ? 'Try adjusting your search or filters' 
                    : 'Create your first task to get started'}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}