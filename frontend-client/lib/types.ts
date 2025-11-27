export interface HistoryEntry {
  id: number
  action: string
  details: string
  status: "success" | "failed" | "running"
  executed_at: string
  completed_at: string
}

export interface Backup {
  id: string;
  accountId: number;
  filename?: string | null;
  file_size?: number | null;
  status: "pending" | "in_progress" | "completed" | "failed";
  created_at: string;
}

export interface Account {
  id: string;
  email: string;
  password: string;
  label: string;
  lastChecked: string;
  status: "idle" | "running" | "error" | "disabled" | "new";
  latestAutomation: string;
  activities: HistoryEntry[];
  backups: Backup[];
}


export interface Automation {
  id: string
  name: string
  description: string
  category: "email" | "inbox" | "attachments" | "maintenance" | "browsing" | "test"
  estimatedDuration: string
  parameters?: Record<string, any>
}

export interface AutomationRun {
  id: string
  accountId: string
  automationId: string
  status: "pending" | "running" | "completed" | "failed" | "cancelled"
  progress: number
  startedAt: string
  completedAt?: string
  logs: LogEntry[]
  result?: {
    success: boolean
    summary: string
    details?: Record<string, any>
  }
}

export interface LogEntry {
  id: string
  level: "DEBUG" | "INFO" | "SUCCESS" | "WARNING" | "ERROR"
  message: string
  timestamp: string
  // account_email?: string
  account_id?: string
  activity_id?: string
  account?: {
    active: boolean
    email: string
    label: string
    password: string
    proxy: string | null
    status: "idle" | "running" | "error" | "disabled" | "new";
  }
  // metadata?: Record<string, any>
}

export interface SystemStats {
  totalAccounts: number
  activeAccounts: number
  runningJobs: number
  failedJobs: number
  completedJobs: number
  lastRunTimestamp?: string
  uptime: string
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// WebSocket event types
export interface WebSocketEvent {
  type: "log" | "progress" | "status_change" | "automation_complete"
  accountId?: string
  automationRunId?: string
  data: any
  timestamp: string
}

export interface RunningJob {
  id: string
  accountId: string
  automationId: string
  accountEmail: string
  automationName: string
  status: "running" | "paused" | "completed" | "failed"
  progress: number
  startedAt: string
  completedAt?: string
  estimatedCompletion?: string
  currentStep: string
  logs: LogEntry[]
  result?: {
    success: boolean
    summary: string
    details?: Record<string, any>
  }
}
