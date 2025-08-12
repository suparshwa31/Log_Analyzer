import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabaseClient'
import { ArrowLeft, AlertTriangle, Info, CheckCircle, Upload, RefreshCw, ChevronDown, ChevronRight } from 'lucide-react'
import ResultsTable from '../components/ResultsTable'
import TimelineChart from '../components/TimelineChart'
import AnomalyHighlight from '../components/AnomalyHighlight'
import { uploadAPI, analysisAPI } from '../lib/api'
import type { LogEntry, AnalysisResult, Anomaly, FileInfo } from '../lib/schemas'

export default function Results() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<FileInfo[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [selectedFile, setSelectedFile] = useState<string>('')
  const [fileSelectionError, setFileSelectionError] = useState('')
  const [currentParseResult, setCurrentParseResult] = useState<LogEntry[]>([])
  const [resolvedAnomalies, setResolvedAnomalies] = useState<Array<{
    type: string
    severity: string
    description: string
    timestamp?: string
    details: any
    resolvedAt: string
  }>>([])
  const [investigationModal, setInvestigationModal] = useState<{
    isOpen: boolean
    anomaly: any
  }>({ isOpen: false, anomaly: null })
  const [viewLogsModal, setViewLogsModal] = useState<{
    isOpen: boolean
    anomaly: any
    logs: LogEntry[]
  }>({ isOpen: false, anomaly: null, logs: [] })
  
  // Collapsible sections state
  const [collapsedSections, setCollapsedSections] = useState<{
    summary: boolean
    anomalies: boolean
    resolved: boolean
    aiSummary: boolean
    timeline: boolean
    detailedAnalysis: boolean
  }>({
    summary: false,
    anomalies: false,
    resolved: true, // Start collapsed
    aiSummary: false,
    timeline: false,
    detailedAnalysis: false
  })
  
  const navigate = useNavigate()

  // Load files and auto-select first file on component mount
  useEffect(() => {
    const loadFilesAndAnalyze = async () => {
      try {
        setLoading(true)
        
        // Load uploaded files
        const fileList = await uploadAPI.listFiles()
        setUploadedFiles(fileList.files)
        
        if (fileList.files.length > 0) {
          // Auto-select first file
          const firstFile = fileList.files[0]
          setSelectedFile(firstFile.filename)
          
          // Auto-analyze first file with fileInfo from the list
          await analyzeFileWithInfo(firstFile)
        } else {
          setError('No log files found. Please upload a file first.')
        }
      } catch (err: any) {
        if (err.response?.status === 401) {
          navigate('/login')
        } else {
          setError('Failed to load files. Please try again.')
        }
      } finally {
        setLoading(false)
      }
    }

    loadFilesAndAnalyze()
  }, [navigate])

  const analyzeFileWithInfo = async (fileInfo: FileInfo) => {
    try {
      setAnalyzing(true)
      setError('')
      setAnalysisResult(null) // Reset analysis result while analyzing
      
      const filePath = fileInfo.path || `/uploads/${fileInfo.filename}`
      const analysisData = await analysisAPI.analyzeLogs(filePath)
      setAnalysisResult(analysisData)
      setCurrentParseResult([]) // Reset parse result since we're using analysis from API
      setResolvedAnomalies([]) // Clear resolved anomalies for new file
      
    } catch (err: any) {
      
      // Handle different types of errors
      let errorMessage = 'Unknown error occurred'
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Analysis timed out after 2 minutes. The log file may be too large or complex to analyze quickly. Please try with a smaller file or contact support.'
      } else if (err.response?.status === 413) {
        errorMessage = 'Log file is too large to analyze. Please try with a smaller file.'
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error occurred during analysis. Please try again or contact support.'
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(`Failed to analyze file: ${errorMessage}`)
      setAnalysisResult(null) // Ensure analysis result is null on error
    } finally {
      setAnalyzing(false)
    }
  }

  const analyzeFile = async (filename: string) => {
    if (!filename) return

    const selectedFileInfo = uploadedFiles.find(f => f.filename === filename)
    if (!selectedFileInfo) {
      setError('File not found')
      return
    }

    await analyzeFileWithInfo(selectedFileInfo)
  }

  const handleFileSelection = (filename: string) => {
    // Clear any previous file selection errors
    setFileSelectionError('')
    setError('')
    
    // If user selects empty option, show error
    if (!filename) {
      setFileSelectionError('Please select a log file to analyze.')
      setSelectedFile('')
      setAnalysisResult(null)
      return
    }
    
    // If same file is selected again, no need to re-analyze
    if (filename === selectedFile) return
    
    setSelectedFile(filename)
    analyzeFile(filename)
  }

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
    
    setResolvedAnomalies(prev => [...prev, resolvedAnomaly])
    
    const updatedAnomalies = analysisResult.anomalies.filter((_, index) => index !== anomalyIndex)
    setAnalysisResult(prev => prev ? { ...prev, anomalies: updatedAnomalies } : null)
  }

  const handleInvestigateAnomaly = (anomaly: any) => {
    setInvestigationModal({ isOpen: true, anomaly })
  }

  const handleDismissAnomaly = (anomaly: any) => {
    if (!analysisResult) return
    
    const updatedAnomalies = analysisResult.anomalies.filter(a => a !== anomaly)
    setAnalysisResult(prev => prev ? { ...prev, anomalies: updatedAnomalies } : null)
  }

  const handleViewLogs = (anomaly: any) => {
    // For now, show empty logs since we removed location.state dependency
    // In a real implementation, you would fetch logs related to this anomaly
    setViewLogsModal({ isOpen: true, anomaly, logs: [] })
  }

  const closeInvestigationModal = () => {
    setInvestigationModal({ isOpen: false, anomaly: null })
  }

  const closeViewLogsModal = () => {
    setViewLogsModal({ isOpen: false, anomaly: null, logs: [] })
  }

  const toggleSection = (section: keyof typeof collapsedSections) => {
    setCollapsedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
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
          <div className="space-x-4">
            <button
              onClick={() => navigate('/upload')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Upload Files
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!analysisResult && !analyzing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Analysis Available</h2>
          <p className="text-gray-600 mb-4">Please upload a log file to see analysis results.</p>
          <button
            onClick={() => navigate('/upload')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Upload Files
          </button>
        </div>
      </div>
    )
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
                  onChange={(e) => handleFileSelection(e.target.value)}
                  className={`block w-64 px-3 py-2 border rounded-md shadow-sm focus:outline-none ${
                    fileSelectionError 
                      ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                  }`}
                  disabled={analyzing}
                >
                  <option value="">Select a log file...</option>
                  {uploadedFiles.map((file) => (
                    <option key={file.filename} value={file.filename}>
                      {file.filename} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </option>
                  ))}
                </select>
                {analyzing && (
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />
                    <span className="text-sm text-blue-600">Analyzing...</span>
                  </div>
                )}
                <button
                  onClick={() => navigate('/upload')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  disabled={analyzing}
                >
                  Upload New File
                </button>
              </div>
            </div>
            
            {/* File Selection Error Display */}
            {fileSelectionError && (
              <div className="mt-4 flex items-center space-x-2 text-red-600">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm font-medium">{fileSelectionError}</span>
              </div>
            )}
          </div>

          {analyzing ? (
            <div className="bg-white shadow rounded-lg p-6 text-center">
              <RefreshCw className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Analyzing Log File</h3>
              <p className="text-gray-600">Please wait while we analyze your log file...</p>
            </div>
          ) : fileSelectionError ? (
            <div className="bg-white shadow rounded-lg p-6 text-center">
              <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Please Select a Log File</h3>
              <p className="text-gray-600 mb-4">Choose a log file from the dropdown above to view analysis results.</p>
              <button
                onClick={() => {
                  setFileSelectionError('')
                  if (uploadedFiles.length > 0) {
                    handleFileSelection(uploadedFiles[0].filename)
                  }
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 mr-2"
              >
                {uploadedFiles.length > 0 ? 'Analyze First File' : 'No Files Available'}
              </button>
              <button
                onClick={() => navigate('/upload')}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Upload New File
              </button>
            </div>
          ) : analysisResult && analysisResult.total_entries !== undefined && analysisResult.statistics ? (
            <>
              {/* Summary Statistics */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Summary Statistics
                    </h3>
                    <button
                      onClick={() => toggleSection('summary')}
                      className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                    >
                      {collapsedSections.summary ? (
                        <ChevronRight className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {!collapsedSections.summary && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <div className="bg-gray-50 overflow-hidden rounded-lg">
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
                                  {(analysisResult.total_entries || 0).toLocaleString()}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 overflow-hidden rounded-lg">
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
                                  {(analysisResult.statistics?.error_count || 0).toLocaleString()}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 overflow-hidden rounded-lg">
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
                                  {(analysisResult.statistics?.warning_count || 0).toLocaleString()}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 overflow-hidden rounded-lg">
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
                                  {(analysisResult.statistics?.info_count || 0).toLocaleString()}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Anomalies Section */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Detected Anomalies ({analysisResult.anomalies?.length || 0})
                    </h3>
                    <button
                      onClick={() => toggleSection('anomalies')}
                      className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                    >
                      {collapsedSections.anomalies ? (
                        <ChevronRight className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {!collapsedSections.anomalies && (
                    <div className="space-y-4">
                      {analysisResult.anomalies && analysisResult.anomalies.length > 0 ? (
                        analysisResult.anomalies.map((anomaly, index) => (
                          <AnomalyHighlight
                            key={index}
                            anomaly={anomaly}
                            onInvestigate={handleInvestigateAnomaly}
                            onDismiss={handleDismissAnomaly}
                            onViewLogs={handleViewLogs}
                          />
                        ))
                      ) : (
                        <p className="text-gray-500 text-center py-8">No anomalies detected in this log file.</p>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Resolved Anomalies Section */}
              {resolvedAnomalies.length > 0 && (
                <div className="bg-white shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg leading-6 font-medium text-gray-900">
                        Resolved Anomalies ({resolvedAnomalies.length})
                      </h3>
                      <button
                        onClick={() => toggleSection('resolved')}
                        className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                      >
                        {collapsedSections.resolved ? (
                          <ChevronRight className="h-5 w-5" />
                        ) : (
                          <ChevronDown className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                    {!collapsedSections.resolved && (
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
                    )}
                  </div>
                </div>
              )}

              {/* AI Summary */}
              {analysisResult.ai_summary && (
                <div className="bg-white shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg leading-6 font-medium text-gray-900">
                        Analysis Summary
                      </h3>
                      <button
                        onClick={() => toggleSection('aiSummary')}
                        className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                      >
                        {collapsedSections.aiSummary ? (
                          <ChevronRight className="h-5 w-5" />
                        ) : (
                          <ChevronDown className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                    {!collapsedSections.aiSummary && (
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
                    )}
                  </div>
                </div>
              )}

              {/* Timeline Chart */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Log Activity Timeline
                    </h3>
                    <button
                      onClick={() => toggleSection('timeline')}
                      className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                    >
                      {collapsedSections.timeline ? (
                        <ChevronRight className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {!collapsedSections.timeline && (
                    <TimelineChart data={{
                      ...analysisResult,
                      parseResult: currentParseResult
                    }} />
                  )}
                </div>
              </div>

              {/* Detailed Results Table */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Detailed Analysis
                    </h3>
                    <button
                      onClick={() => toggleSection('detailedAnalysis')}
                      className="p-1 rounded-md text-gray-400 hover:text-gray-600"
                    >
                      {collapsedSections.detailedAnalysis ? (
                        <ChevronRight className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {!collapsedSections.detailedAnalysis && analysisResult.anomalies && (
                    <ResultsTable 
                      data={analysisResult} 
                      onResolveAnomaly={handleResolveAnomaly}
                      onInvestigateAnomaly={handleInvestigateAnomaly}
                    />
                  )}
                </div>
              </div>
            </>
          ) : null}
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
                  {viewLogsModal.logs.length > 0 
                    ? `Showing ${viewLogsModal.logs.length} relevant log entries for this anomaly.`
                    : 'No specific log entries available for this anomaly.'
                  }
                </p>
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
