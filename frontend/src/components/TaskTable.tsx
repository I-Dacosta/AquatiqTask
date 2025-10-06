"use client";

import { useState } from "react";
import type { Task, TaskStatus } from "@/types/task";
import { StatusBadge } from "@/components/StatusBadge";

interface TaskTableProps {
    tasks: Task[];
    status: TaskStatus;
    onStatusChange: (taskId: string, status: TaskStatus) => Promise<void> | void;
    onOverrideChange: (taskId: string, overridePriority: number | null, overrideLocked: boolean) => Promise<void> | void;
}

const ACTIONS_BY_STATUS: Record<TaskStatus, { label: string; next: TaskStatus }[]> = {
    approved: [{ label: "Start", next: "in_progress" }],
    in_progress: [{ label: "Fullfør", next: "done" }],
    done: [],
    inbox: [
        { label: "Godkjenn", next: "approved" },
        { label: "Start", next: "in_progress" }
    ],
    todo: [{ label: "Start", next: "in_progress" }],
    "in-progress": [{ label: "Fullfør", next: "done" }]
};

export function TaskTable({ tasks, status, onStatusChange, onOverrideChange }: TaskTableProps) {
    const [localOverrides, setLocalOverrides] = useState<Record<string, { value: string; locked: boolean }>>({});
    const [pending, setPending] = useState<string | null>(null);

    const handleAction = async (taskId: string, nextStatus: TaskStatus) => {
        try {
            setPending(taskId);
            await onStatusChange(taskId, nextStatus);
        } finally {
            setPending(null);
        }
    };

    const handleOverrideChange = async (taskId: string) => {
        const override = localOverrides[taskId];
        if (!override) return;

        const value = override.value.trim() === "" ? null : Number(override.value);
        if (value !== null && (Number.isNaN(value) || value < 0 || value > 100)) {
            alert("Prioritet må være mellom 0 og 100");
            return;
        }

        setPending(taskId);
        try {
            await onOverrideChange(taskId, value, override.locked);
        } finally {
            setPending(null);
        }
    };

    const setLocalValue = (taskId: string, partial: Partial<{ value: string; locked: boolean }>) => {
        setLocalOverrides((prev: Record<string, { value: string; locked: boolean }>) => ({
            ...prev,
            [taskId]: {
                value: partial.value ?? prev[taskId]?.value ?? "",
                locked: partial.locked ?? prev[taskId]?.locked ?? false
            }
        }));
    };

    return (
        <div className="card">
            <table className="tasks">
                <thead>
                    <tr>
                        <th>Oppgave</th>
                        <th>AI-score</th>
                        <th>Frist</th>
                        <th>Kilde</th>
                        <th>Skalert/resultat</th>
                        <th>Handlinger</th>
                    </tr>
                </thead>
                <tbody>
                    {tasks.length === 0 && (
                        <tr>
                            <td colSpan={6} style={{ textAlign: "center", padding: "32px" }}>
                                Ingen oppgaver i denne statusen ennå.
                            </td>
                        </tr>
                    )}
                    {tasks.map((task) => {
                        const taskId = String(task.id);
                        const override = localOverrides[taskId] ?? {
                            value: task.override_priority?.toString() ?? "",
                            locked: task.override_locked
                        };
                        return (
                            <tr key={taskId}>
                                <td>
                                    <strong>{task.title}</strong>
                                    <div style={{ marginTop: "6px", fontSize: "0.85rem", opacity: 0.86 }}>{task.description}</div>
                                    <div style={{ marginTop: "6px", display: "flex", gap: "8px", alignItems: "center" }}>
                                        <StatusBadge status={task.status} />
                                        <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem" }}>
                                            {task.requester ?? "Ukjent forespørger"}
                                        </span>
                                    </div>
                                </td>
                                <td>
                                    <div style={{ fontWeight: 600 }}>{task.ai_score}</div>
                                    <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Verdi: {task.value_score}</div>
                                    <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Risiko: {task.risk_score}</div>
                                    <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Rolle: {task.role_score}</div>
                                    <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Haste: {task.haste_score}</div>
                                </td>
                                <td>{task.due_at ? new Date(task.due_at).toLocaleString("nb-NO") : "—"}</td>
                                <td>{task.source}</td>
                                <td style={{ maxWidth: "240px" }}>
                                    <div style={{ fontSize: "0.8rem" }}>{task.ai_reason ?? ""}</div>
                                    <div className="priority-controls" style={{ marginTop: "10px" }}>
                                        <input
                                            type="number"
                                            placeholder="0-100"
                                            value={override.value}
                                            onChange={(event) =>
                                                setLocalValue(taskId, { value: event.currentTarget.value })
                                            }
                                            disabled={pending === taskId}
                                        />
                                        <label>
                                            <input
                                                type="checkbox"
                                                checked={override.locked}
                                                onChange={(event) =>
                                                    setLocalValue(taskId, { locked: event.currentTarget.checked })
                                                }
                                                disabled={pending === taskId}
                                            />
                                            Lås
                                        </label>
                                        <button
                                            onClick={() => handleOverrideChange(taskId)}
                                            disabled={pending === taskId}
                                        >
                                            Lagre
                                        </button>
                                    </div>
                                </td>
                                <td>
                                    <div className="actions">
                                        {(ACTIONS_BY_STATUS[status] ?? []).map((action) => (
                                            <button
                                                key={action.label}
                                                onClick={() => handleAction(taskId, action.next)}
                                                disabled={pending === taskId}
                                            >
                                                {action.label}
                                            </button>
                                        ))}
                                    </div>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
