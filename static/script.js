// Check system status on page load
window.addEventListener('load', checkSystemStatus);

function loadExample() {
    const select = document.getElementById('queryExamples');
    const queryText = document.getElementById('queryText');
    if (select.value) {
        queryText.value = select.value;
    }
}

async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        let statusHtml = '<h3>API Status</h3>';
        statusHtml += `<div class="status-item">
            <span>Service Status</span>
            <span class="status-badge status-online">Online</span>
        </div>`;
        statusHtml += `<div class="status-item">
            <span>Search Type</span>
            <span>${data.search_type}</span>
        </div>`;
        
        if (data.capabilities) {
            statusHtml += `<div class="status-item">
                <span>Basic Functionality</span>
                <span class="status-badge ${data.capabilities.basic_functionality ? 'status-online' : 'status-offline'}">
                    ${data.capabilities.basic_functionality ? 'Available' : 'Limited'}
                </span>
            </div>`;
            statusHtml += `<div class="status-item">
                <span>Advanced AI</span>
                <span class="status-badge ${data.capabilities.advanced_ai ? 'status-online' : 'status-offline'}">
                    ${data.capabilities.advanced_ai ? 'Available' : 'Basic Only'}
                </span>
            </div>`;
        }
        
        document.getElementById('systemStatus').innerHTML = statusHtml;
    } catch (error) {
        document.getElementById('systemStatus').innerHTML = `
            <div class="error">
                <strong>Connection Error:</strong> Could not connect to API
                <br><small>${error.message}</small>
            </div>
        `;
    }
}

async function analyzeDocument() {
    const documentText = document.getElementById('documentText').value;
    const documentName = document.getElementById('documentName').value;
    const spinner = document.getElementById('analyzeSpinner');
    const button = event.target;
    
    if (!documentText.trim()) {
        showResult('error', 'Please paste some document text first.');
        return;
    }
    
    // Show loading state
    spinner.style.display = 'inline-block';
    button.disabled = true;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_text: documentText,
                document_name: documentName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResult('success', 'Document Analysis Complete', data.document_analysis, {
                type: 'document',
                processing: data.processing_details,
                stats: data.document_stats,
                capabilities: data.capabilities
            });
        } else {
            showResult('error', `Analysis Failed: ${data.error}`);
        }
    } catch (error) {
        showResult('error', `Network Error: ${error.message}`);
    } finally {
        spinner.style.display = 'none';
        button.disabled = false;
    }
}

async function processQuery() {
    const queryText = document.getElementById('queryText').value;
    const documentText = document.getElementById('documentText').value;
    const spinner = document.getElementById('querySpinner');
    const button = event.target;
    
    if (!queryText.trim()) {
        showResult('error', 'Please enter a query first.');
        return;
    }
    
    // Show loading state
    spinner.style.display = 'inline-block';
    button.disabled = true;
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: queryText,
                document_text: documentText
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.analysis) {
                showResult('success', 'AI Analysis Complete', data.query, {
                    type: 'query_analysis',
                    analysis: data.analysis,
                    system: data.system,
                    document: data.document_analysis
                });
            } else {
                showResult('info', 'Query Parsed Successfully', data.query, {
                    type: 'query_only',
                    system: data.system,
                    message: data.message
                });
            }
        } else {
            showResult('error', `Query Failed: ${data.error}`);
        }
    } catch (error) {
        showResult('error', `Network Error: ${error.message}`);
    } finally {
        spinner.style.display = 'none';
        button.disabled = false;
    }
}

function showResult(type, title, data = null, extraData = null) {
    const resultsDiv = document.getElementById('results');
    
    let resultHtml = `<div class="result-card">
        <h3>${title}</h3>`;
    
    if (type === 'error') {
        resultHtml += `<div class="error">${title}</div>`;
    } else if (type === 'success') {
        resultHtml += `<div class="success">✅ ${title}</div>`;
        
        if (extraData) {
            if (extraData.type === 'document') {
                // Enhanced document analysis display
                resultHtml += `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div>
                        <h4>📄 Document Details</h4>
                        <div class="result-content">
                            <strong>Name:</strong> ${data.document_name}
                            <strong>Size:</strong> ${data.full_content_length.toLocaleString()} characters
                            <strong>Chunks:</strong> ${data.chunk_count}
                            <strong>Avg Chunk Size:</strong> ${data.average_chunk_size.toLocaleString()}
                        </div>
                    </div>
                    <div>
                        <h4>⚡ Processing Stats</h4>
                        <div class="result-content">
                            <strong>Processing Time:</strong> ${extraData.processing.processing_time}
                            <strong>Search Type:</strong> ${extraData.processing.search_type}
                            <strong>Vector Search:</strong> ${extraData.processing.search_ready ? '✅ Ready' : '❌ Not available'}
                        </div>
                    </div>
                </div>
                
                <h4>📊 Content Statistics</h4>
                <div class="result-content">
                    <strong>Words:</strong> ${extraData.stats.total_words.toLocaleString()}
                    <strong>Reading Time:</strong> ${extraData.stats.estimated_reading_time}
                    <strong>Small Chunks:</strong> ${extraData.stats.chunk_distribution.small_chunks}
                    <strong>Medium Chunks:</strong> ${extraData.stats.chunk_distribution.medium_chunks}
                    <strong>Large Chunks:</strong> ${extraData.stats.chunk_distribution.large_chunks}
                </div>
                
                <h4>📖 Document Preview</h4>
                <div class="result-content" style="max-height: 200px; overflow-y: auto;">
                    ${data.processed_content}
                </div>`;
                
            } else if (extraData.type === 'query_analysis') {
                // Enhanced analysis display
                const analysis = extraData.analysis;
                resultHtml += `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div>
                        <h4>🔍 Query Details</h4>
                        <div class="result-content">
                            <strong>Original Query:</strong> ${data.original}
                            <strong>Domain:</strong> ${data.domain}
                            <strong>Components:</strong> ${Object.keys(data.parsed_components).length} extracted
                        </div>
                        
                        <h4>📋 Parsed Components</h4>
                        <div class="result-content">`;
                
                for (const [key, value] of Object.entries(data.parsed_components)) {
                    resultHtml += `<strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${value}\n`;
                }
                
                resultHtml += `
                        </div>
                    </div>
                    
                    <div>
                        <h4>🎯 Analysis Results</h4>
                        <div class="result-content">
                            <strong>Decision:</strong> <span style="color: ${analysis.decision.status === 'Approved' ? '#28a745' : '#dc3545'}">${analysis.decision.status}</span>
                            <strong>Confidence:</strong> ${analysis.decision.confidence}
                            <strong>Risk Level:</strong> ${analysis.decision.risk_level}
                        </div>
                        
                        <h4>⚡ System Info</h4>
                        <div class="result-content">
                            <strong>Method:</strong> ${extraData.system.analysis_method}
                            <strong>Time:</strong> ${extraData.system.processing_time}
                            <strong>Version:</strong> ${extraData.system.model_version}
                        </div>
                    </div>
                </div>
                
                <h4>💡 Justification</h4>
                <div class="result-content" style="background: #f8f9fa; border-left: 4px solid #007bff;">
                    ${analysis.justification.summary}
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div>
                        <h4>📋 Recommendations</h4>
                        <div class="result-content">`;
                
                analysis.recommendations.forEach((rec, i) => {
                    resultHtml += `${i + 1}. ${rec}\n`;
                });
                
                resultHtml += `
                        </div>
                    </div>
                    
                    <div>
                        <h4>🎯 Next Steps</h4>
                        <div class="result-content">`;
                
                analysis.next_steps.forEach((step, i) => {
                    resultHtml += `${i + 1}. ${step}\n`;
                });
                
                resultHtml += `
                        </div>
                    </div>
                </div>`;
                
            } else if (extraData.type === 'query_only') {
                resultHtml += `
                <div class="info">${extraData.message}</div>
                <h4>🔍 Parsed Query Components</h4>
                <div class="result-content">`;
                
                for (const [key, value] of Object.entries(data.parsed_components)) {
                    resultHtml += `<strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${value}\n`;
                }
                
                resultHtml += `
                </div>
                <div class="result-content">
                    <strong>Processing Time:</strong> ${extraData.system.processing_time}
                    <strong>Domain:</strong> ${data.domain}
                </div>`;
            }
        } else if (data) {
            // Fallback for simple key-value display
            resultHtml += '<div class="result-content">';
            for (const [key, value] of Object.entries(data)) {
                resultHtml += `<strong>${key}:</strong>\n${value}\n\n`;
            }
            resultHtml += '</div>';
        }
    } else if (type === 'info') {
        resultHtml += `<div class="info">ℹ️ ${title}</div>`;
        if (extraData && extraData.type === 'query_only') {
            resultHtml += `<div class="result-content">
                <strong>Query:</strong> ${data.original}
                <strong>Processing Time:</strong> ${extraData.system.processing_time}
            </div>`;
        }
    }
    
    resultHtml += '</div>';
    
    resultsDiv.innerHTML = resultHtml;
}