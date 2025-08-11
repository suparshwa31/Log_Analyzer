from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class LogEntry:
    """Data model for log entries"""
    
    id: Optional[str] = None
    timestamp: Optional[str] = None
    level: str = 'INFO'
    message: str = ''
    service: Optional[str] = None
    format: str = 'generic'
    line_number: Optional[int] = None
    raw_line: str = ''
    
    # Apache/Nginx specific fields
    ip_address: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    response_size: Optional[int] = None
    
    # Syslog specific fields
    hostname: Optional[str] = None
    
    # Metadata
    user_id: Optional[str] = None
    file_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Analysis results
    anomaly_score: Optional[float] = None
    anomaly_type: Optional[str] = None
    tags: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        
        # Handle datetime objects
        if data.get('created_at') and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if data.get('updated_at') and isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        # Handle tags
        if data.get('tags') and isinstance(data['tags'], list):
            data['tags'] = json.dumps(data['tags'])
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create from dictionary"""
        # Handle tags
        if data.get('tags') and isinstance(data['tags'], str):
            try:
                data['tags'] = json.loads(data['tags'])
            except json.JSONDecodeError:
                data['tags'] = []
        
        # Handle datetime strings
        if data.get('created_at') and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            except ValueError:
                data['created_at'] = None
        
        if data.get('updated_at') and isinstance(data['updated_at'], str):
            try:
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                data['updated_at'] = None
        
        return cls(**data)
    
    def to_supabase_format(self) -> Dict[str, Any]:
        """Convert to Supabase-compatible format"""
        data = self.to_dict()
        
        # Remove None values for Supabase
        data = {k: v for k, v in data.items() if v is not None}
        
        # Ensure required fields
        if not data.get('created_at'):
            data['created_at'] = datetime.utcnow().isoformat()
        
        return data
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the log entry"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'level': self.level,
            'message': self.message[:100] + '...' if len(self.message) > 100 else self.message,
            'service': self.service,
            'format': self.format,
            'anomaly_score': self.anomaly_score,
            'anomaly_type': self.anomaly_type
        }
    
    def is_error(self) -> bool:
        """Check if this is an error log"""
        return self.level.upper() in ['ERROR', 'CRITICAL', 'FATAL']
    
    def is_warning(self) -> bool:
        """Check if this is a warning log"""
        return self.level.upper() in ['WARNING', 'WARN']
    
    def is_info(self) -> bool:
        """Check if this is an info log"""
        return self.level.upper() in ['INFO', 'DEBUG']
    
    def get_severity_score(self) -> int:
        """Get numeric severity score"""
        severity_map = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'WARN': 2,
            'ERROR': 3,
            'CRITICAL': 4,
            'FATAL': 5
        }
        return severity_map.get(self.level.upper(), 1)
    
    def add_tag(self, tag: str):
        """Add a tag to the log entry"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the log entry"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if log entry has a specific tag"""
        return self.tags and tag in self.tags if self.tags else False
