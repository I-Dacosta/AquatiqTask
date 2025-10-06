// PostgreSQL Task Operations for PrioritiAI
// Connects directly to PostgreSQL database on VPS
import { Pool } from 'pg'
import type { Task, TaskStatus } from '@/types/task'

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

export interface TaskFilters {
  status?: TaskStatus
  source?: 'outlook' | 'teams' | 'manual'
  priority_min?: number
  priority_max?: number
  search?: string
  urgency_level?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
}

export const taskOperations = {
  /**
   * Get all tasks with optional filtering
   */
  async getTasks(filters: TaskFilters = {}): Promise<Task[]> {
    const conditions: string[] = []
    const values: any[] = []
    let paramIndex = 1

    if (filters.status) {
      conditions.push(`status = $${paramIndex++}`)
      values.push(filters.status)
    }

    if (filters.source) {
      conditions.push(`source = $${paramIndex++}`)
      values.push(filters.source)
    }

    if (filters.urgency_level) {
      conditions.push(`urgency_level = $${paramIndex++}`)
      values.push(filters.urgency_level)
    }

    if (filters.priority_min !== undefined) {
      conditions.push(`priority_score >= $${paramIndex++}`)
      values.push(filters.priority_min)
    }

    if (filters.priority_max !== undefined) {
      conditions.push(`priority_score <= $${paramIndex++}`)
      values.push(filters.priority_max)
    }

    if (filters.search) {
      conditions.push(`(title ILIKE $${paramIndex} OR description ILIKE $${paramIndex})`)
      values.push(`%${filters.search}%`)
      paramIndex++
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : ''
    const orderBy = 'ORDER BY COALESCE(override_priority, priority_score) DESC, created_at DESC'

    const query = `
      SELECT 
        id,
        title,
        description,
        source,
        source_ref,
        requester,
        role_hint,
        due_at,
        est_minutes,
        priority_score,
        urgency_level,
        reasoning,
        override_priority,
        override_locked,
        status,
        created_at,
        updated_at
      FROM tasks
      ${whereClause}
      ${orderBy}
    `

    const result = await pool.query(query, values)
    return result.rows.map(mapDatabaseToTask)
  },

  /**
   * Get single task by ID
   */
  async getTask(id: number): Promise<Task | null> {
    const result = await pool.query(
      `SELECT * FROM tasks WHERE id = $1`,
      [id]
    )
    return result.rows[0] ? mapDatabaseToTask(result.rows[0]) : null
  },

  /**
   * Update task status
   */
  async updateTaskStatus(id: number, status: TaskStatus): Promise<Task | null> {
    const result = await pool.query(
      `UPDATE tasks 
       SET status = $1, updated_at = NOW() 
       WHERE id = $2 
       RETURNING *`,
      [status, id]
    )
    return result.rows[0] ? mapDatabaseToTask(result.rows[0]) : null
  },

  /**
   * Update task priority (manual override)
   */
  async updateTaskPriority(
    id: number,
    overridePriority: number,
    overrideLocked: boolean
  ): Promise<Task | null> {
    const result = await pool.query(
      `UPDATE tasks 
       SET override_priority = $1, override_locked = $2, updated_at = NOW() 
       WHERE id = $3 
       RETURNING *`,
      [overridePriority, overrideLocked, id]
    )
    return result.rows[0] ? mapDatabaseToTask(result.rows[0]) : null
  },

  /**
   * Delete task
   */
  async deleteTask(id: number): Promise<boolean> {
    const result = await pool.query(
      `DELETE FROM tasks WHERE id = $1`,
      [id]
    )
    return (result.rowCount ?? 0) > 0
  },

  /**
   * Get task statistics
   */
  async getTaskStats(): Promise<{
    total: number
    byStatus: Record<string, number>
    byUrgency: Record<string, number>
    avgPriority: number
  }> {
    const totalResult = await pool.query('SELECT COUNT(*) as count FROM tasks')
    const total = parseInt(totalResult.rows[0].count)

    const statusResult = await pool.query(`
      SELECT status, COUNT(*) as count 
      FROM tasks 
      GROUP BY status
    `)
    const byStatus: Record<string, number> = {}
    statusResult.rows.forEach(row => {
      byStatus[row.status] = parseInt(row.count)
    })

    const urgencyResult = await pool.query(`
      SELECT urgency_level, COUNT(*) as count 
      FROM tasks 
      WHERE urgency_level IS NOT NULL
      GROUP BY urgency_level
    `)
    const byUrgency: Record<string, number> = {}
    urgencyResult.rows.forEach(row => {
      byUrgency[row.urgency_level] = parseInt(row.count)
    })

    const avgResult = await pool.query(`
      SELECT AVG(priority_score) as avg 
      FROM tasks 
      WHERE priority_score IS NOT NULL
    `)
    const avgPriority = parseFloat(avgResult.rows[0].avg) || 0

    return { total, byStatus, byUrgency, avgPriority }
  },
}

/**
 * Map database row to Task interface
 */
function mapDatabaseToTask(row: any): Task {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    source: row.source,
    source_ref: row.source_ref,
    requester: row.requester,
    role_hint: row.role_hint,
    due_at: row.due_at,
    dueDate: row.due_at ? new Date(row.due_at) : undefined,
    est_minutes: row.est_minutes,
    ai_score: row.priority_score ? Math.round(row.priority_score * 10) : undefined, // Scale 0-10 to 0-100 for UI
    aiScore: row.priority_score ? Math.round(row.priority_score * 10) : undefined,
    ai_reason: row.reasoning,
    aiExplanation: row.reasoning,
    override_priority: row.override_priority,
    override_locked: row.override_locked ?? false,
    status: normalizeStatus(row.status),
    created_at: row.created_at,
    createdAt: row.created_at ? new Date(row.created_at) : undefined,
    updated_at: row.updated_at,
    updatedAt: row.updated_at ? new Date(row.updated_at) : undefined,
    // Additional fields for UI compatibility
    priority: mapUrgencyToPriority(row.urgency_level),
    tags: row.source ? [row.source] : [],
  }
}

/**
 * Normalize status from database
 */
function normalizeStatus(status: string): TaskStatus {
  // Map database status to frontend status
  if (status === 'incoming') return 'inbox'
  if (status === 'in_progress') return 'in-progress'
  return status as TaskStatus
}

/**
 * Map urgency level to priority for UI
 */
function mapUrgencyToPriority(urgencyLevel: string | null): 'low' | 'medium' | 'high' | 'urgent' {
  switch (urgencyLevel) {
    case 'CRITICAL':
      return 'urgent'
    case 'HIGH':
      return 'high'
    case 'MEDIUM':
      return 'medium'
    case 'LOW':
    default:
      return 'low'
  }
}

export default taskOperations
