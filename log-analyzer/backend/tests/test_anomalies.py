import pytest
from datetime import datetime, timedelta
from services.anomalies import AnomalyDetector

class TestAnomalyDetector:
    """Test cases for AnomalyDetector service"""
    
    @pytest.fixture
    def detector(self):
        """Create an AnomalyDetector instance for testing"""
        return AnomalyDetector()
    
    @pytest.fixture
    def sample_logs(self):
        """Create sample log data for testing"""
        return [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'level': 'INFO',
                'message': 'Application started',
                'format': 'generic'
            },
            {
                'timestamp': '2024-01-15T10:01:00Z',
                'level': 'ERROR',
                'message': 'Database connection failed',
                'format': 'generic'
            },
            {
                'timestamp': '2024-01-15T10:02:00Z',
                'level': 'ERROR',
                'message': 'Database connection failed',
                'format': 'generic'
            },
            {
                'timestamp': '2024-01-15T10:03:00Z',
                'level': 'INFO',
                'message': 'User login successful',
                'format': 'generic'
            },
            {
                'timestamp': '2024-01-15T10:04:00Z',
                'level': 'ERROR',
                'message': 'Database connection failed',
                'format': 'generic'
            }
        ]
    
    @pytest.fixture
    def apache_logs(self):
        """Create sample Apache access logs for testing"""
        return [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'ip_address': '192.168.1.100',
                'method': 'GET',
                'url': '/api/users',
                'status_code': 200,
                'format': 'apache'
            },
            {
                'timestamp': '2024-01-15T10:01:00Z',
                'ip_address': '192.168.1.100',
                'method': 'GET',
                'url': '/api/users',
                'status_code': 404,
                'format': 'apache'
            },
            {
                'timestamp': '2024-01-15T10:02:00Z',
                'ip_address': '192.168.1.100',
                'method': 'POST',
                'url': '/api/users',
                'status_code': 500,
                'format': 'apache'
            }
        ]
    
    def test_detector_initialization(self, detector):
        """Test AnomalyDetector initialization"""
        assert detector is not None
        assert hasattr(detector, 'anomaly_types')
        assert 'error_spike' in detector.anomaly_types
        assert 'unusual_pattern' in detector.anomaly_types
    
    def test_detect_anomalies_empty_logs(self, detector):
        """Test anomaly detection with empty logs"""
        anomalies = detector.detect_anomalies([])
        assert len(anomalies) == 0
    
    def test_detect_error_spikes(self, detector, sample_logs):
        """Test error spike detection"""
        anomalies = detector._detect_error_spikes(sample_logs)
        
        # Should detect high error rate in the sample data
        assert len(anomalies) > 0
        
        # Check that we have error spike anomalies
        error_spikes = [a for a in anomalies if a['type'] == 'error_spike']
        assert len(error_spikes) > 0
    
    def test_detect_unusual_patterns(self, detector, sample_logs):
        """Test unusual pattern detection"""
        anomalies = detector._detect_unusual_patterns(sample_logs)
        
        # Should detect repeated error messages
        assert len(anomalies) > 0
        
        # Check that we have unusual pattern anomalies
        pattern_anomalies = [a for a in anomalies if a['type'] == 'unusual_pattern']
        assert len(pattern_anomalies) > 0
    
    def test_detect_frequency_anomalies(self, detector, sample_logs):
        """Test frequency anomaly detection"""
        anomalies = detector._detect_frequency_anomalies(sample_logs)
        
        # May or may not detect frequency anomalies depending on the data
        # Just ensure the method runs without errors
        assert isinstance(anomalies, list)
    
    def test_detect_time_anomalies(self, detector, sample_logs):
        """Test time anomaly detection"""
        # Add some logs outside business hours
        sample_logs.append({
            'timestamp': '2024-01-15T02:00:00Z',  # 2 AM
            'level': 'ERROR',
            'message': 'Night error',
            'format': 'generic'
        })
        
        anomalies = detector._detect_time_anomalies(sample_logs)
        
        # Should detect errors outside business hours
        time_anomalies = [a for a in anomalies if a['type'] == 'time_anomaly']
        assert len(time_anomalies) > 0
    
    def test_detect_ip_anomalies(self, detector, apache_logs):
        """Test IP anomaly detection"""
        # Add more logs from the same IP to trigger detection
        for i in range(100):
            apache_logs.append({
                'timestamp': f'2024-01-15T10:{i+5:02d}:00Z',
                'ip_address': '192.168.1.100',
                'method': 'GET',
                'url': f'/api/test{i}',
                'status_code': 404,
                'format': 'apache'
            })
        
        anomalies = detector._detect_ip_anomalies(apache_logs)
        
        # Should detect suspicious IP activity
        ip_anomalies = [a for a in anomalies if a['type'] == 'ip_anomaly']
        assert len(ip_anomalies) > 0
    
    def test_detect_status_anomalies(self, detector, apache_logs):
        """Test status code anomaly detection"""
        # Add more error status codes
        for i in range(20):
            apache_logs.append({
                'timestamp': f'2024-01-15T10:{i+5:02d}:00Z',
                'ip_address': '192.168.1.101',
                'method': 'GET',
                'url': f'/api/test{i}',
                'status_code': 500,
                'format': 'apache'
            })
        
        anomalies = detector._detect_status_anomalies(apache_logs)
        
        # Should detect high rate of 5xx errors
        status_anomalies = [a for a in anomalies if a['type'] == 'status_anomaly']
        assert len(status_anomalies) > 0
    
    def test_detect_all_anomalies(self, detector, sample_logs):
        """Test detection of all anomaly types"""
        anomalies = detector.detect_anomalies(sample_logs)
        
        # Should detect multiple types of anomalies
        assert len(anomalies) > 0
        
        # Check that we have different types
        anomaly_types = set(a['type'] for a in anomalies)
        assert len(anomaly_types) > 1
    
    def test_anomaly_severity_levels(self, detector, sample_logs):
        """Test anomaly severity levels"""
        anomalies = detector.detect_anomalies(sample_logs)
        
        for anomaly in anomalies:
            assert 'severity' in anomaly
            assert anomaly['severity'] in ['low', 'medium', 'high']
    
    def test_anomaly_timestamp_format(self, detector, sample_logs):
        """Test anomaly timestamp format"""
        anomalies = detector.detect_anomalies(sample_logs)
        
        for anomaly in anomalies:
            if 'timestamp' in anomaly:
                # Should be ISO format
                assert 'T' in anomaly['timestamp'] or '-' in anomaly['timestamp']
    
    def test_anomaly_details_structure(self, detector, sample_logs):
        """Test anomaly details structure"""
        anomalies = detector.detect_anomalies(sample_logs)
        
        for anomaly in anomalies:
            assert 'details' in anomaly
            assert isinstance(anomaly['details'], dict)
    
    def test_edge_case_single_log(self, detector):
        """Test anomaly detection with single log entry"""
        single_log = [{
            'timestamp': '2024-01-15T10:00:00Z',
            'level': 'ERROR',
            'message': 'Single error',
            'format': 'generic'
        }]
        
        anomalies = detector.detect_anomalies(single_log)
        
        # Should handle single log gracefully
        assert isinstance(anomalies, list)
    
    def test_edge_case_invalid_timestamps(self, detector):
        """Test anomaly detection with invalid timestamps"""
        invalid_logs = [
            {
                'timestamp': 'invalid-timestamp',
                'level': 'ERROR',
                'message': 'Error with invalid timestamp',
                'format': 'generic'
            },
            {
                'timestamp': None,
                'level': 'INFO',
                'message': 'Info without timestamp',
                'format': 'generic'
            }
        ]
        
        anomalies = detector.detect_anomalies(invalid_logs)
        
        # Should handle invalid timestamps gracefully
        assert isinstance(anomalies, list)
    
    def test_performance_large_dataset(self, detector):
        """Test performance with large dataset"""
        # Create large dataset
        large_logs = []
        for i in range(10000):
            large_logs.append({
                'timestamp': f'2024-01-15T{i//60:02d}:{i%60:02d}:00Z',
                'level': 'INFO' if i % 10 != 0 else 'ERROR',
                'message': f'Log entry {i}',
                'format': 'generic'
            })
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        anomalies = detector.detect_anomalies(large_logs)
        end_time = time.time()
        
        # Should complete in less than 5 seconds
        assert end_time - start_time < 5.0
        assert isinstance(anomalies, list)
