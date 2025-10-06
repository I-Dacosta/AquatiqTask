import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || ''

// Only create client if env vars are available (allow build to succeed without them)
export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null

// Database interface matching our PostgreSQL schema
export interface Task {
  id: number
  title: string
  description: string
  source: 'outlook' | 'teams' | 'manual' | 'planner'
  source_ref?: string
  requester: string
  role_hint?: string
  due_at?: string
  est_minutes?: number
  value_score: number
  risk_score: number
  role_score: number
  haste_score: number
  ai_score: number
  ai_reason: string
  override_priority?: number
  override_locked: boolean
  status: 'inbox' | 'todo' | 'approved' | 'in_progress' | 'done'
  created_at: string
  updated_at: string
}

export interface TaskFilters {
  status?: Task['status']
  source?: Task['source']
  priority_min?: number
  priority_max?: number
  search?: string
}

// Task operations
export const taskOperations = {
  // Get all tasks with optional filtering
  async getTasks(filters: TaskFilters = {}): Promise<Task[]> {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    let query = supabase
      .from('tasks')
      .select('*')
      .order('priority_score', { ascending: false })

    if (filters.status) {
      query = query.eq('status', filters.status)
    }
    
    if (filters.source) {
      query = query.eq('source', filters.source)
    }
    
    if (filters.priority_min !== undefined) {
      query = query.gte('priority_score', filters.priority_min)
    }
    
    if (filters.priority_max !== undefined) {
      query = query.lte('priority_score', filters.priority_max)
    }
    
    if (filters.search) {
      query = query.or(`title.ilike.%${filters.search}%,description.ilike.%${filters.search}%`)
    }

    const { data, error } = await query

    if (error) {
      console.error('Error fetching tasks:', error)
      throw error
    }

    return data || []
  },

  // Get single task by ID
  async getTask(id: number): Promise<Task | null> {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    const { data, error } = await supabase
      .from('tasks')
      .select('*')
      .eq('id', id)
      .single()

    if (error) {
      console.error('Error fetching task:', error)
      return null
    }

    return data
  },

  // Update task status
  async updateTaskStatus(id: number, status: Task['status']): Promise<Task | null> {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    const { data, error} = await supabase
      .from('tasks')
      .update({ 
        status,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      console.error('Error updating task status:', error)
      throw error
    }

    return data
  },

  // Update task priority override
  async updateTaskPriority(id: number, priority: number, locked: boolean = false): Promise<Task | null> {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    const { data, error } = await supabase
      .from('tasks')
      .update({ 
        override_priority: priority,
        override_locked: locked,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      console.error('Error updating task priority:', error)
      throw error
    }

    return data
  },

  // Create manual task (for webhook endpoint)
  async createTask(taskData: Partial<Task>): Promise<Task | null> {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    const { data, error } = await supabase
      .from('tasks')
      .insert({
        title: taskData.title || 'Untitled Task',
        description: taskData.description || '',
        source: taskData.source || 'manual',
        requester: taskData.requester || 'API',
        role_hint: taskData.role_hint || '',
        due_at: taskData.due_at,
        est_minutes: taskData.est_minutes,
        priority_score: (taskData as any).priority_score || 5.0,
        urgency_level: (taskData as any).urgency_level || 'MEDIUM',
        reasoning: (taskData as any).reasoning || 'Manual task creation',
        status: 'incoming'
      })
      .select()
      .single()

    if (error) {
      console.error('Error creating task:', error)
      throw error
    }

    return data
  },

  // Get task statistics
  async getTaskStats() {
    if (!supabase) throw new Error('Supabase client not initialized')
    
    const { data, error } = await supabase
      .from('tasks')
      .select('status, priority_score, source')

    if (error) {
      console.error('Error fetching task stats:', error)
      throw error
    }

    const stats = {
      total: data?.length || 0,
      incoming: data?.filter(t => t.status === 'incoming').length || 0,
      todo: data?.filter(t => t.status === 'todo').length || 0,
      approved: data?.filter(t => t.status === 'approved').length || 0,
      in_progress: data?.filter(t => t.status === 'in_progress').length || 0,
      done: data?.filter(t => t.status === 'done').length || 0,
      high_priority: data?.filter(t => (t.priority_score || 0) >= 8.0).length || 0,
      by_source: {
        outlook: data?.filter(t => t.source === 'outlook').length || 0,
        teams: data?.filter(t => t.source === 'teams').length || 0,
        manual: data?.filter(t => t.source === 'manual').length || 0,
      }
    }

    return stats
  }
}