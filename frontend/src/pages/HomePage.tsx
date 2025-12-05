import { useState, useEffect } from 'react';
import { FileUpload } from '../components/FileUpload';
import { ProcessingStatus } from '../components/ProcessingStatus';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { uploadDocument, processDocument, getPromptVersions } from '../services/api';
import type { ExtractionResult } from '../generated/types.gen';

export default function HomePage() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promptVersion, setPromptVersion] = useState('v2.0.0');
  const [availableVersions, setAvailableVersions] = useState<string[]>([]);
  const [isLoadingVersions, setIsLoadingVersions] = useState(true);

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        const data = await getPromptVersions();
        setAvailableVersions(data.versions);
        setPromptVersion(data.default_version);
      } catch (err) {
        console.error('Failed to load prompt versions:', err);
      } finally {
        setIsLoadingVersions(false);
      }
    };

    fetchVersions();
  }, []);

  const handleFileSelect = async (file: File) => {
    console.log('📄 File selected:', file.name, 'Prompt version:', promptVersion);
    setError(null);
    setIsProcessing(true);

    try {
      console.log('⬆️ Uploading document...');
      const uploadResponse = await uploadDocument(file);
      console.log('✅ Upload complete:', uploadResponse.document_id);
      
      setResult({
        document_id: uploadResponse.document_id,
        filename: uploadResponse.filename,
        status: 'processing',
      });

      console.log('🤖 Processing with Bedrock, version:', promptVersion);
      const extractionResult = await processDocument(uploadResponse.document_id, promptVersion);
      console.log('✅ Extraction complete');
      setResult(extractionResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      console.error('❌ Error:', message);
      setError(message);
      setResult(null);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <p className="text-gray-600 text-lg">
            AI-powered medical document extraction using AWS Bedrock
          </p>
        </header>

        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <FileUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />
          
          <div className="flex items-center justify-between text-sm border-t pt-4">
            <span className="text-gray-600">Prompt Version:</span>
            <select
              id="prompt-version"
              value={promptVersion}
              onChange={(e) => setPromptVersion(e.target.value)}
              disabled={isProcessing || isLoadingVersions}
              className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              {isLoadingVersions ? (
                <option>Loading...</option>
              ) : (
                availableVersions.map((version) => (
                  <option key={version} value={version}>
                    {version}
                  </option>
                ))
              )}
            </select>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-semibold">Error</p>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {result && (
            <ProcessingStatus status={result.status} filename={result.filename} />
          )}
        </div>

        {result && result.status === 'completed' && (
          <ResultsDisplay result={result} />
        )}

        <footer className="text-center text-sm text-gray-500">
          <p>Built with React + TypeScript + FastAPI + AWS Bedrock</p>
        </footer>
      </div>
    </div>
  );
}
