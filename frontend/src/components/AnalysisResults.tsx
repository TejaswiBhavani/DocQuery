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

interface AnalysisResultsProps {
  result: AnalysisResult;
}

export default function AnalysisResults({ result }: AnalysisResultsProps) {
  const getDecisionIcon = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('approve')) return '✅';
    if (statusLower.includes('reject') || statusLower.includes('denied')) return '❌';
    return '⏳';
  };

  const getDecisionColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('approve')) return 'text-green-600 bg-green-50 border-green-200';
    if (statusLower.includes('reject') || statusLower.includes('denied')) return 'text-red-600 bg-red-50 border-red-200';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getConfidenceColor = (confidence: string) => {
    const confLower = confidence.toLowerCase();
    if (confLower === 'high') return 'text-green-600';
    if (confLower === 'low') return 'text-red-600';
    return 'text-yellow-600';
  };

  const getConfidenceIcon = (confidence: string) => {
    const confLower = confidence.toLowerCase();
    if (confLower === 'high') return '🟢';
    if (confLower === 'low') return '🔴';
    return '🟡';
  };

  return (
    <div className="space-y-6">
      {/* Decision Card */}
      <div className={`border-2 rounded-lg p-6 ${getDecisionColor(result.analysis.decision.status)}`}>
        <div className="text-center">
          <div className="text-4xl mb-2">
            {getDecisionIcon(result.analysis.decision.status)}
          </div>
          <h3 className="text-2xl font-bold mb-2">
            {result.analysis.decision.status}
          </h3>
          <div className="flex items-center justify-center space-x-4 text-sm">
            <div className="flex items-center">
              <span className="mr-1">
                {getConfidenceIcon(result.analysis.decision.confidence)}
              </span>
              <span className={getConfidenceColor(result.analysis.decision.confidence)}>
                {result.analysis.decision.confidence} Confidence
              </span>
            </div>
            {result.analysis.decision.risk_level && (
              <div className="flex items-center">
                <span className="mr-1">⚠️</span>
                <span>{result.analysis.decision.risk_level} Risk</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Query Details */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3 flex items-center">
          <span className="mr-2">🔍</span>
          Extracted Query Details
        </h4>
        {Object.keys(result.query.parsed_components).length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(result.query.parsed_components).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-600 capitalize">
                  {key.replace('_', ' ')}:
                </span>
                <span className="font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            ℹ️ No specific details extracted - analysis based on document content
          </p>
        )}
      </div>

      {/* Justification */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900 flex items-center">
          <span className="mr-2">📝</span>
          Justification
        </h4>
        <p className="text-gray-700 leading-relaxed">
          {result.analysis.justification.summary}
        </p>
        
        {result.analysis.justification.detailed_factors && 
         result.analysis.justification.detailed_factors.length > 0 && (
          <div>
            <h5 className="font-medium text-gray-800 mt-4 mb-2">Key Factors:</h5>
            <ul className="space-y-1">
              {result.analysis.justification.detailed_factors.map((factor, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2 mt-1">•</span>
                  <span className="text-gray-600 text-sm">{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.analysis.justification.clause_references && 
         result.analysis.justification.clause_references.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-3 mt-3">
            <h5 className="font-medium text-blue-900 mb-2">📚 Clause References:</h5>
            {result.analysis.justification.clause_references.map((ref, index) => (
              <p key={index} className="text-blue-800 text-sm mb-1">{ref}</p>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      {result.analysis.recommendations && result.analysis.recommendations.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <span className="mr-2">💡</span>
            Recommendations
          </h4>
          <ul className="space-y-2">
            {result.analysis.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-500 mr-2 mt-1">{index + 1}.</span>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Next Steps */}
      {result.analysis.next_steps && result.analysis.next_steps.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <span className="mr-2">📋</span>
            Next Steps
          </h4>
          <ul className="space-y-2">
            {result.analysis.next_steps.map((step, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-500 mr-2 mt-1">{index + 1}.</span>
                <span className="text-gray-700">{step}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Document Analysis Info */}
      {result.document_analysis && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <span className="mr-2">📄</span>
            Document Analysis
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Document:</span>
              <span className="font-medium">{result.document_analysis.document_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Chunks analyzed:</span>
              <span className="font-medium">{result.document_analysis.chunks_analyzed}</span>
            </div>
          </div>
          
          {result.document_analysis.relevant_content && 
           result.document_analysis.relevant_content.length > 0 && (
            <div className="mt-3">
              <h5 className="font-medium text-gray-800 mb-2">📖 Relevant Content Preview:</h5>
              <div className="bg-white border rounded p-3 text-sm text-gray-600 max-h-32 overflow-y-auto">
                {result.document_analysis.relevant_content[0]?.substring(0, 300)}
                {result.document_analysis.relevant_content[0]?.length > 300 && '...'}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Technical Details */}
      <details className="bg-gray-50 rounded-lg">
        <summary className="p-4 font-medium text-gray-900 cursor-pointer flex items-center">
          <span className="mr-2">🔧</span>
          Technical Details
        </summary>
        <div className="px-4 pb-4 space-y-2 text-sm">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Analysis ID:</span>
              <span className="font-mono">{result.analysis_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Processing time:</span>
              <span className="font-medium">{result.system.processing_time}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Method:</span>
              <span className="font-medium">{result.system.analysis_method}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Version:</span>
              <span className="font-mono">{result.system.model_version}</span>
            </div>
            {result.system.search_type && (
              <div className="flex justify-between">
                <span className="text-gray-600">Search type:</span>
                <span className="font-medium">{result.system.search_type}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600">Timestamp:</span>
              <span className="font-mono text-xs">
                {new Date(result.timestamp).toLocaleString()}
              </span>
            </div>
          </div>

          {result.system.capabilities_used && (
            <div className="mt-3">
              <h6 className="font-medium text-gray-800 mb-2">Capabilities Used:</h6>
              <div className="flex flex-wrap gap-2">
                {Object.entries(result.system.capabilities_used).map(([key, used]) => (
                  <span 
                    key={key}
                    className={`px-2 py-1 rounded text-xs ${
                      used 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {used ? '✓' : '○'} {key.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </details>
    </div>
  );
}