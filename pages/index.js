import { useState } from 'react'
import Head from 'next/head'
import DocumentUpload from '../components/DocumentUpload'

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [uploadedDocument, setUploadedDocument] = useState(null)
  const [documentContent, setDocumentContent] = useState('')

  const handleDocumentUpload = (document, content) => {
    setUploadedDocument(document)
    setDocumentContent(content)
  }

  const handleSearch = async () => {
    if (!query.trim() || !documentContent) {
      alert('Please upload a document and enter a search query')
      return
    }

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: query,
          document_text: documentContent
        })
      })
      
      const data = await response.json()
      if (data.results) {
        setResults(data.results)
      } else if (data.error) {
        alert('Search failed: ' + data.error)
      }
    } catch (error) {
      alert('Search failed: ' + error.message)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Head>
        <title>DocQuery - AI Document Analysis</title>
        <meta name="description" content="AI-powered document analysis system" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Navigation Header */}
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600">
                  📋 DocQuery
                </h1>
              </div>
              <div className="ml-4">
                <span className="text-gray-600">AI Document Analysis System</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Powered by Vercel + FastAPI
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            AI-Powered Document Analysis
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload documents and search through them with AI-powered semantic search. 
            Our optimized serverless backend provides fast, accurate results.
          </p>
        </div>

        {/* Main Interface Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Document Upload Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6">
              📁 Document Upload
            </h3>
            <DocumentUpload 
              onDocumentUpload={handleDocumentUpload}
              uploadedDocument={uploadedDocument}
            />
          </div>

          {/* Search Interface Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6">
              🔍 Semantic Search
            </h3>
            <div className="space-y-4">
              <input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your query..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button 
                onClick={handleSearch}
                disabled={!documentContent || !query.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
              >
                Search Document
              </button>
            </div>
          </div>
        </div>

        {/* Search Results */}
        {results.length > 0 && (
          <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6">
              📊 Search Results
            </h3>
            <div className="space-y-4">
              {results.map((result, i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-2">Result {i + 1}</div>
                  <div className="text-gray-800">{result}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-center text-gray-800 mb-8">
            System Capabilities
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">🚀</div>
              <h4 className="text-lg font-semibold mb-2">Serverless</h4>
              <p className="text-gray-600">
                Optimized for Vercel deployment with memory-efficient models
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">🧠</div>
              <h4 className="text-lg font-semibold mb-2">AI-Powered</h4>
              <p className="text-gray-600">
                Uses all-MiniLM-L6-v2 for semantic search with 80MB footprint
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">⚡</div>
              <h4 className="text-lg font-semibold mb-2">Fast</h4>
              <p className="text-gray-600">
                Lazy loading and memory optimization for quick responses
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>
              DocQuery - Optimized for Vercel Deployment
            </p>
            <p className="text-sm mt-2">
              Next.js Frontend + FastAPI Serverless Backend + Optimized AI Models
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}