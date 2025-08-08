'use client';

import { useState } from 'react';

interface DocumentUploadProps {
  onDocumentUploaded: (documentId: string, documentName: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export default function DocumentUpload({ onDocumentUploaded, isLoading, setIsLoading }: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadFile = async (file: File) => {
    setIsLoading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_name', file.name);

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 20, 90));
      }, 200);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.success) {
        onDocumentUploaded(result.document_id, result.document_name);
        setUploadProgress(0);
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${(error as Error).message}`);
      setUploadProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-700 mb-2">Processing Document</h3>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
          <div 
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
            style={{ width: `${uploadProgress}%` }}
          ></div>
        </div>
        <p className="text-gray-500">
          {uploadProgress < 30 ? 'Reading document...' :
           uploadProgress < 70 ? 'Extracting text...' :
           uploadProgress < 90 ? 'Creating search index...' : 'Finalizing...'}
        </p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* File Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={handleChange}
          accept=".pdf,.docx,.doc,.txt,.eml"
          disabled={isLoading}
        />
        
        <div className="space-y-4">
          <div className="text-4xl">📄</div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">Drop your document here</h3>
            <p className="text-gray-500 mt-1">or click to browse</p>
          </div>
          <div className="text-sm text-gray-400">
            <p><strong>Supported formats:</strong> PDF, Word (.docx), Text (.txt), Email (.eml)</p>
            <p className="mt-1"><em>Insurance policies • Contracts • Legal documents • Reports</em></p>
          </div>
          <div className="text-xs text-gray-400">
            📁 Maximum file size: 200MB
          </div>
        </div>
      </div>

      {/* Supported Formats Info */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-red-500 text-lg mb-1">📕</div>
          <div className="font-medium">PDF</div>
          <div className="text-gray-500 text-xs">Documents</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-blue-500 text-lg mb-1">📘</div>
          <div className="font-medium">Word</div>
          <div className="text-gray-500 text-xs">.docx files</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-gray-500 text-lg mb-1">📄</div>
          <div className="font-medium">Text</div>
          <div className="text-gray-500 text-xs">.txt files</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-green-500 text-lg mb-1">📧</div>
          <div className="font-medium">Email</div>
          <div className="text-gray-500 text-xs">.eml files</div>
        </div>
      </div>
    </div>
  );
}