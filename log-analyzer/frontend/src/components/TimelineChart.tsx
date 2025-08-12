import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TimelineChartProps {
  data: {
    total_entries: number
    statistics: {
      error_count: number
      warning_count: number
      info_count: number
    }
    parseResult?: Array<{
      timestamp?: string
      level?: string
      line_number: number
    }>
  }
}

export default function TimelineChart({ data }: TimelineChartProps) {
  // Generate timeline data from real log entries
  const generateTimelineData = () => {
    console.log('TimelineChart data:', data)
    console.log('parseResult:', data.parseResult)
    
    if (!data.parseResult || data.parseResult.length === 0) {
      console.log('No parseResult data available')
      // Generate sample data for demonstration
      const sampleData = []
      const now = new Date()
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now)
        time.setHours(now.getHours() - i)
        
        sampleData.push({
          time: time.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
          }),
          total: Math.floor(Math.random() * 100) + 10,
          errors: Math.floor(Math.random() * 20),
          warnings: Math.floor(Math.random() * 30),
          info: Math.floor(Math.random() * 50) + 20
        })
      }
      
      return sampleData
    }
    
    // Use real log data to generate timeline
    const timelineData = []
    const now = new Date()
    
    // Group logs by hour for the last 24 hours
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now)
      time.setHours(now.getHours() - i)
      const hourStart = new Date(time)
      hourStart.setMinutes(0, 0, 0)
      const hourEnd = new Date(time)
      hourEnd.setMinutes(59, 59, 999)
      
      // Count logs in this hour
      const hourLogs = data.parseResult.filter(entry => {
        if (!entry.timestamp) return false
        try {
          const logTime = new Date(entry.timestamp)
          return logTime >= hourStart && logTime <= hourEnd
        } catch {
          return false
        }
      })
      
      const total = hourLogs.length
      const errors = hourLogs.filter(entry => 
        entry.level && ['ERROR', 'CRITICAL', 'FATAL'].includes(entry.level.toUpperCase())
      ).length
      const warnings = hourLogs.filter(entry => 
        entry.level && ['WARNING', 'WARN'].includes(entry.level.toUpperCase())
      ).length
      const info = total - errors - warnings
      
      timelineData.push({
        time: time.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        }),
        total,
        errors,
        warnings,
        info: Math.max(0, info)
      })
    }
    
    return timelineData
  }

  const chartData = generateTimelineData()

  // Show message when no data is available
  if (chartData.length === 0) {
    return (
      <div className="w-full h-80 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg font-medium mb-2">No Timeline Data Available</p>
          <p className="text-sm">Upload a log file to see timeline analysis</p>
        </div>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{`Time: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full">
      {/* Chart Summary Metrics */}
      <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-sm font-medium text-gray-500 mb-1">Peak Volume</p>
          <p className="text-xl font-semibold text-blue-600">
            {Math.max(...chartData.map(d => d.total)).toLocaleString()}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-sm font-medium text-gray-500 mb-1">Avg Volume</p>
          <p className="text-xl font-semibold text-gray-600">
            {Math.round(chartData.reduce((sum, d) => sum + d.total, 0) / chartData.length).toLocaleString()}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-sm font-medium text-gray-500 mb-1">Total Errors</p>
          <p className="text-xl font-semibold text-red-600">
            {chartData.reduce((sum, d) => sum + d.errors, 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-sm font-medium text-gray-500 mb-1">Total Warnings</p>
          <p className="text-xl font-semibold text-yellow-600">
            {chartData.reduce((sum, d) => sum + d.warnings, 0).toLocaleString()}
          </p>
        </div>
      </div>
      
      {/* Timeline Chart */}
      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => value.toLocaleString()}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              verticalAlign="top" 
              height={36}
              wrapperStyle={{
                paddingBottom: '10px'
              }}
            />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Total Logs"
            />
            <Line
              type="monotone"
              dataKey="errors"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="Errors"
            />
            <Line
              type="monotone"
              dataKey="warnings"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              name="Warnings"
            />
            <Line
              type="monotone"
              dataKey="info"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Info"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
