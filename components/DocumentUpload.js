import { useState, useCallback } from 'react'

export default function DocumentUpload({ onDocumentUpload, uploadedDocument }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadError, setUploadError] = useState('')

  // Helper function to convert file to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result)
      reader.onerror = (error) => reject(error)
    })
  }

  // Helper function to read file as text
  const fileToText = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsText(file)
      reader.onload = () => resolve(reader.result)
      reader.onerror = (error) => reject(error)
    })
  }

  const handleFileUpload = useCallback(async (file) => {
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'message/rfc822']
    const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt', '.eml']
    
    const isValidType = allowedTypes.includes(file.type) || 
                       allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    
    if (!isValidType) {
      setUploadError('Unsupported file type. Please upload PDF, Word, Text, or Email files.')
      return
    }

    // Validate file size (max 10MB for client-side processing)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File too large. Please upload files smaller than 10MB.')
      return
    }

    setIsUploading(true)
    setUploadError('')
    setUploadProgress(10)

    try {
      // Convert file to base64 for API
      const base64Data = await fileToBase64(file)
      setUploadProgress(30)

      // Also read as text for local processing (fallback)
      let textContent = ''
      try {
        if (file.type === 'text/plain') {
          textContent = await fileToText(file)
        }
      } catch (textError) {
        console.log('Text reading failed, will rely on server processing')
      }

      setUploadProgress(50)

      // Call the upload API
      const uploadData = {
        file_content: base64Data,
        file_name: file.name,
        document_name: file.name
      }

      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(uploadData)
      })

      setUploadProgress(80)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Upload failed')
      }

      const result = await response.json()
      setUploadProgress(100)

      // Prepare document data for parent component
      const documentData = {
        id: result.document_id,
        name: result.document_name,
        size: file.size,
        type: file.type,
        uploadTime: result.timestamp,
        processingTime: result.processing_time,
        statistics: result.document_analysis,
        capabilities: result.capabilities
      }

      // Use server-processed content or fallback to client text
      const documentContent = result.document_analysis?.content_preview || textContent

      // Call parent callback
      onDocumentUpload(documentData, documentContent)

      // Reset progress after a short delay
      setTimeout(() => {
        setUploadProgress(0)
        setIsUploading(false)
      }, 1000)

    } catch (error) {
      console.error('Upload error:', error)
      setUploadError(error.message)
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [onDocumentUpload])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }, [handleFileUpload])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileInput = useCallback((e) => {
    const files = Array.from(e.target.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }, [handleFileUpload])

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
          isDragOver
            ? 'border-indigo-500 bg-indigo-50'
            : uploadedDocument
            ? 'border-green-300 bg-green-50'
            : 'border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Processing document...</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">{uploadProgress}% complete</p>
            </div>
          </div>
        ) : uploadedDocument ? (
          <div className="space-y-3">
            <div className="text-4xl">✅</div>
            <h4 className="text-lg font-semibold text-green-700">Document Uploaded Successfully!</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>File:</strong> {uploadedDocument.name}</p>
              <p><strong>Size:</strong> {(uploadedDocument.size / 1024).toFixed(1)} KB</p>
              <p><strong>Processing Time:</strong> {uploadedDocument.processingTime}</p>
              {uploadedDocument.statistics && (
                <p><strong>Content:</strong> {uploadedDocument.statistics.chunk_count} chunks, {uploadedDocument.statistics.character_count.toLocaleString()} characters</p>
              )}
            </div>
            <button
              onClick={() => {
                onDocumentUpload(null, '')
                setUploadError('')
              }}
              className="mt-4 px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Upload New Document
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl">📄</div>
            <div>
              <h4 className="text-lg font-semibold text-gray-700">
                Drop your document here
              </h4>
              <p className="text-gray-500 mt-1">
                or click to browse files
              </p>
            </div>
            <div className="text-sm text-gray-400">
              <p>Supported formats: PDF • Word (.docx) • Text (.txt) • Email (.eml)</p>
              <p>Maximum file size: 10MB</p>
            </div>
          </div>
        )}

        {/* Hidden file input */}
        <input
          type="file"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".pdf,.docx,.doc,.txt,.eml"
          onChange={handleFileInput}
          disabled={isUploading}
        />
      </div>

      {/* Error Display */}
      {uploadError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-400 mr-3">❌</div>
            <div>
              <h4 className="text-sm font-medium text-red-800">Upload Error</h4>
              <p className="text-sm text-red-600 mt-1">{uploadError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Upload Tips */}
      {!uploadedDocument && !isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-blue-400 mr-3">💡</div>
            <div>
              <h4 className="text-sm font-medium text-blue-800">Upload Tips</h4>
              <ul className="text-sm text-blue-600 mt-1 space-y-1">
                <li>• Insurance policies and contracts work best</li>
                <li>• Clear, text-based documents provide better analysis</li>
                <li>• Scanned images may have limited functionality</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}