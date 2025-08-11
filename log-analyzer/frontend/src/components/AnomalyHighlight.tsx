import { AlertTriangle, Clock, Info, AlertCircle, Eye, X } from 'lucide-react'

interface AnomalyHighlightProps {
  anomaly: {
    type: string
    severity: string
    description: string
    timestamp?: string
    details: any
  }
  onInvestigate: (anomaly: any) => void
  onDismiss: (anomaly: any) => void
  onViewLogs: (anomaly: any) => void
}

export default function AnomalyHighlight({ 
  anomaly, 
  onInvestigate, 
  onDismiss, 
  onViewLogs 
}: AnomalyHighlightProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      case 'low':
        return <Info className="h-5 w-5 text-blue-500" />
      default:
        return <Info className="h-5 w-5 text-gray-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'border-red-200 bg-red-50'
      case 'medium':
        return 'border-yellow-200 bg-yellow-50'
      case 'low':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const getSeverityBadgeColor = (severity: string) => {
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

  const formatAnomalyType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  const renderDetails = (details: any) => {
    if (!details || typeof details !== 'object') {
      return null
    }

    return (
      <div className="mt-3 pt-3 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Details</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(details).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-sm font-medium text-gray-600 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <span className="text-sm text-gray-900">
                {typeof value === 'number' 
                  ? value.toLocaleString() 
                  : typeof value === 'string' && value.includes('%')
                    ? value
                    : String(value)
                }
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className={`border rounded-lg p-4 ${getSeverityColor(anomaly.severity)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 mt-1">
            {getSeverityIcon(anomaly.severity)}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityBadgeColor(anomaly.severity)}`}>
                {anomaly.severity.toUpperCase()}
              </span>
              <span className="inline-flex px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded-full">
                {formatAnomalyType(anomaly.type)}
              </span>
            </div>
            
            <p className="text-sm font-medium text-gray-900 mb-2">
              {anomaly.description}
            </p>
            
            {anomaly.timestamp && (
              <div className="flex items-center text-xs text-gray-500">
                <Clock className="h-3 w-3 mr-1" />
                {formatTimestamp(anomaly.timestamp)}
              </div>
            )}
            
            {renderDetails(anomaly.details)}
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button 
            onClick={() => onViewLogs(anomaly)}
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <Eye className="h-3 w-3 mr-1" />
            View Logs
          </button>
          <button 
            onClick={() => onInvestigate(anomaly)}
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Info className="h-3 w-3 mr-1" />
            Investigate
          </button>
          <button 
            onClick={() => onDismiss(anomaly)}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            <X className="h-3 w-3 mr-1" />
            Dismiss
          </button>
        </div>
      </div>
    </div>
  )
}
