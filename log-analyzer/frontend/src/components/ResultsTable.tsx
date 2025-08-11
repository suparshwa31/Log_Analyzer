import { useState } from 'react'
import { ChevronDown, ChevronRight, AlertTriangle, Info, CheckCircle } from 'lucide-react'
import type { AnalysisResult, Anomaly } from '../lib/schemas'

interface ResultsTableProps {
  data: AnalysisResult
  onResolveAnomaly?: (index: number) => void
  onInvestigateAnomaly?: (anomaly: Anomaly) => void
}

export default function ResultsTable({ data, onResolveAnomaly, onInvestigateAnomaly }: ResultsTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRows(newExpanded)
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'low':
        return <Info className="h-4 w-4 text-blue-500" />
      default:
        return <Info className="h-4 w-4 text-gray-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }

  const renderDetails = (details: any) => {
    if (!details || typeof details !== 'object') {
      return <span className="text-gray-500">No details available</span>
    }

    return (
      <div className="space-y-2">
        {Object.entries(details).map(([key, value]) => (
          <div key={key} className="flex">
            <span className="font-medium text-gray-700 w-24">{key}:</span>
            <span className="text-gray-900">
              {typeof value === 'number' ? value.toLocaleString() : String(value)}
            </span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Anomaly
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.anomalies.length > 0 ? (
              data.anomalies.map((anomaly, index) => (
              <>
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <button
                        onClick={() => toggleRow(index)}
                        className="mr-2 text-gray-400 hover:text-gray-600"
                      >
                        {expandedRows.has(index) ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </button>
                      <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                        {anomaly.description}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 capitalize">
                      {anomaly.type.replace('_', ' ')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getSeverityIcon(anomaly.severity)}
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(anomaly.severity)}`}>
                        {anomaly.severity}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {anomaly.timestamp ? formatTimestamp(anomaly.timestamp) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      {onInvestigateAnomaly && (
                        <button 
                          onClick={() => onInvestigateAnomaly(anomaly)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Investigate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
                {expandedRows.has(index) && (
                  <tr key={`expanded-${index}`}>
                    <td colSpan={5} className="px-6 py-4 bg-gray-50">
                      <div className="space-y-3">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Details</h4>
                          {renderDetails(anomaly.details)}
                        </div>
                        <div className="flex space-x-2">
                          <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700">
                            <Info className="h-3 w-3 mr-1" />
                            View Logs
                          </button>
                          {onResolveAnomaly && (
                            <button 
                              onClick={() => onResolveAnomaly(index)}
                              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                            >
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Mark Resolved
                            </button>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))
            ) : (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                  <div className="py-8">
                    <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p>No anomalies detected in this log file.</p>
                    <p className="text-sm text-gray-400 mt-2">This is usually a good sign!</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Summary Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <div>
              <p className="text-sm font-medium text-gray-500">Total Anomalies</p>
              <p className="text-lg font-semibold text-gray-900">{data.anomalies.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center">
            <Info className="h-5 w-5 text-blue-500 mr-2" />
            <div>
              <p className="text-sm font-medium text-gray-500">Log Entries</p>
              <p className="text-lg font-semibold text-gray-900">{data.total_entries.toLocaleString()}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <div>
              <p className="text-sm font-medium text-gray-500">Error Rate</p>
              <p className="text-lg font-semibold text-gray-900">
                {((data.statistics.error_count / data.total_entries) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
