// Re-export types from Zod schemas for backward compatibility
export type {
  LogLevel,
  LogFormat,
  AnomalySeverity,
  AnomalyType,
  LogEntry,
  Anomaly,
  AISummary,
  Statistics,
  AnalysisResult,
  TimelineData,
  FileInfo,
  FileListResponse,
  UploadResponse,
  DeleteFileResponse,
  ErrorResponse,
  SuccessResponse,
  User,
  AuthResponse,
  FileUploadRequest,
  AnalysisRequest,
  AnomalyRequest,
  TimelineRequest,
  LoginForm,
  SignUpForm,
  FileUpload,
  APIResponse,
} from '../lib/schemas'

// Legacy type definitions for backward compatibility
// These will be removed in future versions
export interface LegacyLogEntry {
  line_number: number
  timestamp?: string
  level: string
  message: string
  service?: string
  format: string
  raw_line: string
  
  // Apache/Nginx specific fields
  ip_address?: string
  method?: string
  url?: string
  status_code?: number
  response_size?: number
  
  // Syslog specific fields
  hostname?: string
  
  // Metadata
  user_id?: string
  file_id?: string
  created_at?: string
  updated_at?: string
  
  // Analysis results
  anomaly_score?: number
  anomaly_type?: string
  tags?: string[]
}

export interface LegacyAnomaly {
  type: string
  severity: string
  description: string
  timestamp?: string
  details: Record<string, any>
}

export interface LegacyAnalysisResult {
  total_entries: number
  anomalies: LegacyAnomaly[]
  ai_summary?: {
    summary: string
    insights: string[]
    recommendations: string[]
  }
  statistics: {
    error_count: number
    warning_count: number
    info_count: number
  }
}

export interface LegacyTimelineData {
  timeline: Record<string, {
    total: number
    errors: number
    warnings: number
    info: number
  }>
  total_entries: number
}

export interface LegacyUploadedFile {
  filename: string
  size: number
  uploaded_at: number
  path?: string
}

export interface LegacyFileUploadStatus {
  name: string
  size: number
  status: 'uploading' | 'success' | 'error'
  message?: string
}

export interface LegacyUser {
  id: string
  email: string
  role: string
  provider: string
}

export interface LegacyAuthResponse {
  valid: boolean
  user?: LegacyUser
  error?: string
}

export interface LegacyAPIResponse<T = any> {
  data?: T
  message?: string
  error?: string
}
