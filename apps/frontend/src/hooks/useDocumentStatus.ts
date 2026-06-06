import { useState, useEffect, useCallback } from 'react';

interface DocumentStatusResponse {
  document_id: number;
  status: string;
  upload_status: string;
  file_name: string;
}

interface UseDocumentStatusReturn {
  status: string;
  isQueued: boolean;
  isProcessing: boolean;
  isCompleted: boolean;
  isFailed: boolean;
  error: string | null;
  isLoading: boolean;
}

export function useDocumentStatus(documentId: string): UseDocumentStatusReturn {
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchStatus = useCallback(async () => {
    if (!documentId) return;

    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: DocumentStatusResponse = await response.json();
      setStatus(data.status);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    if (!documentId) return;

    // Initial fetch
    fetchStatus();

    // Set up polling interval (every 2.5 seconds)
    const intervalId = setInterval(() => {
      fetchStatus();
    }, 2500);

    // Clean up interval on component unmount
    return () => {
      clearInterval(intervalId);
    };
  }, [documentId, fetchStatus]);

  // Stop polling when reaching terminal state
  useEffect(() => {
    if (status === 'COMPLETED' || status === 'FAILED') {
      // The cleanup function in the previous useEffect will handle clearing the interval
      // This effect is just to document the terminal state logic
    }
  }, [status]);

  return {
    status,
    isQueued: status === 'QUEUED',
    isProcessing: status === 'PROCESSING',
    isCompleted: status === 'COMPLETED',
    isFailed: status === 'FAILED',
    error,
    isLoading
  };
}
