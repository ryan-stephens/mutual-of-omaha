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

export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const { data, error } = await uploadDocumentApiUploadPost({
    body: { file },
  });

  if (error || !data) {
    throw new Error(formatError(error, 'Failed to upload document'));
  }

  return data;
};

export const processDocument = async (documentId: string): Promise<ExtractionResult> => {
  const { data, error } = await processDocumentApiProcessDocumentIdPost({
    path: { document_id: documentId },
    body: null,
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
