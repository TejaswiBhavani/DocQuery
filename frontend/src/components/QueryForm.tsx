'use client';

import { useState } from 'react';

interface QueryFormProps {
  documentId: string;
  documentName: string;
  onAnalysisComplete: (result: AnalysisResult) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

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

export default function QueryForm({ 
  documentId, 
  documentName, 
  onAnalysisComplete, 
  isLoading, 
  setIsLoading 
}: QueryFormProps) {
  const [query, setQuery] = useState('');
  const [useLocalAI, setUseLocalAI] = useState(true);
  const [selectedExample, setSelectedExample] = useState('');

  const exampleQueries = [
    "46-year-old male, knee surgery in Mumbai, 3-month policy",
    "35-year-old female, heart surgery in Delhi, 1-year insurance",
    "Male patient, dental treatment, Bangalore, 6-month coverage",
    "Emergency surgery coverage for pre-existing condition",
    "Maternity benefits eligibility after 2-year waiting period"
  ];

  const quickTemplates = [
    { label: "Age + Procedure", template: "45-year-old patient needs surgery" },
    { label: "Location + Coverage", template: "Treatment in Mumbai, covered under policy" },
    { label: "Policy Duration", template: "2-year-old insurance policy coverage" }
  ];

  const handleExampleSelect = (example: string) => {
    setSelectedExample(example);
    setQuery(example);
  };

  const handleTemplateClick = (template: string) => {
    setQuery(template);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          document_id: documentId,
          use_local_ai: useLocalAI
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.success) {
        onAnalysisComplete(result);
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`Analysis failed: ${(error as Error).message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Document Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-blue-600 mr-2">📄</span>
          <div>
            <p className="font-medium text-blue-900">Document Ready</p>
            <p className="text-sm text-blue-700">{documentName}</p>
          </div>
        </div>
      </div>

      {/* AI Method Selection */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          AI Analysis Method
        </label>
        <div className="flex space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="local"
              checked={useLocalAI}
              onChange={(e) => setUseLocalAI(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">
              🤖 Local AI (No API key needed)
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="openai"
              checked={!useLocalAI}
              onChange={(e) => setUseLocalAI(!e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">
              🌐 OpenAI GPT (Requires API key)
            </span>
          </label>
        </div>
      </div>

      {/* Example Queries */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          💡 Try these example queries:
        </label>
        <select 
          className="w-full p-2 border border-gray-300 rounded-md"
          value={selectedExample}
          onChange={(e) => handleExampleSelect(e.target.value)}
        >
          <option value="">Choose an example...</option>
          {exampleQueries.map((example, index) => (
            <option key={index} value={example}>{example}</option>
          ))}
        </select>
      </div>

      {/* Query Input */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            💬 Ask Your Question
          </label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask questions like: '46-year-old male, knee surgery in Mumbai, 3-month-old policy' ✨"
            className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
          <p className="mt-1 text-sm text-gray-500">
            📋 Describe the patient, procedure, location, and policy details in natural language
          </p>
        </div>

        {/* Quick Templates */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">🚀 Quick Templates:</p>
          <div className="flex flex-wrap gap-2">
            {quickTemplates.map((template, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleTemplateClick(template.template)}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                disabled={isLoading}
              >
                {template.label}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
            isLoading || !query.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Analyzing...
            </div>
          ) : (
            '🤖 Analyze with AI'
          )}
        </button>
      </form>
    </div>
  );
}