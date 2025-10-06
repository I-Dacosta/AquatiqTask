import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit'
import { getMockTasks } from '@/lib/mock-tasks'
import type { Task, TaskStatus } from '@/types/task'

interface TasksState {
  tasks: Task[]
  loading: boolean
  error: string | null
  selectedTask: Task | null
  filters: {
    status: TaskStatus | 'all'
    search: string
  }
}

const initialState: TasksState = {
  tasks: getMockTasks(),
  loading: false,
  error: null,
  selectedTask: null,
  filters: {
    status: 'all',
    search: '',
  },
}

// Async thunks for API calls
export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/tasks')
      if (!response.ok) {
        throw new Error('Failed to fetch tasks')
      }
      return await response.json()
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

export const createTask = createAsyncThunk(
  'tasks/createTask',
  async (taskData: Partial<Task>, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      })
      if (!response.ok) {
        throw new Error('Failed to create task')
      }
      return await response.json()
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

export const updateTask = createAsyncThunk(
  'tasks/updateTask',
  async (payload: { id: string } & Partial<Task>, { rejectWithValue }) => {
    const { id, ...taskData } = payload
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      })
      if (!response.ok) {
        throw new Error('Failed to update task')
      }
      return await response.json()
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

export const deleteTask = createAsyncThunk(
  'tasks/deleteTask',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Failed to delete task')
      }
      return id
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    setSelectedTask: (state, action: PayloadAction<Task | null>) => {
      state.selectedTask = action.payload
    },
    setStatusFilter: (state, action: PayloadAction<TaskStatus | 'all'>) => {
      state.filters.status = action.payload
    },
    setSearchFilter: (state, action: PayloadAction<string>) => {
      state.filters.search = action.payload
    },
    setTaskStatus: (state, action: PayloadAction<{ id: Task['id']; status: TaskStatus }>) => {
      const targetId = String(action.payload.id)
      const taskIndex = state.tasks.findIndex((task) => String(task.id) === targetId)
      if (taskIndex !== -1) {
        state.tasks[taskIndex].status = action.payload.status
      }
      if (state.selectedTask && String(state.selectedTask.id) === targetId) {
        state.selectedTask = {
          ...state.selectedTask,
          status: action.payload.status,
        }
      }
    },
    clearError: (state) => {
      state.error = null
    },
    clearFilters: (state) => {
      state.filters = {
        status: 'all',
        search: '',
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchTasks.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.loading = false
        state.tasks = action.payload
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Create task
      .addCase(createTask.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.loading = false
        state.tasks.push(action.payload)
      })
      .addCase(createTask.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Update task
      .addCase(updateTask.pending, (state) => {
        state.error = null
      })
      .addCase(updateTask.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tasks.findIndex((task) => String(task.id) === String(action.payload.id))
        if (index !== -1) {
          state.tasks[index] = action.payload
        }
        if (state.selectedTask?.id === action.payload.id) {
          state.selectedTask = action.payload
        }
      })
      .addCase(updateTask.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // Delete task
      .addCase(deleteTask.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteTask.fulfilled, (state, action) => {
        state.loading = false
        state.tasks = state.tasks.filter((task) => String(task.id) !== String(action.payload))
        if (state.selectedTask && String(state.selectedTask.id) === String(action.payload)) {
          state.selectedTask = null
        }
      })
      .addCase(deleteTask.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  },
})

export const {
  setSelectedTask,
  setStatusFilter,
  setSearchFilter,
  setTaskStatus,
  clearError,
  clearFilters,
} = tasksSlice.actions

export default tasksSlice.reducer