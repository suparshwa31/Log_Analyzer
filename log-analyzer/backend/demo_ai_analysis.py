#!/usr/bin/env python3
"""
Demo script for AI Analysis Summary functionality
Shows how the OpenAI API integration works for generating summaries, insights, and recommendations.
"""

import os
import sys
from services.ai_helpers import AIHelper

def main():
    """Demonstrate AI Analysis Summary functionality"""
    
    # Sample log data
    sample_logs = [
        {'level': 'ERROR', 'message': 'Database connection timeout', 'timestamp': '2024-01-01T10:00:00'},
        {'level': 'ERROR', 'message': 'Failed to authenticate user', 'timestamp': '2024-01-01T10:01:00'},
        {'level': 'WARNING', 'message': 'High memory usage detected (85%)', 'timestamp': '2024-01-01T10:02:00'},
        {'level': 'INFO', 'message': 'User login successful', 'timestamp': '2024-01-01T10:03:00'},
        {'level': 'ERROR', 'message': 'API endpoint returned 500 status', 'timestamp': '2024-01-01T10:04:00'},
        {'level': 'WARNING', 'message': 'Slow query detected (3.2s)', 'timestamp': '2024-01-01T10:05:00'},
        {'level': 'INFO', 'message': 'Batch job completed successfully', 'timestamp': '2024-01-01T10:06:00'},
        {'level': 'ERROR', 'message': 'Redis connection lost', 'timestamp': '2024-01-01T10:07:00'},
        {'level': 'WARNING', 'message': 'Disk usage at 90%', 'timestamp': '2024-01-01T10:08:00'},
        {'level': 'INFO', 'message': 'Cache cleared successfully', 'timestamp': '2024-01-01T10:09:00'}
    ]
    
    # Sample anomalies
    sample_anomalies = [
        {
            'type': 'error_spike',
            'severity': 'high',
            'description': 'Error rate spike detected: 40% of logs are errors',
            'timestamp': '2024-01-01T10:00:00',
            'details': {'error_count': 4, 'total_count': 10, 'threshold': 0.1}
        },
        {
            'type': 'unusual_pattern',
            'severity': 'medium',
            'description': 'Multiple database connectivity issues',
            'timestamp': '2024-01-01T10:02:00',
            'details': {'pattern': 'database_issues', 'occurrences': 3}
        }
    ]
    
    # Initialize AI helper
    ai_helper = AIHelper()
    
    
    if ai_helper.enabled:
        
        try:
            # Generate AI summary
            result = ai_helper.generate_summary(sample_logs, sample_anomalies)
            
            if result:
                # AI summary generated successfully
                pass
            else:
                # Failed to generate AI summary
                pass
        
        except Exception as e:
            # Error generating AI analysis
            pass
    
    else:
        # Generate basic fallback summary
        basic_result = ai_helper._generate_basic_summary(sample_logs, sample_anomalies)
    
    # Demo complete

if __name__ == "__main__":
    main()
