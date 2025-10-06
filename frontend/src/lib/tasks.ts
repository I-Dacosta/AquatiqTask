import getPool from "src/lib/db";
import type { Task, TaskStatus } from "src/types/task";

export async function getTasksByStatus(status: TaskStatus): Promise<Task[]> {
    const pool = getPool();
    const result = await pool.query<Task>(
        `SELECT * FROM tasks WHERE status = $1 ORDER BY COALESCE(override_priority, priority_score) DESC, due_at NULLS LAST`,
        [status]
    );
    return result.rows;
}

export interface UpdateTaskPayload {
    status?: TaskStatus;
    override_priority?: number | null;
    override_locked?: boolean;
}

export async function updateTask(id: string, payload: UpdateTaskPayload): Promise<Task | null> {
    const pool = getPool();
    const fields: string[] = [];
    const values: unknown[] = [];

    if (payload.status) {
        fields.push(`status = $${fields.length + 1}`);
        values.push(payload.status);
    }
    if (payload.override_priority !== undefined) {
        fields.push(`override_priority = $${fields.length + 1}`);
        values.push(payload.override_priority);
    }
    if (payload.override_locked !== undefined) {
        fields.push(`override_locked = $${fields.length + 1}`);
        values.push(payload.override_locked);
    }
    if (!fields.length) {
        return null;
    }

    fields.push(`updated_at = NOW()`);

    const result = await pool.query<Task>(
        `UPDATE tasks SET ${fields.join(", ")} WHERE id = $${values.length + 1} RETURNING *`,
        [...values, id]
    );

    return result.rows[0] ?? null;
}
