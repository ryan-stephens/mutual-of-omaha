import { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { ProcessingStatus } from './components/ProcessingStatus';
import { ResultsDisplay } from './components/ResultsDisplay';
import { uploadDocument, processDocument } from './services/api';
import type { ExtractionResult } from './generated/types.gen';

function App() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setError(null);
    setIsProcessing(true);

    try {
      const uploadResponse = await uploadDocument(file);
      
      setResult({
        document_id: uploadResponse.document_id,
        filename: uploadResponse.filename,
        status: 'processing',
      });

      const extractionResult = await processDocument(uploadResponse.document_id);
      setResult(extractionResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
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
          <h1 className="text-5xl font-bold text-gray-900">
            MedExtract 🏥
          </h1>
          <p className="text-gray-600 text-lg">
            AI-powered medical document extraction using AWS Bedrock
          </p>
        </header>

        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <FileUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />

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

export default App;
