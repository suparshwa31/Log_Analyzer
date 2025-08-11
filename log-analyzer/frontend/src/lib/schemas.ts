import { z } from 'zod'

// Enums
export const LogLevelSchema = z.enum(['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL', 'FATAL'])
export const LogFormatSchema = z.enum(['apache', 'nginx', 'syslog', 'json', 'generic'])
export const AnomalySeveritySchema = z.enum(['low', 'medium', 'high'])
export const AnomalyTypeSchema = z.enum([
  'error_spike',
  'unusual_pattern', 
  'frequency_anomaly',
  'time_anomaly',
  'ip_anomaly',
  'status_anomaly'
])

// Base Schemas
export const LogEntrySchema = z.object({
  line_number: z.number(),
  timestamp: z.string().nullable().optional(),
  level: LogLevelSchema,
  message: z.string(),
  service: z.string().nullable().optional(),
  format: LogFormatSchema,
  raw_line: z.string(),
  
  // Apache/Nginx specific fields
  ip_address: z.string().nullable().optional(),
  method: z.string().nullable().optional(),
  url: z.string().nullable().optional(),
  status_code: z.number().nullable().optional(),
  response_size: z.number().nullable().optional(),
  
  // Syslog specific fields
  hostname: z.string().nullable().optional(),
  
  // Metadata
  user_id: z.string().nullable().optional(),
  file_id: z.string().nullable().optional(),
  created_at: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
  
  // Analysis results
  anomaly_score: z.number().nullable().optional(),
  anomaly_type: AnomalyTypeSchema.nullable().optional(),
  tags: z.array(z.string()).nullable().optional(),
})

export const AnomalySchema = z.object({
  type: AnomalyTypeSchema,
  severity: AnomalySeveritySchema,
  description: z.string(),
  timestamp: z.string().nullable().optional(),
  details: z.record(z.any()),
})

export const AISummarySchema = z.object({
  summary: z.string(),
  insights: z.array(z.string()),
  recommendations: z.array(z.string()),
})

export const StatisticsSchema = z.object({
  error_count: z.number(),
  warning_count: z.number(),
  info_count: z.number(),
})

export const AnalysisResultSchema = z.object({
  total_entries: z.number(),
  anomalies: z.array(AnomalySchema),
  ai_summary: AISummarySchema.nullable().optional(),
  statistics: StatisticsSchema,
  timeline: z.record(z.record(z.number())).nullable().optional(),
})

export const TimelineDataSchema = z.object({
  timeline: z.record(z.record(z.number())),
  total_entries: z.number(),
})

export const FileInfoSchema = z.object({
  filename: z.string(),
  size: z.number(),
  uploaded_at: z.number(),
  path: z.string().nullable().optional(),
})

export const FileListResponseSchema = z.object({
  files: z.array(FileInfoSchema),
})

export const UploadResponseSchema = z.object({
  message: z.string(),
  filename: z.string(),
  file_path: z.string(),
  parse_result: z.array(z.record(z.any())).nullable().optional(),
})

export const DeleteFileResponseSchema = z.object({
  message: z.string(),
})

export const ErrorResponseSchema = z.object({
  error: z.string(),
  details: z.string().nullable().optional(),
})

export const SuccessResponseSchema = z.object({
  message: z.string(),
  data: z.record(z.any()).nullable().optional(),
})

// User Schemas
export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  role: z.string(),
  provider: z.string(),
})

export const AuthResponseSchema = z.object({
  valid: z.boolean(),
  user: UserSchema.nullable().optional(),
  error: z.string().nullable().optional(),
})

// Request Schemas
export const FileUploadRequestSchema = z.object({
  file_path: z.string(),
  user_id: z.string().nullable().optional(),
})

export const AnalysisRequestSchema = z.object({
  file_path: z.string(),
})

export const AnomalyRequestSchema = z.object({
  file_path: z.string(),
})

export const TimelineRequestSchema = z.object({
  file_path: z.string(),
})

// Form Schemas
export const LoginFormSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export const SignUpFormSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

// File Upload Schema
export const FileUploadSchema = z.object({
  files: z
    .custom<FileList>((val) => val instanceof FileList && val.length > 0, {
      message: 'Please select at least one file',
    }),
})


// API Response Schemas
export const APIResponseSchema = z.object({
  data: z.any().optional(),
  message: z.string().optional(),
  error: z.string().optional(),
})

// Type exports
export type LogLevel = z.infer<typeof LogLevelSchema>
export type LogFormat = z.infer<typeof LogFormatSchema>
export type AnomalySeverity = z.infer<typeof AnomalySeveritySchema>
export type AnomalyType = z.infer<typeof AnomalyTypeSchema>
export type LogEntry = z.infer<typeof LogEntrySchema>
export type Anomaly = z.infer<typeof AnomalySchema>
export type AISummary = z.infer<typeof AISummarySchema>
export type Statistics = z.infer<typeof StatisticsSchema>
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>
export type TimelineData = z.infer<typeof TimelineDataSchema>
export type FileInfo = z.infer<typeof FileInfoSchema>
export type FileListResponse = z.infer<typeof FileListResponseSchema>
export type UploadResponse = z.infer<typeof UploadResponseSchema>
export type DeleteFileResponse = z.infer<typeof DeleteFileResponseSchema>
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>
export type SuccessResponse = z.infer<typeof SuccessResponseSchema>
export type User = z.infer<typeof UserSchema>
export type AuthResponse = z.infer<typeof AuthResponseSchema>
export type FileUploadRequest = z.infer<typeof FileUploadRequestSchema>
export type AnalysisRequest = z.infer<typeof AnalysisRequestSchema>
export type AnomalyRequest = z.infer<typeof AnomalyRequestSchema>
export type TimelineRequest = z.infer<typeof TimelineRequestSchema>
export type LoginForm = z.infer<typeof LoginFormSchema>
export type SignUpForm = z.infer<typeof SignUpFormSchema>
export type FileUpload = z.infer<typeof FileUploadSchema>
export type APIResponse = z.infer<typeof APIResponseSchema>

// Validation helpers
export const validateLogEntry = (data: unknown): LogEntry => {
  return LogEntrySchema.parse(data)
}

export const validateAnalysisResult = (data: unknown): AnalysisResult => {
  return AnalysisResultSchema.parse(data)
}

export const validateFileList = (data: unknown): FileListResponse => {
  return FileListResponseSchema.parse(data)
}

export const validateUploadResponse = (data: unknown): UploadResponse => {
  return UploadResponseSchema.parse(data)
}

export const validateAuthResponse = (data: unknown): AuthResponse => {
  return AuthResponseSchema.parse(data)
}

// Safe parsing (returns null if invalid)
export const safeParse = <T>(schema: z.ZodSchema<T>, data: unknown): T | null => {
  try {
    return schema.parse(data)
  } catch {
    return null
  }
}
