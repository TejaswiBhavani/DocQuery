import { useState } from 'react'

export default function QueryInterface({ documentContent, uploadedDocument }) {
  const [query, setQuery] = useState('')
  const [useLocalAI, setUseLocalAI] = useState(true)
  const [openaiApiKey, setOpenaiApiKey] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisError, setAnalysisError] = useState('')

  // Example queries for user convenience
  const exampleQueries = [
    "46M, knee surgery in Pune, 3-month policy",
    "35-year-old female, heart surgery in Mumbai, 1-year insurance",
    "Male patient, dental treatment, Bangalore, 6-month coverage",
    "Pre-existing condition coverage for diabetes patient",
    "Emergency treatment coverage outside network hospital"
  ]

  const handleQuerySubmit = async (e) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setAnalysisError('Please enter a query to analyze')
      return
    }

    if (!useLocalAI && !openaiApiKey.trim()) {
      setAnalysisError('Please enter your OpenAI API key or switch to Local AI')
      return
    }

    setIsAnalyzing(true)
    setAnalysisError('')
    setAnalysisResult(null)

    try {
      const analysisData = {
        query: query.trim(),
        document_text: documentContent || '',
        document_id: uploadedDocument?.id || 'no-document',
        use_local_ai: useLocalAI,
        openai_api_key: useLocalAI ? '' : openaiApiKey
      }

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const result = await response.json()
      setAnalysisResult(result)

    } catch (error) {
      console.error('Analysis error:', error)
      setAnalysisError(error.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleExampleSelect = (example) => {
    setQuery(example)
  }

  const getDecisionColor = (status) => {
    if (!status) return 'text-gray-600'
    const statusLower = status.toLowerCase()
    if (statusLower.includes('approve') || statusLower.includes('accept')) {
      return 'text-green-600'
    } else if (statusLower.includes('reject') || statusLower.includes('deny')) {
      return 'text-red-600'
    } else {
      return 'text-yellow-600'
    }
  }

  const getDecisionIcon = (status) => {
    if (!status) return '⏳'
    const statusLower = status.toLowerCase()
    if (statusLower.includes('approve') || statusLower.includes('accept')) {
      return '✅'
    } else if (statusLower.includes('reject') || statusLower.includes('deny')) {
      return '❌'
    } else {
      return '⏳'
    }
  }

  const getConfidenceColor = (confidence) => {
    if (!confidence) return 'text-gray-500'
    switch (confidence.toLowerCase()) {
      case 'high': return 'text-green-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      {!uploadedDocument ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-4">📋</div>
          <h4 className="text-lg font-medium mb-2">Ready to analyze</h4>
          <p>Upload a document first to start asking questions</p>
          <p className="text-sm mt-2">👈 Use the upload area on the left</p>
        </div>
      ) : (
        <>
          {/* AI Method Selection */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-800 mb-3">AI Analysis Method</h4>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="aiMethod"
                  value="local"
                  checked={useLocalAI}
                  onChange={(e) => setUseLocalAI(e.target.checked)}
                  className="mr-3"
                />
                <span className="text-sm">
                  🤖 Local AI (No API key needed) - Uses open-source models
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="aiMethod"
                  value="openai"
                  checked={!useLocalAI}
                  onChange={(e) => setUseLocalAI(!e.target.checked)}
                  className="mr-3"
                />
                <span className="text-sm">
                  🌐 OpenAI GPT (Requires API key) - More advanced analysis
                </span>
              </label>
            </div>

            {!useLocalAI && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  placeholder="sk-proj-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Your API key is used only for this analysis and not stored
                </p>
              </div>
            )}
          </div>

          {/* Example Queries */}
          <div>
            <h4 className="font-medium text-gray-800 mb-3">💡 Try these example queries:</h4>
            <div className="grid grid-cols-1 gap-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleSelect(example)}
                  className="text-left p-2 text-sm bg-gray-100 hover:bg-indigo-50 hover:border-indigo-300 border border-gray-200 rounded transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Query Input */}
          <form onSubmit={handleQuerySubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                💬 Ask Your Question
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask questions like: '46-year-old male, knee surgery in Pune, 3-month-old policy' ✨"
                rows="4"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={isAnalyzing}
              />
              <p className="text-xs text-gray-500 mt-1">
                📋 Describe the patient, procedure, location, and policy details in natural language
              </p>
            </div>

            <button
              type="submit"
              disabled={isAnalyzing || !query.trim()}
              className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  🤖 AI Analysis in progress...
                </>
              ) : (
                '🤖 Analyze with AI'
              )}
            </button>
          </form>

          {/* Error Display */}
          {analysisError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="text-red-400 mr-3">❌</div>
                <div>
                  <h4 className="text-sm font-medium text-red-800">Analysis Error</h4>
                  <p className="text-sm text-red-600 mt-1">{analysisError}</p>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResult && (
            <div className="bg-white border rounded-lg p-6 shadow-lg">
              <h3 className="text-xl font-bold text-gray-800 mb-6">📋 Analysis Results</h3>

              {/* Decision */}
              <div className="mb-6">
                <div className={`text-3xl font-bold text-center py-4 px-6 rounded-lg ${
                  analysisResult.analysis.decision.status?.toLowerCase().includes('approve') ? 'bg-green-50 border-green-200' :
                  analysisResult.analysis.decision.status?.toLowerCase().includes('reject') ? 'bg-red-50 border-red-200' :
                  'bg-yellow-50 border-yellow-200'
                } border-2`}>
                  <div className={`text-4xl mb-2 ${getDecisionColor(analysisResult.analysis.decision.status)}`}>
                    {getDecisionIcon(analysisResult.analysis.decision.status)} {analysisResult.analysis.decision.status}
                  </div>
                  <div className="flex justify-center items-center space-x-4 text-sm">
                    <span className={`font-medium ${getConfidenceColor(analysisResult.analysis.decision.confidence)}`}>
                      Confidence: {analysisResult.analysis.decision.confidence}
                    </span>
                    {analysisResult.analysis.decision.risk_level && (
                      <span className="text-gray-600">
                        Risk: {analysisResult.analysis.decision.risk_level}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Extracted Query Details */}
              {analysisResult.query.parsed_components && Object.keys(analysisResult.query.parsed_components).length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-800 mb-3">🔍 Extracted Query Details</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {Object.entries(analysisResult.query.parsed_components).map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium text-gray-600">
                          {key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:
                        </span>
                        <span className="ml-2 text-gray-800">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Justification */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">📝 Justification</h4>
                <p className="text-gray-700 leading-relaxed">
                  {analysisResult.analysis.justification.summary}
                </p>
                {analysisResult.analysis.justification.detailed_factors && 
                 analysisResult.analysis.justification.detailed_factors.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-600 mb-2">Detailed Factors:</p>
                    <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                      {analysisResult.analysis.justification.detailed_factors.map((factor, index) => (
                        <li key={index}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              {analysisResult.analysis.recommendations && analysisResult.analysis.recommendations.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-800 mb-3">💡 Recommendations</h4>
                  <ul className="list-disc pl-5 text-gray-700 space-y-1">
                    {analysisResult.analysis.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Next Steps */}
              {analysisResult.analysis.next_steps && analysisResult.analysis.next_steps.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-800 mb-3">📋 Next Steps</h4>
                  <ol className="list-decimal pl-5 text-gray-700 space-y-1">
                    {analysisResult.analysis.next_steps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Technical Details */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <details className="text-sm">
                  <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                    🔧 Technical Details
                  </summary>
                  <div className="mt-3 space-y-2 text-gray-600">
                    <p><strong>Analysis ID:</strong> {analysisResult.analysis_id}</p>
                    <p><strong>Method:</strong> {analysisResult.system.analysis_method}</p>
                    <p><strong>Processing Time:</strong> {analysisResult.system.processing_time}</p>
                    {analysisResult.document_analysis && (
                      <p><strong>Chunks Analyzed:</strong> {analysisResult.document_analysis.chunks_analyzed}</p>
                    )}
                  </div>
                </details>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}