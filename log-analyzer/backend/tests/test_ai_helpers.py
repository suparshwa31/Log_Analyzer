import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.ai_helpers import AIHelper


class TestAIHelper:
    """Test cases for AI helper functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.sample_logs = [
            {'level': 'ERROR', 'message': 'Database connection failed', 'timestamp': '2024-01-01T10:00:00'},
            {'level': 'WARNING', 'message': 'High memory usage detected', 'timestamp': '2024-01-01T10:01:00'},
            {'level': 'INFO', 'message': 'User login successful', 'timestamp': '2024-01-01T10:02:00'},
            {'level': 'ERROR', 'message': 'API timeout occurred', 'timestamp': '2024-01-01T10:03:00'},
            {'level': 'INFO', 'message': 'Batch job completed', 'timestamp': '2024-01-01T10:04:00'}
        ]
        
        self.sample_anomalies = [
            {
                'type': 'error_spike',
                'severity': 'high',
                'description': 'Error rate spike detected',
                'timestamp': '2024-01-01T10:00:00',
                'details': {'error_count': 10, 'threshold': 2}
            },
            {
                'type': 'unusual_pattern',
                'severity': 'medium',
                'description': 'Unusual login pattern detected',
                'timestamp': '2024-01-01T10:01:00',
                'details': {'pattern': 'multiple_failed_attempts'}
            }
        ]

    def test_ai_helper_initialization_without_api_key(self):
        """Test AIHelper initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()
            assert not helper.enabled
            assert helper.client is None

    def test_ai_helper_initialization_with_api_key(self):
        """Test AIHelper initialization with API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('services.ai_helpers.OpenAI') as mock_openai:
                helper = AIHelper()
                assert helper.enabled
                assert helper.client is not None
                mock_openai.assert_called_once_with(api_key='test-key')

    def test_generate_summary_without_api_key(self):
        """Test summary generation without API key"""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()
            result = helper.generate_summary(self.sample_logs, self.sample_anomalies)
            assert result is None

    def test_generate_basic_summary(self):
        """Test basic summary generation (fallback)"""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()
            result = helper._generate_basic_summary(self.sample_logs, self.sample_anomalies)
            
            assert 'summary' in result
            assert 'insights' in result
            assert 'recommendations' in result
            assert len(result['insights']) > 0
            assert len(result['recommendations']) > 0

    @patch('services.ai_helpers.OpenAI')
    def test_generate_summary_with_api_success(self, mock_openai_class):
        """Test successful summary generation with OpenAI API"""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock responses for each API call
        mock_summary_response = MagicMock()
        mock_summary_response.choices[0].message.content = "System analysis shows high error rates and performance issues."
        
        mock_insights_response = MagicMock()
        mock_insights_response.choices[0].message.content = '["High error rate detected", "Performance degradation observed", "Database connectivity issues"]'
        
        mock_recommendations_response = MagicMock()
        mock_recommendations_response.choices[0].message.content = '["Investigate database connections", "Monitor error patterns", "Review system performance"]'
        
        # Set up the mock to return different responses for each call
        mock_client.chat.completions.create.side_effect = [
            mock_summary_response,
            mock_insights_response,
            mock_recommendations_response
        ]
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            helper = AIHelper()
            result = helper.generate_summary(self.sample_logs, self.sample_anomalies)
            
            assert result is not None
            assert 'summary' in result
            assert 'insights' in result
            assert 'recommendations' in result
            assert isinstance(result['insights'], list)
            assert isinstance(result['recommendations'], list)
            assert len(result['insights']) > 0
            assert len(result['recommendations']) > 0

    @patch('services.ai_helpers.OpenAI')
    def test_generate_summary_with_api_failure(self, mock_openai_class):
        """Test summary generation with API failure (fallback to basic)"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            helper = AIHelper()
            result = helper.generate_summary(self.sample_logs, self.sample_anomalies)
            
            assert result is not None
            assert 'summary' in result
            assert 'insights' in result
            assert 'recommendations' in result

    def test_prepare_context(self):
        """Test context preparation for AI analysis"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('services.ai_helpers.OpenAI'):
                helper = AIHelper()
                context = helper._prepare_context(self.sample_logs, self.sample_anomalies)
                
                assert 'Total log entries: 5' in context
                assert 'Total anomalies detected: 2' in context
                assert 'error_spike' in context
                assert 'unusual_pattern' in context

    @patch('services.ai_helpers.OpenAI')
    def test_generate_insights_json_response(self, mock_openai_class):
        """Test insights generation with JSON response"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '["High error rate detected", "System performance issues"]'
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            helper = AIHelper()
            context = helper._prepare_context(self.sample_logs, self.sample_anomalies)
            insights = helper._generate_insights(context)
            
            assert isinstance(insights, list)
            assert len(insights) == 2
            assert "High error rate detected" in insights

    @patch('services.ai_helpers.OpenAI')
    def test_generate_recommendations_json_response(self, mock_openai_class):
        """Test recommendations generation with JSON response"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '["Investigate database issues", "Monitor system performance"]'
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            helper = AIHelper()
            context = helper._prepare_context(self.sample_logs, self.sample_anomalies)
            recommendations = helper._generate_recommendations(context)
            
            assert isinstance(recommendations, list)
            assert len(recommendations) == 2
            assert "Investigate database issues" in recommendations

    def test_analyze_log_patterns_without_api_key(self):
        """Test log pattern analysis without API key"""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()
            result = helper.analyze_log_patterns(self.sample_logs)
            assert 'error' in result

    def test_suggest_improvements(self):
        """Test system improvement suggestions"""
        helper = AIHelper()
        
        # Test with high error rate
        error_heavy_logs = [{'level': 'ERROR'} for _ in range(8)] + [{'level': 'INFO'} for _ in range(2)]
        suggestions = helper.suggest_improvements(error_heavy_logs, [])
        assert any("High error rate detected" in suggestion for suggestion in suggestions)
        
        # Test with normal logs
        normal_logs = [{'level': 'INFO'} for _ in range(10)]
        suggestions = helper.suggest_improvements(normal_logs, [])
        assert len(suggestions) > 0
