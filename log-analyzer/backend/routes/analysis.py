from flask import Blueprint, request, jsonify, current_app
from services.anomalies import AnomalyDetector
from services.parser import LogParser
from services.ai_helpers import AIHelper
from routes.auth import require_auth
from models.schemas import (
    AnalysisRequest, AnomalyRequest, TimelineRequest,
    AnalysisResultResponse, AnomalyResponse, TimelineDataResponse,
    StatisticsResponse, AISummaryResponse, LogLevel
)
from pydantic import ValidationError
import json

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
@require_auth
def analyze_logs():
    """Analyze uploaded log file for anomalies and insights"""
    try:
        # Validate request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({'error': 'Request body is required'}), 400
        
        validated_request = AnalysisRequest(**request_data)
        
        # Parse the log file with performance optimizations
        parser = LogParser()
        # Process all lines without sampling
        parsed_logs = parser.parse_file(validated_request.file_path, max_lines=20000, sample_rate=1.0)
        
        # Detect anomalies
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(parsed_logs)
        
        # Generate AI summary if available
        ai_summary = None
        if current_app.config.get('OPENAI_API_KEY'):
            ai_helper = AIHelper()
            ai_summary = ai_helper.generate_summary(parsed_logs, anomalies)
        
        # Generate timeline data for visualization (optimized)
        timeline_data = {}
        from datetime import datetime
        from collections import defaultdict
        
        # Use defaultdict for better performance
        hourly_stats = defaultdict(lambda: {'total': 0, 'errors': 0, 'warnings': 0, 'info': 0})
        
        for log in parsed_logs:
            timestamp = log.get('timestamp')
            if not timestamp:
                continue
                
            try:
                # Simplified timestamp parsing for performance
                if isinstance(timestamp, str):
                    dt = None
                    # Try most common format first
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        try:
                            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            continue  # Skip unparseable timestamps
                    
                    if dt:
                        hour_key = dt.strftime('%Y-%m-%d %H:00:00')
                        hourly_stats[hour_key]['total'] += 1
                        
                        level = log.get('level', 'INFO').upper()
                        if level in ['ERROR', 'CRITICAL', 'FATAL']:
                            hourly_stats[hour_key]['errors'] += 1
                        elif level in ['WARNING', 'WARN']:
                            hourly_stats[hour_key]['warnings'] += 1
                        else:
                            hourly_stats[hour_key]['info'] += 1
                            
            except Exception:
                continue
        
        # Convert defaultdict to regular dict
        timeline_data = dict(hourly_stats)
        
        
        # Prepare analysis results (optimized to avoid multiple list comprehensions)
        error_count = 0
        warning_count = 0
        info_count = 0
        
        for log in parsed_logs:
            level = log.get('level', '').upper()
            if level in ['ERROR', 'CRITICAL', 'FATAL']:
                error_count += 1
            elif level in ['WARNING', 'WARN']:
                warning_count += 1
            else:
                info_count += 1
        
        statistics = StatisticsResponse(
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count
        )
        
        # Convert anomalies to Pydantic models
        anomaly_responses = []
        for anomaly in anomalies:
            anomaly_responses.append(AnomalyResponse(
                type=anomaly.get('type', 'unknown'),
                severity=anomaly.get('severity', 'low'),
                description=anomaly.get('description', ''),
                timestamp=anomaly.get('timestamp'),
                details=anomaly.get('details', {})
            ))
        
        # Create AI summary response if available
        ai_summary_response = None
        if ai_summary:
            ai_summary_response = AISummaryResponse(
                summary=ai_summary.get('summary', ''),
                insights=ai_summary.get('insights', []),
                recommendations=ai_summary.get('recommendations', [])
            )
        
        analysis_result = AnalysisResultResponse(
            total_entries=len(parsed_logs),
            anomalies=anomaly_responses,
            ai_summary=ai_summary_response,
            statistics=statistics,
            timeline=timeline_data
        )
        
        return jsonify(analysis_result.model_dump())
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': f'Error analyzing logs: {str(e)}'}), 500

@analysis_bp.route('/anomalies', methods=['POST'])
@require_auth
def get_anomalies():
    """Get detailed anomaly analysis for a specific log file"""
    try:
        # Validate request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({'error': 'Request body is required'}), 400
        
        validated_request = AnomalyRequest(**request_data)
        
        # Parse and analyze
        parser = LogParser()
        parsed_logs = parser.parse_file(validated_request.file_path)
        
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(parsed_logs)
        
        # Group anomalies by type
        grouped_anomalies = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.get('type', 'unknown')
            if anomaly_type not in grouped_anomalies:
                grouped_anomalies[anomaly_type] = []
            grouped_anomalies[anomaly_type].append(anomaly)
        
        # Convert anomalies to Pydantic models
        anomaly_responses = []
        for anomaly in anomalies:
            anomaly_responses.append(AnomalyResponse(
                type=anomaly.get('type', 'unknown'),
                severity=anomaly.get('severity', 'low'),
                description=anomaly.get('description', ''),
                timestamp=anomaly.get('timestamp'),
                details=anomaly.get('details', {})
            ))
        
        return jsonify({
            'anomalies': [anomaly.model_dump() for anomaly in anomaly_responses],
            'grouped_anomalies': grouped_anomalies,
            'summary': {
                'total_anomalies': len(anomalies),
                'types': list(grouped_anomalies.keys())
            }
        })
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': f'Error getting anomalies: {str(e)}'}), 500

@analysis_bp.route('/timeline', methods=['POST'])
@require_auth
def get_timeline_data():
    """Get timeline data for visualization"""
    try:
        # Validate request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({'error': 'Request body is required'}), 400
        
        validated_request = TimelineRequest(**request_data)
        
        parser = LogParser()
        parsed_logs = parser.parse_file(validated_request.file_path)
        
        # Group logs by time intervals
        timeline_data = {}
        from datetime import datetime
        
        for log in parsed_logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    # Parse the timestamp to get the hour key
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
                        
                        # Round to hour for grouping
                        hour_key = dt.strftime('%Y-%m-%d %H:00:00')
                        
                        if hour_key not in timeline_data:
                            timeline_data[hour_key] = {
                                'total': 0,
                                'errors': 0,
                                'warnings': 0,
                                'info': 0
                            }
                        
                        timeline_data[hour_key]['total'] += 1
                        level = log.get('level', 'INFO').upper()
                        
                        if level in ['ERROR', 'CRITICAL', 'FATAL']:
                            timeline_data[hour_key]['errors'] += 1
                        elif level in ['WARNING', 'WARN']:
                            timeline_data[hour_key]['warnings'] += 1
                        else:
                            timeline_data[hour_key]['info'] += 1
                            
                except Exception as e:
                    continue
        
        timeline_response = TimelineDataResponse(
            timeline=timeline_data,
            total_entries=len(parsed_logs)
        )
        
        return jsonify(timeline_response.model_dump())
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': f'Error getting timeline data: {str(e)}'}), 500
