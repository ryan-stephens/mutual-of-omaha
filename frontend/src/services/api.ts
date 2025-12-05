import {
  uploadDocumentApiUploadPost,
  processDocumentApiProcessDocumentIdPost,
  getResultsApiResultsDocumentIdGet,
} from '../generated/sdk.gen';
import type { DocumentUploadResponse, ExtractionResult } from '../generated/types.gen';

const formatError = (error: unknown, defaultMessage: string): string => {
  if (error && typeof error === 'object' && 'detail' in error) {
    const httpError = error as { detail?: Array<{ msg: string }> };
    if (httpError.detail && httpError.detail.length > 0) {
      return httpError.detail.map(d => d.msg).join(', ');
    }
  }
  return defaultMessage;
};

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data:*/*;base64, prefix
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = error => reject(error);
  });
};

export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  // Lambda requires base64 encoded file
  if (apiUrl.indexOf('amazonaws') !== -1) {
    const fileContent = await fileToBase64(file);
    
    const response = await fetch(`${apiUrl}/api/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filename: file.name,
        file_content: fileContent,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to upload document');
    }
    
    return await response.json();
  }
  
  // Local FastAPI uses multipart form data
  const { data, error } = await uploadDocumentApiUploadPost({
    body: { file },
  });

  if (error || !data) {
    throw new Error(formatError(error, 'Failed to upload document'));
  }

  return data;
};

export const processDocument = async (
  documentId: string,
  promptVersion: string = 'v2.0.0'
): Promise<ExtractionResult> => {
  const { data, error } = await processDocumentApiProcessDocumentIdPost({
    path: { document_id: documentId },
    body: { prompt_version: promptVersion },
  });

  if (error || !data) {
    throw new Error(formatError(error, 'Failed to process document'));
  }

  return data;
};

export const getResults = async (documentId: string): Promise<ExtractionResult> => {
  const { data, error } = await getResultsApiResultsDocumentIdGet({
    path: { document_id: documentId },
  });

  if (error || !data) {
    throw new Error(formatError(error, 'Failed to get results'));
  }

  return data;
};

export interface PromptVersionsResponse {
  versions: string[];
  default_version: string;
  total_count: number;
}

export const getPromptVersions = async (): Promise<PromptVersionsResponse> => {
  const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  // Skip API call if using Lambda (endpoint not deployed yet)
  // Check if URL contains amazonaws (Lambda API Gateway)
  if (apiUrl.indexOf('amazonaws') !== -1) {
    console.log('🔧 Using Lambda - returning static prompt versions');
    return {
      versions: ['v1.0.0', 'v1.1.0', 'v2.0.0'],
      default_version: 'v2.0.0',
      total_count: 3,
    };
  }
  
  try {
    const response = await fetch(`${apiUrl}/api/prompts/versions`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch prompt versions');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching prompt versions:', error);
    // Fallback to hardcoded versions if API fails
    return {
      versions: ['v1.0.0', 'v1.1.0', 'v2.0.0'],
      default_version: 'v2.0.0',
      total_count: 3,
    };
  }
};
