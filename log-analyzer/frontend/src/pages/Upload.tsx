import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabaseClient'
import { Upload as UploadIcon, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import FileUploader from '../components/FileUploader'
import { uploadAPI } from '../lib/api'
import type { UploadResponse } from '../lib/schemas'

export default function Upload() {
  const [uploadedFiles, setUploadedFiles] = useState<Array<{
    name: string
    size: number
    status: 'uploading' | 'success' | 'error'
    message?: string
    uploadResponse?: UploadResponse
  }>>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const navigate = useNavigate()

  const handleFileUpload = async (files: FileList) => {
    const newFiles = Array.from(files).map(file => ({
      name: file.name,
      size: file.size,
      status: 'uploading' as const,
      message: 'Uploading...'
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const fileIndex = uploadedFiles.length + i

      try {
        // Upload file using the API
        const result = await uploadAPI.uploadFile(file)
        
        setUploadedFiles(prev => prev.map((f, idx) => 
          idx === fileIndex 
            ? { 
                ...f, 
                status: 'success', 
                message: 'Upload successful',
                uploadResponse: result
              }
            : f
        ))
      } catch (error) {
        console.error('Upload failed:', error)
        setUploadedFiles(prev => prev.map((f, idx) => 
          idx === fileIndex 
            ? { ...f, status: 'error', message: 'Upload failed' }
            : f
        ))
      }
    }
  }

  const handleAnalyze = async () => {
    const successfulUploads = uploadedFiles.filter(f => f.status === 'success')
    if (successfulUploads.length === 0) {
      return
    }

    setIsAnalyzing(true)
    
    try {
      // Get the first successful upload for analysis
      const firstUpload = successfulUploads[0]
      if (firstUpload.uploadResponse) {
        // Navigate to results page with the uploaded file data
        navigate('/results', { 
          state: { 
            uploadedFile: firstUpload.uploadResponse,
            parseResult: firstUpload.uploadResponse.parse_result
          } 
        })
      } else {
        navigate('/results')
      }
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
  }

  const successfulUploads = uploadedFiles.filter(f => f.status === 'success')
  const hasSuccessfulUploads = successfulUploads.length > 0

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Log Analyzer</h1>
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
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="mb-6">
              <h2 className="text-lg font-medium text-gray-900 mb-2">
                Upload Log Files
              </h2>
              <p className="text-sm text-gray-600">
                Upload your log files to analyze them for anomalies and insights.
                Supported formats: .log, .txt, .gz, .tar
              </p>
            </div>

            <FileUploader onFileUpload={handleFileUpload} />

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="mt-6">
                <h3 className="text-md font-medium text-gray-900 mb-3">
                  Uploaded Files
                </h3>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                    >
                      <div className="flex items-center">
                        <FileText className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        {file.status === 'uploading' && (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        )}
                        {file.status === 'success' && (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        )}
                        {file.status === 'error' && (
                          <AlertCircle className="h-5 w-5 text-red-500" />
                        )}
                        <span className={`ml-2 text-sm ${
                          file.status === 'success' ? 'text-green-600' :
                          file.status === 'error' ? 'text-red-600' :
                          'text-blue-600'
                        }`}>
                          {file.message}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analyze Button */}
            {hasSuccessfulUploads && (
              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <UploadIcon className="h-4 w-4 mr-2" />
                      Analyze Logs
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
