import pytest
from models.schemas import (
    LogLevel, LogFormat, AnomalySeverity, AnomalyType,
    AnalysisRequest, AnomalyRequest, TimelineRequest,
    LogEntryResponse, AnomalyResponse, StatisticsResponse,
    AnalysisResultResponse, TimelineDataResponse,
    FileInfoResponse, FileListResponse, UploadResponse,
    DeleteFileResponse, ErrorResponse, SuccessResponse,
    UserResponse, AuthResponse, LogAnalysisConfig,
    AnomalyDetectionConfig
)

class TestSchemas:
    """Test cases for Pydantic schemas"""
    
    def test_log_level_enum(self):
        """Test LogLevel enum values"""
        assert LogLevel.INFO == "INFO"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.CRITICAL == "CRITICAL"
        assert LogLevel.FATAL == "FATAL"
    
    def test_log_format_enum(self):
        """Test LogFormat enum values"""
        assert LogFormat.APACHE == "apache"
        assert LogFormat.NGINX == "nginx"
        assert LogFormat.SYSLOG == "syslog"
        assert LogFormat.JSON == "json"
        assert LogFormat.GENERIC == "generic"
    
    def test_anomaly_severity_enum(self):
        """Test AnomalySeverity enum values"""
        assert AnomalySeverity.LOW == "low"
        assert AnomalySeverity.MEDIUM == "medium"
        assert AnomalySeverity.HIGH == "high"
    
    def test_anomaly_type_enum(self):
        """Test AnomalyType enum values"""
        assert AnomalyType.ERROR_SPIKE == "error_spike"
        assert AnomalyType.UNUSUAL_PATTERN == "unusual_pattern"
        assert AnomalyType.FREQUENCY_ANOMALY == "frequency_anomaly"
        assert AnomalyType.TIME_ANOMALY == "time_anomaly"
        assert AnomalyType.IP_ANOMALY == "ip_anomaly"
        assert AnomalyType.STATUS_ANOMALY == "status_anomaly"
    
    def test_analysis_request_validation(self):
        """Test AnalysisRequest validation"""
        # Valid request
        request = AnalysisRequest(file_path="/path/to/logs.log")
        assert request.file_path == "/path/to/logs.log"
        
        # Missing required field should raise error
        with pytest.raises(ValueError):
            AnalysisRequest()
    
    def test_anomaly_request_validation(self):
        """Test AnomalyRequest validation"""
        request = AnomalyRequest(file_path="/path/to/logs.log")
        assert request.file_path == "/path/to/logs.log"
    
    def test_timeline_request_validation(self):
        """Test TimelineRequest validation"""
        request = TimelineRequest(file_path="/path/to/logs.log")
        assert request.file_path == "/path/to/logs.log"
    
    def test_log_entry_response_validation(self):
        """Test LogEntryResponse validation"""
        log_entry = LogEntryResponse(
            line_number=1,
            level=LogLevel.INFO,
            message="Test log message",
            format=LogFormat.GENERIC,
            raw_line="2024-01-15 INFO Test log message"
        )
        assert log_entry.line_number == 1
        assert log_entry.level == LogLevel.INFO
        assert log_entry.message == "Test log message"
        assert log_entry.format == LogFormat.GENERIC
    
    def test_anomaly_response_validation(self):
        """Test AnomalyResponse validation"""
        anomaly = AnomalyResponse(
            type=AnomalyType.ERROR_SPIKE,
            severity=AnomalySeverity.HIGH,
            description="High error rate detected",
            details={"error_rate": 0.15, "threshold": 0.05}
        )
        assert anomaly.type == AnomalyType.ERROR_SPIKE
        assert anomaly.severity == AnomalySeverity.HIGH
        assert anomaly.description == "High error rate detected"
        assert anomaly.details["error_rate"] == 0.15
    
    def test_statistics_response_validation(self):
        """Test StatisticsResponse validation"""
        stats = StatisticsResponse(
            error_count=100,
            warning_count=50,
            info_count=1000
        )
        assert stats.error_count == 100
        assert stats.warning_count == 50
        assert stats.info_count == 1000
    
    def test_analysis_result_response_validation(self):
        """Test AnalysisResultResponse validation"""
        stats = StatisticsResponse(
            error_count=100,
            warning_count=50,
            info_count=1000
        )
        
        anomaly = AnomalyResponse(
            type=AnomalyType.ERROR_SPIKE,
            severity=AnomalySeverity.HIGH,
            description="High error rate detected",
            details={"error_rate": 0.15}
        )
        
        result = AnalysisResultResponse(
            total_entries=1150,
            anomalies=[anomaly],
            statistics=stats
        )
        
        assert result.total_entries == 1150
        assert len(result.anomalies) == 1
        assert result.statistics.error_count == 100
    
    def test_file_info_response_validation(self):
        """Test FileInfoResponse validation"""
        file_info = FileInfoResponse(
            filename="test.log",
            size=1024,
            uploaded_at=1642233600.0
        )
        assert file_info.filename == "test.log"
        assert file_info.size == 1024
        assert file_info.uploaded_at == 1642233600.0
    
    def test_file_list_response_validation(self):
        """Test FileListResponse validation"""
        file_info = FileInfoResponse(
            filename="test.log",
            size=1024,
            uploaded_at=1642233600.0
        )
        
        file_list = FileListResponse(files=[file_info])
        assert len(file_list.files) == 1
        assert file_list.files[0].filename == "test.log"
    
    def test_upload_response_validation(self):
        """Test UploadResponse validation"""
        upload = UploadResponse(
            message="File uploaded successfully",
            filename="test.log",
            file_path="/uploads/test.log"
        )
        assert upload.message == "File uploaded successfully"
        assert upload.filename == "test.log"
        assert upload.file_path == "/uploads/test.log"
    
    def test_delete_file_response_validation(self):
        """Test DeleteFileResponse validation"""
        delete = DeleteFileResponse(message="File deleted successfully")
        assert delete.message == "File deleted successfully"
    
    def test_error_response_validation(self):
        """Test ErrorResponse validation"""
        error = ErrorResponse(
            error="File not found",
            details="The requested file does not exist"
        )
        assert error.error == "File not found"
        assert error.details == "The requested file does not exist"
    
    def test_success_response_validation(self):
        """Test SuccessResponse validation"""
        success = SuccessResponse(
            message="Operation completed successfully",
            data={"status": "ok"}
        )
        assert success.message == "Operation completed successfully"
        assert success.data["status"] == "ok"
    
    def test_user_response_validation(self):
        """Test UserResponse validation"""
        user = UserResponse(
            id="user123",
            email="test@example.com",
            role="user",
            provider="supabase"
        )
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.provider == "supabase"
    
    def test_auth_response_validation(self):
        """Test AuthResponse validation"""
        user = UserResponse(
            id="user123",
            email="test@example.com",
            role="user",
            provider="supabase"
        )
        
        auth = AuthResponse(valid=True, user=user)
        assert auth.valid is True
        assert auth.user is not None
        assert auth.user.id == "user123"
    
    def test_log_analysis_config_validation(self):
        """Test LogAnalysisConfig validation"""
        config = LogAnalysisConfig(
            max_log_size=10485760,  # 10MB
            max_file_size=52428800,  # 50MB
            allowed_extensions=[".log", ".txt"]
        )
        assert config.max_log_size == 10485760
        assert config.max_file_size == 52428800
        assert ".log" in config.allowed_extensions
        
        # Test validation error for negative size
        with pytest.raises(ValueError):
            LogAnalysisConfig(max_log_size=-1)
    
    def test_anomaly_detection_config_validation(self):
        """Test AnomalyDetectionConfig validation"""
        config = AnomalyDetectionConfig(
            error_spike_threshold=2.5,
            frequency_anomaly_threshold=2.0,
            business_hours_start=8,
            business_hours_end=17,
            suspicious_ip_threshold=150,
            high_error_rate_threshold=0.6
        )
        assert config.error_spike_threshold == 2.5
        assert config.business_hours_start == 8
        assert config.business_hours_end == 17
        
        # Test validation error for invalid hours
        with pytest.raises(ValueError):
            AnomalyDetectionConfig(business_hours_start=25)
        
        # Test validation error for business hours end before start
        with pytest.raises(ValueError):
            AnomalyDetectionConfig(business_hours_start=10, business_hours_end=9)
    
    def test_model_serialization(self):
        """Test that models can be serialized to dict"""
        log_entry = LogEntryResponse(
            line_number=1,
            level=LogLevel.INFO,
            message="Test message",
            format=LogFormat.GENERIC,
            raw_line="Test raw line"
        )
        
        # Test serialization
        data = log_entry.model_dump()
        assert isinstance(data, dict)
        assert data["line_number"] == 1
        assert data["level"] == "INFO"
        
        # Test JSON serialization
        json_data = log_entry.model_dump_json()
        assert isinstance(json_data, str)
        assert "INFO" in json_data
