import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/lib/store'
import {
  createTask as createTaskThunk,
  deleteTask as deleteTaskThunk,
  setSelectedTask,
  updateTask as updateTaskThunk,
} from '@/lib/features/tasks/tasksSlice'
import type { Task, TaskPriority, TaskStatus } from '@/types/task'

const normalizeStatus = (status?: TaskStatus | null): TaskStatus | undefined => {
  if (!status) return undefined
  if (status === 'in-progress') return 'in_progress'
  return status
}

const mapTaskInput = (input: Partial<Task>) => {
  const normalized: Partial<Task> = {
    ...input,
  }

  if (input.status) {
    normalized.status = normalizeStatus(input.status)
  }

  if (input.aiScore !== undefined && input.ai_score === undefined) {
    normalized.ai_score = input.aiScore
  }

  if (input.ai_reason && !input.aiExplanation) {
    normalized.aiExplanation = input.ai_reason
  }

  if (input.aiExplanation && !input.ai_reason) {
    normalized.ai_reason = input.aiExplanation
  }

  if (input.createdAt instanceof Date) {
    normalized.created_at = input.createdAt.toISOString()
  }

  if (input.updatedAt instanceof Date) {
    normalized.updated_at = input.updatedAt.toISOString()
  }

  if (input.dueDate instanceof Date) {
    normalized.due_at = input.dueDate.toISOString()
  }

  if (typeof input.dueDate === 'string' && !input.due_at) {
    normalized.due_at = input.dueDate
  }

  return normalized
}

export const useTaskStore = () => {
  const dispatch = useAppDispatch()
  const { tasks, selectedTask, loading, error } = useAppSelector((state) => state.tasks)

  const addTask = useCallback(
    async (data: Partial<Task>) => {
      const payload = mapTaskInput(data)
      return dispatch(createTaskThunk(payload)).unwrap()
    },
    [dispatch]
  )

  const updateTask = useCallback(
    async (id: Task['id'], data: Partial<Task>) => {
      const payload = mapTaskInput(data)
      // Ensure payload doesn't include id
      const { id: _, ...payloadWithoutId } = payload as any
      return dispatch(
        updateTaskThunk({
          id: `${id}`,
          ...payloadWithoutId,
        })
      ).unwrap()
    },
    [dispatch]
  )

  const deleteTask = useCallback(
    async (id: Task['id']) => {
      return dispatch(deleteTaskThunk(`${id}`)).unwrap()
    },
    [dispatch]
  )

  const selectTask = useCallback(
    (task: Task | null) => {
      dispatch(setSelectedTask(task))
    },
    [dispatch]
  )

  return {
    tasks,
    selectedTask,
    loading,
    error,
    addTask,
    updateTask,
    deleteTask,
    selectTask,
  }
}
