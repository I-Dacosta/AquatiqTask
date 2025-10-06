'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import {
  Calendar,
  Home,
  Search,
  Settings,
  User,
  Plus,
  FileText,
  BarChart3,
  Archive,
  Trash2,
  ListTodo,
} from 'lucide-react'
import { useAppSelector, useAppDispatch } from '@/lib/store'
import { setStatusFilter, setSearchFilter } from '@/lib/features/tasks/tasksSlice'
import type { Task } from '@/types/task'

type CommandMenuOpenEventDetail = {
  query?: string
}

export function CommandMenu() {
  const [open, setOpen] = React.useState(false)
  const [commandQuery, setCommandQuery] = React.useState('')
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { tasks, filters } = useAppSelector((state) => state.tasks)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  React.useEffect(() => {
    const handleOpen = (event: Event) => {
      const detail = (event as CustomEvent<CommandMenuOpenEventDetail>).detail
      if (typeof detail?.query === 'string') {
        setCommandQuery(detail.query)
        dispatch(setSearchFilter(detail.query))
      }
      setOpen(true)
    }

    window.addEventListener('command-menu:open', handleOpen as EventListener)
    return () => window.removeEventListener('command-menu:open', handleOpen as EventListener)
  }, [dispatch])

  React.useEffect(() => {
    if (open) {
      setCommandQuery(filters.search)
    }
  }, [open, filters.search])

  const runCommand = React.useCallback((command: () => void) => {
    setOpen(false)
    command()
  }, [])

  const navigateToPage = (path: string) => {
    runCommand(() => router.push(path as any))
  }

  const filterTasks = (status: 'inbox' | 'todo' | 'approved' | 'in_progress' | 'done' | 'all') => {
    runCommand(() => dispatch(setStatusFilter(status)))
  }

  const clearSearch = () => {
    setCommandQuery('')
    dispatch(setSearchFilter(''))
  }

  return (
    <CommandDialog
      open={open}
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen)
        if (!nextOpen) {
          setCommandQuery('')
        }
      }}
    >
      <CommandInput
        placeholder="Type a command or search..."
        value={commandQuery}
        onValueChange={(value) => {
          setCommandQuery(value)
          dispatch(setSearchFilter(value))
        }}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => navigateToPage('/')}>
            <Home className="mr-2 h-4 w-4" />
            Home
          </CommandItem>
          <CommandItem onSelect={() => navigateToPage('/dashboard')}>
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard
          </CommandItem>
          <CommandItem onSelect={() => navigateToPage('/login')}>
            <User className="mr-2 h-4 w-4" />
            Login
          </CommandItem>
        </CommandGroup>
        
        <CommandSeparator />
        
        <CommandGroup heading="Tasks">
          <CommandItem onSelect={() => filterTasks('all')}>
            <FileText className="mr-2 h-4 w-4" />
            All Tasks ({tasks.length})
          </CommandItem>
          <CommandItem onSelect={() => filterTasks('inbox')}>
            <Calendar className="mr-2 h-4 w-4" />
            Inbox ({tasks.filter((t: Task) => t.status === 'inbox').length})
          </CommandItem>
          <CommandItem onSelect={() => filterTasks('todo')}>
            <ListTodo className="mr-2 h-4 w-4" />
            To Do ({tasks.filter((t: Task) => t.status === 'todo').length})
          </CommandItem>
          <CommandItem onSelect={() => filterTasks('approved')}>
            <Plus className="mr-2 h-4 w-4" />
            Approved Tasks ({tasks.filter((t: Task) => t.status === 'approved').length})
          </CommandItem>
          <CommandItem onSelect={() => filterTasks('in_progress')}>
            <Settings className="mr-2 h-4 w-4" />
            In Progress ({tasks.filter((t: Task) => t.status === 'in_progress').length})
          </CommandItem>
          <CommandItem onSelect={() => filterTasks('done')}>
            <Archive className="mr-2 h-4 w-4" />
            Completed ({tasks.filter((t: Task) => t.status === 'done').length})
          </CommandItem>
        </CommandGroup>
        
        <CommandSeparator />
        
        <CommandGroup heading="Actions">
          <CommandItem onSelect={clearSearch}>
            <Search className="mr-2 h-4 w-4" />
            Clear Search
          </CommandItem>
          <CommandItem onSelect={() => console.log('New task')}>
            <Plus className="mr-2 h-4 w-4" />
            Create New Task
          </CommandItem>
          <CommandItem onSelect={() => console.log('Export data')}>
            <FileText className="mr-2 h-4 w-4" />
            Export Data
          </CommandItem>
        </CommandGroup>

        {tasks.length > 0 && (
          <>
            <CommandSeparator />
            <CommandGroup heading="Recent Tasks">
              {tasks.slice(0, 5).map((task: Task) => (
                <CommandItem
                  key={task.id}
                  onSelect={() => console.log('Selected task:', task.id)}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  <span className="truncate">{task.title}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  )
}