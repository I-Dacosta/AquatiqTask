// Task System Types

export type TaskStatus =
  | 'inbox'
  | 'todo'
  | 'in-progress'
  | 'done'
  | 'approved'
  | 'in_progress';

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface TaskLogEntry {
  id: string;
  action: string;
  timestamp: Date;
  details: string;
}

export interface Task {
  id: string | number;
  title: string;
  description: string;
  status: TaskStatus;
  priority?: TaskPriority;
  aiScore?: number; // 0-100
  ai_score?: number;
  aiExplanation?: string;
  ai_reason?: string;
  tags?: string[];
  createdAt?: Date;
  created_at?: string;
  updatedAt?: Date;
  updated_at?: string;
  dueDate?: Date;
  due_at?: string;
  source?: string;
  source_ref?: string;
  requester?: string;
  role_hint?: string;
  est_minutes?: number;
  value_score?: number;
  risk_score?: number;
  role_score?: number;
  haste_score?: number;
  override_priority?: number | null;
  override_locked?: boolean;
  log?: TaskLogEntry[];
  assignedTo?: string;
  assigned_to?: string;
  estimatedHours?: number;
  actualHours?: number;
  dependencies?: string[]; // Array of task IDs
  attachments?: TaskAttachment[];
  comments?: TaskComment[];
}

export interface TaskAttachment {
  id: string;
  name: string;
  url: string;
  type: string; // MIME type
  size: number; // bytes
  uploadedAt: Date;
  uploadedBy: string;
}

export interface TaskComment {
  id: string;
  content: string;
  author: string;
  createdAt: Date;
  updatedAt?: Date;
  mentions?: string[]; // Array of user IDs mentioned
  attachments?: TaskAttachment[];
}

export interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  pendingTasks: number;
  progressPercentage: number;
}

export interface TaskFilter {
  status?: TaskStatus[];
  priority?: TaskPriority[];
  tags?: string[];
  assignedTo?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  search?: string;
}

export interface TaskSort {
  field: 'createdAt' | 'updatedAt' | 'dueDate' | 'priority' | 'aiScore' | 'title';
  direction: 'asc' | 'desc';
}

export interface TaskStats {
  total: number;
  byStatus: Record<TaskStatus, number>;
  byPriority: Record<TaskPriority, number>;
  averageAiScore: number;
  completionRate: number;
  overdueTasks: number;
}

// UI Component Props Types
export interface TaskCardProps {
  task: Task;
  onClick?: (task: Task) => void;
  onStatusChange?: (taskId: string, newStatus: TaskStatus) => void;
  onPriorityChange?: (taskId: string, newPriority: TaskPriority) => void;
  onDelete?: (taskId: string) => void;
  className?: string;
  showActions?: boolean;
  compact?: boolean;
}

export interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  error?: string | null;
  onTaskSelect?: (task: Task) => void;
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
  onTaskDelete?: (taskId: string) => void;
  filter?: TaskFilter;
  sort?: TaskSort;
  className?: string;
  emptyMessage?: string;
  enableDragDrop?: boolean;
}

export interface TaskTabsProps {
  tasksByStatus: {
    inbox: Task[];
    todo: Task[];
    progress: Task[];
    done: Task[];
  };
  onTaskSelect: (task: Task) => void;
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
  className?: string;
}

export interface TaskModalProps {
  task: Task | null;
  open?: boolean;
  onClose: () => void;
  onSave?: (taskId: string, updates: Partial<Task>) => void;
  onDelete?: (taskId: string) => void;
  mode?: 'view' | 'edit';
}

export interface TaskActionsProps {
  task: Task;
  onStatusChange?: (newStatus: TaskStatus) => void;
  onPriorityChange?: (newPriority: TaskPriority) => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onView?: () => void;
  disabled?: boolean;
  className?: string;
}

// API Types
export interface CreateTaskRequest {
  title: string;
  description: string;
  priority?: TaskPriority;
  tags?: string[];
  dueDate?: Date;
  assignedTo?: string;
  estimatedHours?: number;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  dueDate?: Date;
  assignedTo?: string;
  estimatedHours?: number;
  actualHours?: number;
}

export interface TaskSearchRequest {
  query?: string;
  filter?: TaskFilter;
  sort?: TaskSort;
  page?: number;
  limit?: number;
}

export interface TaskSearchResponse {
  tasks: Task[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// Utility Types and Constants
export type TaskStatusGroup = 'inbox' | 'todo' | 'progress' | 'done';

export interface TaskStatusMapping {
  [key: string]: TaskStatusGroup;
}

export const TASK_STATUS_GROUPS: TaskStatusMapping = {
  'inbox': 'inbox',
  'todo': 'todo',
  'in-progress': 'progress',
  'done': 'done',
  'approved': 'todo',
  'in_progress': 'progress',
};

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  'low': 'Low Priority',
  'medium': 'Medium Priority',
  'high': 'High Priority',
  'urgent': 'Urgent',
};

export const PRIORITY_COLORS: Record<TaskPriority, string> = {
  'low': 'bg-green-100 text-green-700 border-green-300',
  'medium': 'bg-yellow-100 text-yellow-700 border-yellow-300',
  'high': 'bg-orange-100 text-orange-700 border-orange-300',
  'urgent': 'bg-red-100 text-red-700 border-red-300 animate-pulse',
};

export const STATUS_LABELS: Record<TaskStatus, string> = {
  'inbox': 'Inbox',
  'todo': 'To Do',
  'in-progress': 'In Progress',
  'done': 'Done',
  'approved': 'Approved',
  'in_progress': 'In Progress',
};

export const STATUS_COLORS: Record<TaskStatus, string> = {
  'inbox': 'bg-white text-gray-800 border-gray-200',
  'todo': 'bg-blue-500 text-white border-blue-600',
  'in-progress': 'bg-yellow-500 text-gray-800 border-yellow-600',
  'done': 'bg-green-500 text-white border-green-600',
  'approved': 'bg-blue-500 text-white border-blue-600',
  'in_progress': 'bg-yellow-500 text-gray-800 border-yellow-600',
};

export const PRIORITY_ORDER: Record<TaskPriority, number> = {
  'urgent': 4,
  'high': 3,
  'medium': 2,
  'low': 1,
};

// Helper functions for task management
export const getPriorityWeight = (priority: TaskPriority): number => {
  return PRIORITY_ORDER[priority];
};

export const getStatusGroup = (status: TaskStatus): TaskStatusGroup => {
  return TASK_STATUS_GROUPS[status] as TaskStatusGroup;
};

export const isTaskOverdue = (task: Task): boolean => {
  const dueValue = task.dueDate ?? task.due_at;
  if (!dueValue) return false;
  const dueDate = new Date(dueValue);
  return dueDate < new Date() && task.status !== 'done';
};

export const getTaskAgeInDays = (task: Task): number => {
  const now = new Date();
  const createdValue = task.createdAt ?? task.created_at;
  if (!createdValue) return 0;
  const created = new Date(createdValue);
  const diffTime = Math.abs(now.getTime() - created.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const getDaysUntilDue = (task: Task): number | null => {
  const dueValue = task.dueDate ?? task.due_at;
  if (!dueValue) return null;
  const now = new Date();
  const due = new Date(dueValue);
  const diffTime = due.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const getTaskCompletionTime = (task: Task): number | null => {
  if (task.status !== 'done') return null;
  const createdValue = task.createdAt ?? task.created_at;
  const completedValue = task.updatedAt ?? task.updated_at;
  if (!createdValue || !completedValue) return null;
  const created = new Date(createdValue);
  const completed = new Date(completedValue);
  const diffTime = completed.getTime() - created.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};