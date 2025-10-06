import type { TaskStatus } from "src/types/task";

export const API_STATUSES = [
  "inbox",
  "todo",
  "approved",
  "in_progress",
  "done",
] as const;

export type ApiTaskStatus = (typeof API_STATUSES)[number];

const SUPABASE_TO_LOCAL_STATUS: Record<ApiTaskStatus, TaskStatus> = {
  inbox: "inbox",
  todo: "todo",
  approved: "approved",
  in_progress: "in_progress",
  done: "done",
};

export const isApiTaskStatus = (value: string): value is ApiTaskStatus => {
  return (API_STATUSES as readonly string[]).includes(value);
};

export const toLocalTaskStatus = (status: ApiTaskStatus): TaskStatus => {
  return SUPABASE_TO_LOCAL_STATUS[status];
};
