import { useCallback, useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export const FileUpload = ({ onFileSelect, isProcessing }: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      onFileSelect(files[0]);
      // Reset input so same file can be selected again
      e.target.value = '';
    }
  }, [onFileSelect]);

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-xl p-12 text-center transition-all
        ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50'}
        ${isProcessing ? 'opacity-50 pointer-events-none' : 'hover:border-indigo-400'}
      `}
    >
      <div className="flex flex-col items-center gap-4">
        <svg
          className="w-16 h-16 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <div>
          <label
            htmlFor="file-upload"
            className="cursor-pointer text-indigo-600 hover:text-indigo-500 font-semibold"
          >
            Choose a file
          </label>
          <span className="text-gray-600"> or drag and drop</span>
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept=".txt,.pdf,.doc,.docx"
            onChange={handleFileInput}
            disabled={isProcessing}
          />
        </div>
        <p className="text-sm text-gray-500">
          TXT, PDF, DOC up to 10MB
        </p>
      </div>
    </div>
  );
};
