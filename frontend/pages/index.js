import { useState } from 'react'
import Head from 'next/head'
import DocumentUpload from '../components/DocumentUpload'
import QueryInterface from '../components/QueryInterface'

export default function Home() {
  const [uploadedDocument, setUploadedDocument] = useState(null)
  const [documentContent, setDocumentContent] = useState('')

  const handleDocumentUpload = (document, content) => {
    setUploadedDocument(document)
    setDocumentContent(content)
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
                Powered by AI
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
            Upload insurance policies, contracts, or any documents and ask natural language questions. 
            Our AI system analyzes your documents and provides intelligent decisions with detailed justifications.
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

          {/* Query Interface Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6">
              ❓ Query Analysis
            </h3>
            <QueryInterface 
              documentContent={documentContent}
              uploadedDocument={uploadedDocument}
            />
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-center text-gray-800 mb-8">
            System Capabilities
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">🤖</div>
              <h4 className="text-lg font-semibold mb-2">AI Analysis</h4>
              <p className="text-gray-600">
                Advanced AI models for intelligent document analysis and decision making
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">🔍</div>
              <h4 className="text-lg font-semibold mb-2">Smart Search</h4>
              <p className="text-gray-600">
                Semantic search to find relevant information quickly and accurately
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl mb-4">📄</div>
              <h4 className="text-lg font-semibold mb-2">Multi-Format</h4>
              <p className="text-gray-600">
                Support for PDF, Word, Text, and Email document formats
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
              DocQuery - AI Document Analysis System
            </p>
            <p className="text-sm mt-2">
              Powered by FastAPI, Next.js, and advanced AI models
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}