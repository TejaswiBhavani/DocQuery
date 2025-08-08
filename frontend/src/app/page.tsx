'use client';

interface AnalysisResult {
  success: boolean;
  analysis_id: string;
  timestamp: string;
  query: {
    original: string;
    parsed_components: Record<string, unknown>;
    domain: string;
  };
  analysis: {
    decision: {
      status: string;
      confidence: string;
      risk_level?: string;
    };
    justification: {
      summary: string;
      detailed_factors?: string[];
      clause_references?: string[];
    };
    recommendations?: string[];
    next_steps?: string[];
  };
  document_analysis?: {
    document_id: string;
    document_name: string;
    chunks_analyzed: number;
    relevant_content?: string[];
  };
  system: {
    analysis_method: string;
    processing_time: string;
    model_version: string;
    search_type?: string;
    capabilities_used?: Record<string, boolean>;
  };
}

import { useState } from 'react';
import DocumentUpload from '@/components/DocumentUpload';
import QueryForm from '@/components/QueryForm';
import AnalysisResults from '@/components/AnalysisResults';

export default function Home() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentUploaded = (id: string, name: string) => {
    setDocumentId(id);
    setDocumentName(name);
    setAnalysisResult(null); // Clear previous results
  };

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4">
            <span className="text-2xl">📋</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            DocQuery
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered document analysis system. Upload insurance policies, contracts, 
            or any documents and ask natural language questions for intelligent insights.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column - Upload and Query */}
            <div className="space-y-8">
              {/* Document Upload Section */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                  <span className="mr-3">📁</span>
                  Document Upload
                </h2>
                <DocumentUpload
                  onDocumentUploaded={handleDocumentUploaded}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                />
              </div>

              {/* Query Form Section */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                  <span className="mr-3">❓</span>
                  Query Analysis
                </h2>
                {!documentId ? (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📄</div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Ready to analyze</h3>
                    <p className="text-gray-500">Upload a document first to start asking questions</p>
                    <p className="text-sm text-gray-400 mt-2">👈 Use the upload area above</p>
                  </div>
                ) : (
                  <QueryForm
                    documentId={documentId}
                    documentName={documentName}
                    onAnalysisComplete={handleAnalysisComplete}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                  />
                )}
              </div>
            </div>

            {/* Right Column - Results */}
            <div className="lg:sticky lg:top-8 lg:h-fit">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                  <span className="mr-3">📊</span>
                  Analysis Results
                </h2>
                {analysisResult ? (
                  <AnalysisResults result={analysisResult} />
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🤖</div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">AI Analysis Ready</h3>
                    <p className="text-gray-500">
                      Upload a document and submit a query to see intelligent analysis results
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Features Footer */}
        <div className="mt-16 text-center">
          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-2xl mb-2">📄</div>
              <h3 className="font-medium text-gray-900">Multi-format</h3>
              <p className="text-sm text-gray-600">PDF, DOCX, Email, Text</p>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-2xl mb-2">🔍</div>
              <h3 className="font-medium text-gray-900">Semantic Search</h3>
              <p className="text-sm text-gray-600">AI-powered search</p>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-2xl mb-2">🧠</div>
              <h3 className="font-medium text-gray-900">Local AI</h3>
              <p className="text-sm text-gray-600">No API keys required</p>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-2xl mb-2">📊</div>
              <h3 className="font-medium text-gray-900">Structured Output</h3>
              <p className="text-sm text-gray-600">JSON responses</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
