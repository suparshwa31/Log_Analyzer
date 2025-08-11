import os
from typing import List, Dict, Any, Optional
import json
import openai

class AIHelper:
    """AI/LLM helper for generating log summaries and insights"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.enabled = bool(self.openai_api_key)
        
        if self.enabled:
            openai.api_key = self.openai_api_key
    
    def generate_summary(self, logs: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate AI-powered summary of log analysis"""
        if not self.enabled:
            return None
        
        try:
            # Prepare context for AI
            context = self._prepare_context(logs, anomalies)
            
            # Generate summary using OpenAI
            summary = self._call_openai_api(context)
            
            return {
                'summary': summary,
                'insights': self._extract_insights(summary),
                'recommendations': self._extract_recommendations(summary)
            }
            
        except Exception as e:
            print(f"AI summary generation failed: {str(e)}")
            # Fallback to basic summary if AI fails
            return self._generate_basic_summary(logs, anomalies)
    
    def _prepare_context(self, logs: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> str:
        """Prepare context for AI analysis"""
        # Count log levels
        level_counts = {}
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count anomalies by type
        anomaly_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.get('type', 'unknown')
            anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
        
        # Get sample log messages for context
        sample_messages = []
        for log in logs[:10]:  # First 10 logs
            if log.get('message'):
                sample_messages.append(log.get('message')[:100])  # First 100 chars
        
        # Create context string
        context = f"""
        Log Analysis Summary:
        - Total log entries: {len(logs)}
        - Log levels: {json.dumps(level_counts)}
        - Total anomalies detected: {len(anomalies)}
        - Anomaly types: {json.dumps(anomaly_counts)}
        
        Top anomalies:
        """
        
        for i, anomaly in enumerate(anomalies[:5]):
            context += f"\n{i+1}. {anomaly.get('description', 'Unknown')} (Severity: {anomaly.get('severity', 'unknown')})"
        
        if sample_messages:
            context += f"\n\nSample log messages:\n"
            for i, msg in enumerate(sample_messages[:5]):
                context += f"{i+1}. {msg}\n"
        
        return context
    
    def _call_openai_api(self, context: str) -> str:
        """Call OpenAI API for summary generation"""
        if not self.openai_api_key:
            return "AI analysis not available - no API key configured"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity and system administration expert. Analyze the provided log data and provide a concise, professional summary with actionable insights and recommendations."
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this log data and provide a summary:\n\n{context}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {str(e)}")
            # Fallback to basic summary
            return f"""
            Based on the log analysis, here are the key findings:
            
            {context}
            
            The system appears to be experiencing some operational issues that require attention.
            Consider investigating the detected anomalies and monitoring system performance.
            """
    
    def _extract_insights(self, summary: str) -> List[str]:
        """Extract key insights from AI summary"""
        # Simple keyword-based insight extraction
        insights = []
        
        if 'error' in summary.lower():
            insights.append("System errors detected")
        if 'performance' in summary.lower():
            insights.append("Performance issues identified")
        if 'security' in summary.lower():
            insights.append("Security concerns raised")
        if 'anomaly' in summary.lower():
            insights.append("Unusual patterns detected")
        if 'network' in summary.lower():
            insights.append("Network activity patterns identified")
        if 'access' in summary.lower():
            insights.append("Access patterns analyzed")
        
        return insights if insights else ["No specific insights available"]
    
    def _extract_recommendations(self, summary: str) -> List[str]:
        """Extract recommendations from AI summary"""
        # Simple keyword-based recommendation extraction
        recommendations = []
        
        if 'investigate' in summary.lower():
            recommendations.append("Investigate detected anomalies")
        if 'monitor' in summary.lower():
            recommendations.append("Monitor system performance")
        if 'review' in summary.lower():
            recommendations.append("Review system logs regularly")
        if 'update' in summary.lower():
            recommendations.append("Consider system updates")
        if 'security' in summary.lower():
            recommendations.append("Review security configurations")
        if 'backup' in summary.lower():
            recommendations.append("Verify backup systems")
        
        return recommendations if recommendations else ["Continue monitoring system health"]
    
    def _generate_basic_summary(self, logs: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic summary without AI"""
        # Count log levels
        level_counts = {}
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count anomalies by severity
        severity_counts = {}
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'summary': f"Analysis complete. Found {len(logs)} log entries with {len(anomalies)} anomalies.",
            'insights': [
                f"Log distribution: {json.dumps(level_counts)}",
                f"Anomaly severity: {json.dumps(severity_counts)}"
            ],
            'recommendations': [
                "Review high-severity anomalies first",
                "Monitor error rates over time",
                "Check system performance metrics"
            ]
        }
    
    def analyze_log_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in log data"""
        if not self.enabled:
            return {"error": "AI analysis not available"}
        
        try:
            # Group logs by hour
            hourly_patterns = {}
            for log in logs:
                timestamp = log.get('timestamp')
                if timestamp:
                    try:
                        # Extract hour from timestamp
                        hour = timestamp[:13] + ':00:00'  # Round to hour
                        if hour not in hourly_patterns:
                            hourly_patterns[hour] = {'total': 0, 'errors': 0}
                        
                        hourly_patterns[hour]['total'] += 1
                        if log.get('level', '').upper() == 'ERROR':
                            hourly_patterns[hour]['errors'] += 1
                            
                    except (ValueError, TypeError):
                        continue
            
            return {
                'hourly_patterns': hourly_patterns,
                'total_entries': len(logs),
                'pattern_analysis': "Log volume and error patterns analyzed"
            }
            
        except Exception as e:
            return {"error": f"Pattern analysis failed: {str(e)}"}
    
    def suggest_improvements(self, logs: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> List[str]:
        """Suggest system improvements based on log analysis"""
        suggestions = []
        
        # Analyze error patterns
        error_logs = [log for log in logs if log.get('level', '').upper() == 'ERROR']
        if len(error_logs) > len(logs) * 0.1:  # More than 10% errors
            suggestions.append("High error rate detected - review system configuration")
        
        # Analyze response times (for web logs)
        if any(log.get('format') == 'apache' for log in logs):
            suggestions.append("Monitor web server response times")
        
        # Analyze IP patterns
        ip_logs = [log for log in logs if log.get('ip_address')]
        if ip_logs:
            unique_ips = len(set(log.get('ip_address') for log in ip_logs))
            if unique_ips > 1000:
                suggestions.append("High number of unique IPs - consider rate limiting")
        
        return suggestions if suggestions else ["System appears to be operating normally"]
