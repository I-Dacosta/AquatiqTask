"use client";

import type { TaskStatus } from "@/types/task";
import clsx from "clsx";

const STATUS_LABEL: Record<TaskStatus, string> = {
    approved: "Approved",
    in_progress: "In Progress",
    done: "Done",
    inbox: "Inbox",
    todo: "To Do",
    "in-progress": "In Progress"
};

export function StatusBadge({ status }: { status: TaskStatus }) {
    return (
        <span className={clsx("status-badge")} data-status={status}>
            {STATUS_LABEL[status]}
        </span>
    );
}
