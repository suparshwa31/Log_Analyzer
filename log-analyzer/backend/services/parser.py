import re
import json
from datetime import datetime
from typing import List, Dict, Any

class LogParser:
    """Parse various log formats into structured JSON"""
    
    def __init__(self):
        # Common log patterns
        self.patterns = {
            'apache': re.compile(r'^(\S+) - - \[([^\]]+)\] "([^"]*)" (\d+) (\d+|-)'),
            'apache_error': re.compile(r'^\[([^\]]+)\] \[([^\]]+)\] (.*)'),
            'nginx': re.compile(r'^(\S+) - - \[([^\]]+)\] "([^"]*)" (\d+) (\d+|-)'),
            'syslog': re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:]+):\s*(.*)'),
            'json': re.compile(r'^\{.*\}$'),
            'timestamp': re.compile(r'^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})'),
            'level': re.compile(r'(ERROR|WARN|WARNING|INFO|DEBUG|CRITICAL|FATAL)', re.IGNORECASE)
        }
    
    def parse_file(self, file_path: str, max_lines: int = 10000, sample_rate: float = 1.0) -> List[Dict[str, Any]]:
        """Parse a log file and return structured data with optional sampling for performance"""
        parsed_logs = []
        lines_processed = 0
        
        try:
            # Check if this is a Supabase storage path
            if file_path.startswith('supabase://'):
                # Get file content from Supabase storage
                from utils.file_storage import get_file
                file_content = get_file(file_path)
                if file_content is None:
                    raise Exception(f"Could not retrieve file from Supabase storage: {file_path}")
                
                # Parse content as text
                lines = file_content.decode('utf-8', errors='ignore').split('\n')
                total_lines = len(lines)
                
                # Apply sampling for large files only if sample_rate < 1.0
                if sample_rate < 1.0 and total_lines > max_lines:
                    import random
                    # Sample lines randomly
                    sampled_indices = sorted(random.sample(range(total_lines), int(total_lines * sample_rate)))
                    lines = [lines[i] for i in sampled_indices]
                
                for line_num, line in enumerate(lines, 1):
                    if lines_processed >= max_lines:
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                    
                    parsed_entry = self.parse_line(line, line_num)
                    if parsed_entry:
                        parsed_logs.append(parsed_entry)
                        lines_processed += 1
            else:
                # Local file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    for line_num, line in enumerate(file, 1):
                        if lines_processed >= max_lines:
                            break
                            
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Apply sampling only if sample_rate < 1.0
                        if sample_rate < 1.0:
                            import random
                            if random.random() > sample_rate:
                                continue
                        
                        parsed_entry = self.parse_line(line, line_num)
                        if parsed_entry:
                            parsed_logs.append(parsed_entry)
                            lines_processed += 1
                        
        except Exception as e:
            raise Exception(f"Error parsing file {file_path}: {str(e)}")
        
        return parsed_logs
    
    def parse_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse a single log line"""
        # Try to detect log format
        if self.patterns['json'].match(line):
            return self._parse_json_line(line, line_num)
        elif self.patterns['apache_error'].match(line):
            return self._parse_apache_error_line(line, line_num)
        elif self.patterns['apache'].match(line):
            return self._parse_apache_line(line, line_num)
        elif self.patterns['syslog'].match(line):
            return self._parse_syslog_line(line, line_num)
        else:
            return self._parse_generic_line(line, line_num)
    
    def _parse_json_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse JSON formatted log line"""
        try:
            data = json.loads(line)
            return {
                'line_number': line_num,
                'timestamp': data.get('timestamp') or data.get('time') or data.get('@timestamp'),
                'level': data.get('level') or data.get('severity') or 'INFO',
                'message': data.get('message') or data.get('msg') or line,
                'service': data.get('service') or data.get('app'),
                'raw_line': line,
                'format': 'json'
            }
        except json.JSONDecodeError:
            return self._parse_generic_line(line, line_num)
    
    def _parse_apache_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Apache/Nginx access log line"""
        match = self.patterns['apache'].match(line)
        if match:
            ip, timestamp, request, status, size = match.groups()
            
            # Parse request components
            request_parts = request.split()
            method = request_parts[0] if len(request_parts) > 0 else ''
            url = request_parts[1] if len(request_parts) > 1 else ''
            
            return {
                'line_number': line_num,
                'timestamp': self._parse_timestamp(timestamp),
                'ip_address': ip,
                'method': method,
                'url': url,
                'status_code': int(status) if status.isdigit() else 0,
                'response_size': int(size) if size.isdigit() else 0,
                'raw_line': line,
                'format': 'apache'
            }
        return None
    
    def _parse_apache_error_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Apache error log line"""
        match = self.patterns['apache_error'].match(line)
        if match:
            timestamp, level, message = match.groups()
            
            return {
                'line_number': line_num,
                'timestamp': self._parse_timestamp(timestamp),
                'level': level.upper(),
                'message': message,
                'raw_line': line,
                'format': 'apache_error'
            }
        return None
    
    def _parse_syslog_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse syslog format line"""
        match = self.patterns['syslog'].match(line)
        if match:
            timestamp, hostname, service, message = match.groups()
            
            # Extract log level from message
            level_match = self.patterns['level'].search(message)
            level = level_match.group(1).upper() if level_match else 'INFO'
            
            return {
                'line_number': line_num,
                'timestamp': self._parse_timestamp(timestamp),
                'hostname': hostname,
                'service': service,
                'level': level,
                'message': message,
                'raw_line': line,
                'format': 'syslog'
            }
        return None
    
    def _parse_generic_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse generic log line with basic extraction"""
        # Try to extract timestamp
        timestamp_match = self.patterns['timestamp'].search(line)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # Try to extract log level
        level_match = self.patterns['level'].search(line)
        level = level_match.group(1).upper() if level_match else 'INFO'
        
        return {
            'line_number': line_num,
            'timestamp': timestamp,
            'level': level,
            'message': line,
            'raw_line': line,
            'format': 'generic'
        }
    
    def _parse_timestamp(self, timestamp_str: str) -> str:
        """Parse various timestamp formats"""
        try:
            # Common timestamp formats with year
            formats_with_year = [
                '%d/%b/%Y:%H:%M:%S %z',  # Apache access logs with timezone
                '%d/%b/%Y:%H:%M:%S',     # Apache access logs without timezone
                '%a %b %d %H:%M:%S %Y',  # Apache error logs: Thu Jun 09 06:07:04 2005
                '%Y-%m-%d %H:%M:%S',     # ISO format
                '%Y-%m-%dT%H:%M:%S',     # ISO format with T
                '%Y-%m-%dT%H:%M:%S.%fZ'  # ISO format with microseconds
            ]
            
            # Try formats with year first
            for fmt in formats_with_year:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # Formats without year - add current year
            formats_without_year = [
                '%b %d %H:%M:%S',        # Syslog format: Jun 09 06:07:04
                '%a %b %d %H:%M:%S',     # Apache error without year: Thu Jun 09 06:07:04
            ]
            
            current_year = datetime.now().year
            for fmt in formats_without_year:
                try:
                    # Parse without year first
                    dt = datetime.strptime(timestamp_str, fmt)
                    # Add current year
                    dt = dt.replace(year=current_year)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            return timestamp_str
            
        except Exception:
            return timestamp_str
