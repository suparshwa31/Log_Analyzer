import pytest
import tempfile
import os
from services.parser import LogParser

class TestLogParser:
    """Test cases for LogParser service"""
    
    @pytest.fixture
    def parser(self):
        """Create a LogParser instance for testing"""
        return LogParser()
    
    @pytest.fixture
    def temp_log_file(self):
        """Create a temporary log file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("""2024-01-15 10:30:00 [INFO] Application started
2024-01-15 10:30:01 [ERROR] Database connection failed
2024-01-15 10:30:02 [WARNING] High memory usage detected
""")
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    def test_parser_initialization(self, parser):
        """Test LogParser initialization"""
        assert parser is not None
        assert hasattr(parser, 'patterns')
        assert 'apache' in parser.patterns
        assert 'syslog' in parser.patterns
        assert 'json' in parser.patterns
    
    def test_parse_generic_line(self, parser):
        """Test parsing generic log lines"""
        line = "2024-01-15 10:30:00 [INFO] Application started"
        result = parser.parse_line(line, 1)
        
        assert result is not None
        assert result['line_number'] == 1
        assert result['timestamp'] == '2024-01-15 10:30:00'
        assert result['level'] == 'INFO'
        assert result['message'] == line
        assert result['format'] == 'generic'
    
    def test_parse_apache_line(self, parser):
        """Test parsing Apache access log lines"""
        line = '192.168.1.100 - - [15/Jan/2024:10:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234'
        result = parser.parse_line(line, 1)
        
        assert result is not None
        assert result['line_number'] == 1
        assert result['ip_address'] == '192.168.1.100'
        assert result['method'] == 'GET'
        assert result['url'] == '/api/users'
        assert result['status_code'] == 200
        assert result['response_size'] == 1234
        assert result['format'] == 'apache'
    
    def test_parse_syslog_line(self, parser):
        """Test parsing syslog format lines"""
        line = 'Jan 15 10:30:00 server01 sshd[1234]: Failed password for user admin from 192.168.1.100'
        result = parser.parse_line(line, 1)
        
        assert result is not None
        assert result['line_number'] == 1
        assert result['hostname'] == 'server01'
        assert result['service'] == 'sshd'
        assert result['level'] == 'INFO'  # Default level for syslog
        assert result['format'] == 'syslog'
    
    def test_parse_json_line(self, parser):
        """Test parsing JSON formatted log lines"""
        line = '{"timestamp": "2024-01-15T10:30:00Z", "level": "ERROR", "message": "Database error", "service": "api"}'
        result = parser.parse_line(line, 1)
        
        assert result is not None
        assert result['line_number'] == 1
        assert result['timestamp'] == '2024-01-15T10:30:00Z'
        assert result['level'] == 'ERROR'
        assert result['message'] == 'Database error'
        assert result['service'] == 'api'
        assert result['format'] == 'json'
    
    def test_parse_file(self, parser, temp_log_file):
        """Test parsing an entire log file"""
        results = parser.parse_file(temp_log_file)
        
        assert len(results) == 3
        assert results[0]['level'] == 'INFO'
        assert results[1]['level'] == 'ERROR'
        assert results[2]['level'] == 'WARNING'
    
    def test_parse_line_with_invalid_timestamp(self, parser):
        """Test parsing lines with invalid timestamps"""
        line = "Invalid timestamp [INFO] Some message"
        result = parser.parse_line(line, 1)
        
        assert result is not None
        assert result['timestamp'] is None
        assert result['level'] == 'INFO'
        assert result['message'] == line
    
    def test_parse_empty_line(self, parser):
        """Test parsing empty lines"""
        line = ""
        result = parser.parse_line(line, 1)
        
        assert result is None
    
    def test_parse_whitespace_line(self, parser):
        """Test parsing whitespace-only lines"""
        line = "   \n\t  "
        result = parser.parse_line(line, 1)
        
        assert result is None
    
    def test_timestamp_parsing_formats(self, parser):
        """Test parsing various timestamp formats"""
        # Test ISO format
        line1 = "2024-01-15T10:30:00Z [INFO] Message 1"
        result1 = parser.parse_line(line1, 1)
        assert result1['timestamp'] == '2024-01-15T10:30:00Z'
        
        # Test space-separated format
        line2 = "2024-01-15 10:30:00 [INFO] Message 2"
        result2 = parser.parse_line(line2, 2)
        assert result2['timestamp'] == '2024-01-15 10:30:00'
    
    def test_level_detection(self, parser):
        """Test log level detection"""
        # Test various level formats
        levels = ['ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'CRITICAL', 'FATAL']
        
        for level in levels:
            line = f"2024-01-15 10:30:00 [{level}] Test message"
            result = parser.parse_line(line, 1)
            assert result['level'] == level.upper()
    
    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file"""
        with pytest.raises(Exception):
            parser.parse_file('/nonexistent/file.log')
    
    def test_parse_large_file(self, parser):
        """Test parsing a large log file"""
        # Create a large log file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            for i in range(1000):
                f.write(f"2024-01-15 10:30:{i:02d} [INFO] Log entry {i}\n")
            temp_file = f.name
        
        try:
            results = parser.parse_file(temp_file)
            assert len(results) == 1000
        finally:
            os.unlink(temp_file)
