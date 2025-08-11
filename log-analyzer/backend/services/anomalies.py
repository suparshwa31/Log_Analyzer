from typing import List, Dict, Any
from collections import defaultdict, Counter
import statistics
from datetime import datetime, timedelta

class AnomalyDetector:
    """Detect anomalies in log data using various algorithms"""
    
    def __init__(self):
        self.anomaly_types = {
            'error_spike': 'Sudden increase in error rate',
            'unusual_pattern': 'Unusual log pattern detected',
            'frequency_anomaly': 'Abnormal frequency of events',
            'time_anomaly': 'Logs outside normal time patterns',
            'ip_anomaly': 'Suspicious IP activity',
            'status_anomaly': 'Unusual HTTP status codes'
        }
    
    def detect_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Main method to detect all types of anomalies"""
        if not logs:
            return []
        
        anomalies = []
        
        # Detect different types of anomalies
        anomalies.extend(self._detect_error_spikes(logs))
        anomalies.extend(self._detect_unusual_patterns(logs))
        anomalies.extend(self._detect_frequency_anomalies(logs))
        anomalies.extend(self._detect_time_anomalies(logs))
        anomalies.extend(self._detect_ip_anomalies(logs))
        anomalies.extend(self._detect_status_anomalies(logs))
        
        return anomalies
    
    def _detect_error_spikes(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sudden spikes in error rates"""
        anomalies = []
        
        # Group logs by time intervals (hourly)
        hourly_errors = defaultdict(int)
        hourly_total = defaultdict(int)
        
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    # Parse timestamp and round to hour
                    if isinstance(timestamp, str):
                        # Try to parse ISO format first
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            # Try common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                try:
                                    dt = datetime.strptime(timestamp, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                continue  # Skip if we can't parse the timestamp
                        
                        hour_key = dt.replace(minute=0, second=0, microsecond=0)
                        
                        hourly_total[hour_key] += 1
                        if log.get('level', '').upper() in ['ERROR', 'CRITICAL', 'FATAL']:
                            hourly_errors[hour_key] += 1
                        
                except (ValueError, TypeError):
                    continue
        
        # Calculate error rates and detect spikes
        error_rates = []
        for hour in sorted(hourly_total.keys()):
            if hourly_total[hour] > 0:
                rate = hourly_errors[hour] / hourly_total[hour]
                error_rates.append((hour, rate))
        
        if len(error_rates) > 1:
            rates = [rate for _, rate in error_rates]
            mean_rate = statistics.mean(rates)
            std_rate = statistics.stdev(rates) if len(rates) > 1 else 0
            
            for hour, rate in error_rates:
                if std_rate > 0 and abs(rate - mean_rate) > 2 * std_rate:
                    anomalies.append({
                        'type': 'error_spike',
                        'severity': 'high' if rate > mean_rate + 3 * std_rate else 'medium',
                        'timestamp': hour.isoformat(),
                        'description': f'Error rate spike: {rate:.2%} vs normal {mean_rate:.2%}',
                        'details': {
                            'current_rate': rate,
                            'normal_rate': mean_rate,
                            'deviation': abs(rate - mean_rate) / std_rate
                        }
                    })
        
        return anomalies
    
    def _detect_unusual_patterns(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual patterns in log messages"""
        anomalies = []
        
        # Look for repeated error messages (extract meaningful part after timestamp and level)
        error_messages = []
        for log in logs:
            if log.get('level', '').upper() in ['ERROR', 'CRITICAL', 'FATAL']:
                message = log.get('message', '')
                # Try to extract meaningful part (remove timestamp and level prefix if present)
                # Look for patterns like "ERROR Some message" or "2024-01-01 ERROR Some message"
                import re
                # Remove timestamp and level prefixes to focus on the actual error message
                cleaned_message = re.sub(r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}\s*', '', message)
                cleaned_message = re.sub(r'^(ERROR|CRITICAL|FATAL)\s*', '', cleaned_message, flags=re.IGNORECASE)
                
                if cleaned_message.strip():
                    error_messages.append(cleaned_message.strip())
        
        message_counts = Counter(error_messages)
        
        # Flag messages that appear too frequently
        total_errors = len(error_messages)
        if total_errors >= 3:  # Need at least 3 errors to detect patterns
            for message, count in message_counts.most_common(5):
                if count >= 3 and count > total_errors * 0.3:  # At least 3 occurrences and more than 30% of errors
                    anomalies.append({
                        'type': 'unusual_pattern',
                        'severity': 'medium',
                        'description': f'Repeated error pattern: "{message[:100]}{'...' if len(message) > 100 else ''}"',
                        'details': {
                            'message': message,
                            'count': count,
                            'percentage': count / total_errors
                        }
                    })
        
        return anomalies
    
    def _detect_frequency_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect abnormal frequency of events"""
        anomalies = []
        
        # Group by minute to detect burst activity
        minute_counts = defaultdict(int)
        
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        # Try to parse ISO format first
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            # Try common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                try:
                                    dt = datetime.strptime(timestamp, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                continue  # Skip if we can't parse the timestamp
                        
                        minute_key = dt.replace(second=0, microsecond=0)
                        minute_counts[minute_key] += 1
                except (ValueError, TypeError):
                    continue
        
        if minute_counts:
            counts = list(minute_counts.values())
            mean_count = statistics.mean(counts)
            std_count = statistics.stdev(counts) if len(counts) > 1 else 0
            
            for minute, count in minute_counts.items():
                if std_count > 0 and count > mean_count + 2 * std_count:
                    anomalies.append({
                        'type': 'frequency_anomaly',
                        'severity': 'medium',
                        'timestamp': minute.isoformat(),
                        'description': f'High log volume: {count} logs vs normal {mean_count:.1f}',
                        'details': {
                            'current_count': count,
                            'normal_count': mean_count,
                            'deviation': (count - mean_count) / std_count
                        }
                    })
        
        return anomalies
    
    def _detect_time_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect logs outside normal time patterns"""
        anomalies = []
        
        # Check for logs outside business hours (assuming 9 AM - 6 PM)
        business_hours = range(9, 18)
        
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        # Try to parse ISO format first
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            # Try common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                try:
                                    dt = datetime.strptime(timestamp, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                continue  # Skip if we can't parse the timestamp
                        
                        hour = dt.hour
                        
                        if hour not in business_hours and log.get('level', '').upper() in ['ERROR', 'CRITICAL', 'FATAL']:
                            anomalies.append({
                                'type': 'time_anomaly',
                                'severity': 'low',
                                'timestamp': timestamp,
                                'description': f'Error outside business hours: {hour:02d}:00',
                                'details': {
                                    'hour': hour,
                                    'business_hours': list(business_hours)
                                }
                            })
                except (ValueError, TypeError):
                    continue
        
        return anomalies
    
    def _detect_ip_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect suspicious IP activity"""
        anomalies = []
        
        # Group by IP address
        ip_activity = defaultdict(list)
        
        for log in logs:
            if log.get('format') == 'apache':
                ip = log.get('ip_address')
                if ip:
                    ip_activity[ip].append(log)
        
        # Check for IPs with unusual activity patterns
        for ip, ip_logs in ip_activity.items():
            if len(ip_logs) > 100:  # High volume from single IP
                error_count = len([log for log in ip_logs if log.get('status_code', 0) >= 400])
                error_rate = error_count / len(ip_logs)
                
                if error_rate > 0.5:  # More than 50% errors
                    anomalies.append({
                        'type': 'ip_anomaly',
                        'severity': 'high',
                        'description': f'Suspicious IP activity: {ip}',
                        'details': {
                            'ip_address': ip,
                            'total_requests': len(ip_logs),
                            'error_rate': error_rate,
                            'error_count': error_count
                        }
                    })
        
        return anomalies
    
    def _detect_status_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual HTTP status codes"""
        anomalies = []
        
        # Group by status code
        status_counts = defaultdict(int)
        
        for log in logs:
            if log.get('format') == 'apache':
                status = log.get('status_code')
                if status:
                    status_counts[status] += 1
        
        # Check for unusual status code patterns
        total_requests = sum(status_counts.values())
        if total_requests > 0:
            for status, count in status_counts.items():
                percentage = count / total_requests
                
                # Flag high rates of 4xx/5xx errors
                if status >= 400 and percentage > 0.1:  # More than 10% errors
                    anomalies.append({
                        'type': 'status_anomaly',
                        'severity': 'medium' if status < 500 else 'high',
                        'description': f'High rate of {status} status codes: {percentage:.1%}',
                        'details': {
                            'status_code': status,
                            'count': count,
                            'percentage': percentage,
                            'total_requests': total_requests
                        }
                    })
        
        return anomalies
