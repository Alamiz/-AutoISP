export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

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
  credentials: {
    password: string;
    number?: string;
    recovery_email?: string;
  };
  label: string;
  last_sync: string;
  status: "active" | "inactive" | "error" | "disabled";
  latest_automation: string;
  provider: "gmx" | "webde";
  type: "desktop" | "mobile";
  proxy_settings: {
    host: string;
    port: number;
    username: string;
    password: string;
    protocol: "http" | "https";
  };
  activities: HistoryEntry[];
  backups: Backup[];
  created_at: string;
  updated_at: string;
}


export interface AutomationParam {
  name: string;
  label: string;
  type: "text" | "number" | "boolean" | "textarea";
  placeholder?: string;
  required?: boolean;
  defaultValue?: string | number | boolean;
}

export interface Automation {
  id: string
  name: string
  description: string
  category: "email" | "inbox" | "attachments" | "maintenance" | "browsing" | "Test" | "Auth" | "Email" | "Maintenance" | "Browsing" // Added capitalized versions to match data
  estimatedDuration: string
  provider?: "gmx" | "webde" | "all"
  params?: AutomationParam[]
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
