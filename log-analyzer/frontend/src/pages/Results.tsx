import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../lib/supabaseClient'
import { ArrowLeft, AlertTriangle, Info, CheckCircle } from 'lucide-react'
import ResultsTable from '../components/ResultsTable'
import TimelineChart from '../components/TimelineChart'
import AnomalyHighlight from '../components/AnomalyHighlight'
import type { UploadResponse, LogEntry, AnalysisResult, Anomaly } from '../lib/schemas'

export default function Results() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [resolvedAnomalies, setResolvedAnomalies] = useState<Array<{
    type: string
    severity: string
    description: string
    timestamp?: string
    details: any
    resolvedAt: string
  }>>([])
  const [selectedFile, setSelectedFile] = useState<string>('')
  const [investigationModal, setInvestigationModal] = useState<{
    isOpen: boolean
    anomaly: any
  }>({ isOpen: false, anomaly: null })
  const [viewLogsModal, setViewLogsModal] = useState<{
    isOpen: boolean
    anomaly: any
    logs: LogEntry[]
  }>({ isOpen: false, anomaly: null, logs: [] })
  const navigate = useNavigate()
  const location = useLocation()

  // Helper function to create analysis result from parsed log data
  const createAnalysisResultFromParseResult = (parseResult: LogEntry[], uploadedFile: UploadResponse): AnalysisResult => {
    // Count log levels
    const errorCount = parseResult.filter(entry => 
      entry.level && ['ERROR', 'CRITICAL', 'FATAL'].includes(entry.level.toUpperCase())
    ).length
    
    const warningCount = parseResult.filter(entry => 
      entry.level && ['WARNING', 'WARN'].includes(entry.level.toUpperCase())
    ).length
    
    const infoCount = parseResult.filter(entry => 
      entry.level && ['INFO', 'DEBUG'].includes(entry.level.toUpperCase())
    ).length

    // Generate real anomalies from the parsed data
    const anomalies: Anomaly[] = []
    
    // Error spike anomaly
    if (errorCount > 0) {
      const errorRate = errorCount / parseResult.length
      if (errorRate > 0.1) { // More than 10% errors
        anomalies.push({
          type: 'error_spike',
          severity: 'high',
          description: `High error rate detected: ${(errorRate * 100).toFixed(1)}% (${errorCount} errors)`,
          timestamp: new Date().toISOString(),
          details: {
            error_rate: errorRate,
            error_count: errorCount,
            total_entries: parseResult.length,
            threshold: '10%'
          }
        })
      }
    }

    // IP anomaly detection (if we have IP addresses)
    const ipAddresses = parseResult
      .filter(entry => entry.ip_address)
      .map(entry => entry.ip_address)
      .filter(Boolean)
    
    if (ipAddresses.length > 0) {
      const ipCounts = ipAddresses.reduce((acc, ip) => {
        acc[ip!] = (acc[ip!] || 0) + 1
        return acc
      }, {} as Record<string, number>)
      
      const suspiciousIPs = Object.entries(ipCounts)
        .filter(([, count]) => count > 100) // More than 100 requests from same IP
        .sort(([, a], [, b]) => b - a)
      
      if (suspiciousIPs.length > 0) {
        const [ip, count] = suspiciousIPs[0]
        anomalies.push({
          type: 'ip_anomaly',
          severity: 'medium',
          description: `Suspicious IP activity: ${ip} (${count} requests)`,
          timestamp: new Date().toISOString(),
          details: {
            ip_address: ip,
            total_requests: count,
            percentage: ((count / parseResult.length) * 100).toFixed(1) + '%'
          }
        })
      }
    }

    // Unusual pattern detection
    const messages = parseResult
      .filter(entry => entry.message)
      .map(entry => entry.message)
      .filter(Boolean)
    
    if (messages.length > 0) {
      const messageCounts = messages.reduce((acc, message) => {
        acc[message!] = (acc[message!] || 0) + 1
        return acc
      }, {} as Record<string, number>)
      
      const repeatedMessages = Object.entries(messageCounts)
        .filter(([, count]) => count > 10) // More than 10 occurrences
        .sort(([, a], [, b]) => b - a)
      
      if (repeatedMessages.length > 0) {
        const [message, count] = repeatedMessages[0]
        anomalies.push({
          type: 'unusual_pattern',
          severity: 'medium',
          description: `Repeated message pattern: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`,
          timestamp: new Date().toISOString(),
          details: {
            message: message,
            count: count,
            percentage: ((count / parseResult.length) * 100).toFixed(1) + '%'
          }
        })
      }
    }

    // Generate basic insights from the parsed data
    const insights = []
    if (errorCount > 0) insights.push(`${errorCount} error entries detected`)
    if (warningCount > 0) insights.push(`${warningCount} warning entries detected`)
    if (parseResult.length > 1000) insights.push('Large log file detected')
    if (anomalies.length > 0) insights.push(`${anomalies.length} anomalies detected`)
    
    const recommendations = []
    if (errorCount > 0) recommendations.push('Review error logs for system issues')
    if (warningCount > 0) recommendations.push('Monitor warning patterns')
    if (parseResult.length > 1000) recommendations.push('Consider log rotation for large files')
    if (anomalies.length > 0) recommendations.push('Investigate detected anomalies')

    return {
      total_entries: parseResult.length,
      anomalies,
      ai_summary: {
        summary: `Analyzed ${parseResult.length} log entries from ${uploadedFile.filename}`,
        insights,
        recommendations
      },
      statistics: {
        error_count: errorCount,
        warning_count: warningCount,
        info_count: infoCount
      }
    }
  }

  useEffect(() => {
    const fetchResults = async () => {
      console.log('Results page - location.state:', location.state)
      
      try {
        // Check if we have data passed from the Upload page
        const { uploadedFile, parseResult } = location.state || {}
        
        console.log('uploadedFile:', uploadedFile)
        console.log('parseResult:', parseResult)
        
        if (uploadedFile) {
          if (parseResult && parseResult.length > 0) {
            // Use real parsed data from the uploaded file
            console.log('Using real parsed data:', parseResult.length, 'entries')
            const realResult = createAnalysisResultFromParseResult(parseResult, uploadedFile)
            setAnalysisResult(realResult)
          } else if (uploadedFile.parse_result && uploadedFile.parse_result.length > 0) {
            // Use parse result from uploadedFile
            console.log('Using parse result from uploadedFile:', uploadedFile.parse_result.length, 'entries')
            const realResult = createAnalysisResultFromParseResult(uploadedFile.parse_result, uploadedFile)
            setAnalysisResult(realResult)
          } else {
            // File uploaded but no parsed data - create basic result
            console.log('File uploaded but no parsed data, creating basic result')
            const basicResult: AnalysisResult = {
              total_entries: 0,
              anomalies: [],
              ai_summary: {
                summary: `File ${uploadedFile.filename} was uploaded successfully but could not be parsed.`,
                insights: ['File upload completed', 'No log entries were parsed'],
                recommendations: ['Check if the log file format is supported', 'Verify the file is not empty or corrupted']
              },
              statistics: {
                error_count: 0,
                warning_count: 0,
                info_count: 0
              }
            }
            setAnalysisResult(basicResult)
          }
        } else {
          // No real data available - show error
          console.log('No uploadedFile found in location.state')
          setError('No log data available. Please upload a file first.')
        }
      } catch (err) {
        console.error('Error processing results:', err)
        setError('Failed to process analysis results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [location.state])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
  }

  const handleResolveAnomaly = (anomalyIndex: number) => {
    if (!analysisResult) return
    
    const anomaly = analysisResult.anomalies[anomalyIndex]
    const resolvedAnomaly = {
      ...anomaly,
      resolvedAt: new Date().toISOString()
    }
    
    // Add to resolved anomalies
    setResolvedAnomalies(prev => [...prev, resolvedAnomaly])
    
    // Remove from active anomalies
    const updatedAnomalies = analysisResult.anomalies.filter((_, index) => index !== anomalyIndex)
    setAnalysisResult(prev => prev ? { ...prev, anomalies: updatedAnomalies } : null)
  }

  const handleInvestigateAnomaly = (anomaly: any) => {
    setInvestigationModal({ isOpen: true, anomaly })
  }

  const handleDismissAnomaly = (anomaly: any) => {
    if (!analysisResult) return
    
    // Remove the anomaly from the list
    const updatedAnomalies = analysisResult.anomalies.filter(a => a !== anomaly)
    setAnalysisResult(prev => prev ? { ...prev, anomalies: updatedAnomalies } : null)
  }

  const handleViewLogs = (anomaly: any) => {
    if (!location.state?.parseResult) return
    
    let relevantLogs: LogEntry[] = []
    
    // Filter logs based on anomaly type
    switch (anomaly.type) {
      case 'error_spike':
        relevantLogs = location.state.parseResult.filter((entry: LogEntry) => 
          entry.level && ['ERROR', 'CRITICAL', 'FATAL'].includes(entry.level.toUpperCase())
        )
        break
      case 'ip_anomaly':
        if (anomaly.details?.ip_address) {
          relevantLogs = location.state.parseResult.filter((entry: LogEntry) => 
            entry.ip_address === anomaly.details.ip_address
          )
        }
        break
      case 'unusual_pattern':
        if (anomaly.details?.message) {
          relevantLogs = location.state.parseResult.filter((entry: LogEntry) => 
            entry.message === anomaly.details.message
          )
        }
        break
      default:
        relevantLogs = location.state.parseResult.slice(0, 50) // Show first 50 logs for unknown types
    }
    
    setViewLogsModal({ isOpen: true, anomaly, logs: relevantLogs })
  }

  const closeInvestigationModal = () => {
    setInvestigationModal({ isOpen: false, anomaly: null })
  }

  const closeViewLogsModal = () => {
    setViewLogsModal({ isOpen: false, anomaly: null, logs: [] })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!analysisResult) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/upload')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Analysis Results</h1>
            </div>
            <button
              onClick={handleSignOut}
              className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0 space-y-6">
          {/* File Selection */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Log File Analysis</h3>
                <p className="text-sm text-gray-600">Select a log file to analyze</p>
              </div>
              <div className="flex items-center space-x-4">
                <select
                  value={selectedFile}
                  onChange={(e) => setSelectedFile(e.target.value)}
                  className="block w-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a log file...</option>
                  {location.state?.uploadedFile && (
                    <option value={location.state.uploadedFile.filename}>
                      {location.state.uploadedFile.filename}
                    </option>
                  )}
                </select>
                <button
                  onClick={() => navigate('/upload')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Upload New File
                </button>
              </div>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Info className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Entries
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analysisResult.total_entries.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Errors
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analysisResult.statistics.error_count.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Warnings
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analysisResult.statistics.warning_count.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Info
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {analysisResult.statistics.info_count.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Anomalies Section */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Detected Anomalies ({analysisResult.anomalies.length})
              </h3>
              <div className="space-y-4">
                {analysisResult.anomalies.map((anomaly, index) => (
                  <AnomalyHighlight
                    key={index}
                    anomaly={anomaly}
                    onInvestigate={handleInvestigateAnomaly}
                    onDismiss={handleDismissAnomaly}
                    onViewLogs={handleViewLogs}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Resolved Anomalies Section */}
          {resolvedAnomalies.length > 0 && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Resolved Anomalies ({resolvedAnomalies.length})
                </h3>
                <div className="space-y-4">
                  {resolvedAnomalies.map((anomaly, index) => (
                    <div key={index} className="border border-green-200 rounded-lg p-4 bg-green-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            <span className="text-sm font-medium text-green-800">
                              {anomaly.type.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                              anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {anomaly.severity}
                            </span>
                          </div>
                          <p className="text-sm text-green-700 mb-2">{anomaly.description}</p>
                          <p className="text-xs text-green-600">
                            Resolved at: {new Date(anomaly.resolvedAt).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* AI Summary */}
          {analysisResult.ai_summary && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  AI Analysis Summary
                </h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Summary</h4>
                    <p className="mt-1 text-sm text-gray-900">
                      {analysisResult.ai_summary.summary}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Key Insights</h4>
                    <ul className="mt-1 space-y-1">
                      {analysisResult.ai_summary.insights.map((insight, index) => (
                        <li key={index} className="text-sm text-gray-900 flex items-center">
                          <Info className="h-4 w-4 text-blue-500 mr-2" />
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Recommendations</h4>
                    <ul className="mt-1 space-y-1">
                      {analysisResult.ai_summary.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-900 flex items-center">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Parsed Log Entries Preview */}
          {location.state?.parseResult ? (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Parsed Log Entries Preview
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Line
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Level
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Message
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Format
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                                            {location.state.parseResult.slice(0, 10).map((entry: LogEntry, index: number) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {entry.line_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              entry.level?.toUpperCase() === 'ERROR' ? 'bg-red-100 text-red-800' :
                              entry.level?.toUpperCase() === 'WARNING' || entry.level?.toUpperCase() === 'WARN' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {entry.level || 'INFO'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                            {entry.message}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {entry.format}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {location.state.parseResult.length > 10 && (
                    <div className="mt-4 text-center text-sm text-gray-500">
                      Showing first 10 of {location.state.parseResult.length} entries
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="text-center text-gray-500">
                  <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p>No parsed log data available. Upload a file first to see the analysis results.</p>
                </div>
              </div>
            </div>
          )}

          {/* Timeline Chart */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Log Activity Timeline
              </h3>
              <TimelineChart data={{
                ...analysisResult,
                parseResult: location.state?.parseResult || []
              }} />
            </div>
          </div>

          {/* Detailed Results Table */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Detailed Analysis
              </h3>
              <ResultsTable 
                data={analysisResult} 
                onResolveAnomaly={handleResolveAnomaly}
                onInvestigateAnomaly={handleInvestigateAnomaly}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Investigation Modal */}
      {investigationModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Anomaly Investigation
                </h3>
                <button
                  onClick={closeInvestigationModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {investigationModal.anomaly && (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Type</h4>
                    <p className="mt-1 text-sm text-gray-900 capitalize">
                      {investigationModal.anomaly.type.replace('_', ' ')}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Severity</h4>
                    <p className="mt-1 text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        investigationModal.anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                        investigationModal.anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {investigationModal.anomaly.severity}
                      </span>
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Description</h4>
                    <p className="mt-1 text-sm text-gray-900">
                      {investigationModal.anomaly.description}
                    </p>
                  </div>
                  
                  {investigationModal.anomaly.timestamp && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Timestamp</h4>
                      <p className="mt-1 text-sm text-gray-900">
                        {new Date(investigationModal.anomaly.timestamp).toLocaleString()}
                      </p>
                    </div>
                  )}
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Details</h4>
                    <div className="mt-1 bg-gray-50 rounded-md p-3">
                      <pre className="text-sm text-gray-900 whitespace-pre-wrap">
                        {JSON.stringify(investigationModal.anomaly.details, null, 2)}
                      </pre>
                    </div>
                  </div>
                  
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      onClick={closeInvestigationModal}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* View Logs Modal */}
      {viewLogsModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Logs Related to Anomaly: {viewLogsModal.anomaly?.type.replace('_', ' ').toUpperCase()}
                </h3>
                <button
                  onClick={closeViewLogsModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Showing {viewLogsModal.logs.length} relevant log entries for this anomaly.
                </p>
              </div>
              
              <div className="overflow-x-auto max-h-96">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Line
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Level
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Timestamp
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Message
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {viewLogsModal.logs.map((entry: LogEntry, index: number) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.line_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            entry.level?.toUpperCase() === 'ERROR' ? 'bg-red-100 text-red-800' :
                            entry.level?.toUpperCase() === 'WARNING' || entry.level?.toUpperCase() === 'WARN' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {entry.level || 'INFO'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.timestamp || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.ip_address || 'N/A'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                          <div className="truncate" title={entry.message}>
                            {entry.message}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="flex justify-end pt-4">
                <button
                  onClick={closeViewLogsModal}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
