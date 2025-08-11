from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class LogFormat(str, Enum):
    APACHE = "apache"
    NGINX = "nginx"
    SYSLOG = "syslog"
    JSON = "json"
    GENERIC = "generic"

class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AnomalyType(str, Enum):
    ERROR_SPIKE = "error_spike"
    UNUSUAL_PATTERN = "unusual_pattern"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    TIME_ANOMALY = "time_anomaly"
    IP_ANOMALY = "ip_anomaly"
    STATUS_ANOMALY = "status_anomaly"

# Request Models
class FileUploadRequest(BaseModel):
    file_path: str = Field(..., description="Path to the uploaded file")
    user_id: Optional[str] = Field(None, description="User ID for the upload")

class AnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to the log file to analyze")

class AnomalyRequest(BaseModel):
    file_path: str = Field(..., description="Path to the log file to analyze for anomalies")

class TimelineRequest(BaseModel):
    file_path: str = Field(..., description="Path to the log file for timeline analysis")

# Response Models
class LogEntryResponse(BaseModel):
    line_number: int = Field(..., description="Line number in the log file")
    timestamp: Optional[str] = Field(None, description="Parsed timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    service: Optional[str] = Field(None, description="Service name")
    format: LogFormat = Field(..., description="Log format type")
    raw_line: str = Field(..., description="Original log line")
    
    # Apache/Nginx specific fields
    ip_address: Optional[str] = Field(None, description="IP address")
    method: Optional[str] = Field(None, description="HTTP method")
    url: Optional[str] = Field(None, description="Request URL")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    response_size: Optional[int] = Field(None, description="Response size in bytes")
    
    # Syslog specific fields
    hostname: Optional[str] = Field(None, description="Hostname")
    
    # Metadata
    user_id: Optional[str] = Field(None, description="User ID")
    file_id: Optional[str] = Field(None, description="File ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Analysis results
    anomaly_score: Optional[float] = Field(None, description="Anomaly detection score")
    anomaly_type: Optional[AnomalyType] = Field(None, description="Type of anomaly detected")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the log entry")

class AnomalyResponse(BaseModel):
    type: AnomalyType = Field(..., description="Type of anomaly")
    severity: AnomalySeverity = Field(..., description="Severity level")
    description: str = Field(..., description="Human-readable description")
    timestamp: Optional[str] = Field(None, description="When the anomaly occurred")
    details: Dict[str, Any] = Field(..., description="Detailed information about the anomaly")

class AISummaryResponse(BaseModel):
    summary: str = Field(..., description="AI-generated summary")
    insights: List[str] = Field(..., description="Key insights")
    recommendations: List[str] = Field(..., description="Recommended actions")

class StatisticsResponse(BaseModel):
    error_count: int = Field(..., description="Number of error logs")
    warning_count: int = Field(..., description="Number of warning logs")
    info_count: int = Field(..., description="Number of info logs")

class AnalysisResultResponse(BaseModel):
    total_entries: int = Field(..., description="Total number of log entries")
    anomalies: List[AnomalyResponse] = Field(..., description="Detected anomalies")
    ai_summary: Optional[AISummaryResponse] = Field(None, description="AI analysis summary")
    statistics: StatisticsResponse = Field(..., description="Log statistics")
    timeline: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Timeline data grouped by hour")

class TimelineDataResponse(BaseModel):
    timeline: Dict[str, Dict[str, int]] = Field(..., description="Timeline data grouped by hour")
    total_entries: int = Field(..., description="Total number of entries")

class FileInfoResponse(BaseModel):
    filename: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: float = Field(..., description="Upload timestamp")
    path: Optional[str] = Field(None, description="File path")

class FileListResponse(BaseModel):
    files: List[FileInfoResponse] = Field(..., description="List of uploaded files")

class UploadResponse(BaseModel):
    message: str = Field(..., description="Upload status message")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="Path to uploaded file")
    parse_result: Optional[List[Dict[str, Any]]] = Field(None, description="Parsing result")

class DeleteFileResponse(BaseModel):
    message: str = Field(..., description="Deletion status message")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

# User Models
class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    provider: str = Field(..., description="Authentication provider")

class AuthResponse(BaseModel):
    valid: bool = Field(..., description="Token validity")
    user: Optional[UserResponse] = Field(None, description="User information")
    error: Optional[str] = Field(None, description="Error message if validation failed")

# Validation Models
class LogAnalysisConfig(BaseModel):
    max_log_size: int = Field(default=52428800, description="Maximum log size in bytes")
    max_file_size: int = Field(default=104857600, description="Maximum file size in bytes")
    allowed_extensions: List[str] = Field(default=[".log", ".txt", ".gz", ".tar"], description="Allowed file extensions")
    
    @validator('max_log_size', 'max_file_size')
    def validate_positive_size(cls, v):
        if v <= 0:
            raise ValueError('Size must be positive')
        return v

class AnomalyDetectionConfig(BaseModel):
    error_spike_threshold: float = Field(default=2.0, description="Standard deviation threshold for error spikes")
    frequency_anomaly_threshold: float = Field(default=2.0, description="Standard deviation threshold for frequency anomalies")
    business_hours_start: int = Field(default=9, description="Business hours start (0-23)")
    business_hours_end: int = Field(default=18, description="Business hours end (0-23)")
    suspicious_ip_threshold: int = Field(default=100, description="Minimum requests for IP anomaly detection")
    high_error_rate_threshold: float = Field(default=0.5, description="Error rate threshold for IP anomalies")
    
    @validator('business_hours_start', 'business_hours_end')
    def validate_hours(cls, v):
        if not 0 <= v <= 23:
            raise ValueError('Hour must be between 0 and 23')
        return v
    
    @validator('business_hours_end')
    def validate_business_hours(cls, v, values):
        if 'business_hours_start' in values and v <= values['business_hours_start']:
            raise ValueError('Business hours end must be after start')
        return v
