'use client';

import { useState, useEffect } from 'react';

interface SlaViolation {
  document_id: number;
  file_name: string;
  organization_id: string;
  violation_type: 'QUEUE_DELAY' | 'PROCESSING_DELAY';
  delay_seconds: number;
  threshold_seconds: number;
  created_at?: string;
  processing_started_at?: string;
}

interface SlaBreachResponse {
  total_violations: number;
  violations: SlaViolation[];
}

export default function SlaBreachMonitor() {
  const [violations, setViolations] = useState<SlaViolation[]>([]);
  const [totalViolations, setTotalViolations] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSlaBreaches = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/operator/sla-breaches');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: SlaBreachResponse = await response.json();
      setViolations(data.violations);
      setTotalViolations(data.total_violations);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSlaBreaches();
    
    // Refresh every 10 seconds
    const intervalId = setInterval(() => {
      fetchSlaBreaches();
    }, 10000);

    return () => clearInterval(intervalId);
  }, []);

  const getViolationBadge = (violationType: string) => {
    if (violationType === 'QUEUE_DELAY') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-300">
          QUEUE_DELAY
        </span>
      );
    } else if (violationType === 'PROCESSING_DELAY') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-300 animate-pulse">
          PROCESSING_DELAY
        </span>
      );
    }
    return null;
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">SLA Breach Monitor</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Total Violations:</span>
            <span className="text-2xl font-bold text-red-600">{totalViolations}</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-2 text-gray-600">Loading SLA breaches...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">Error: {error}</p>
          </div>
        )}

        {!isLoading && !error && violations.length === 0 && (
          <div className="text-center py-8">
            <div className="inline-block p-4 rounded-full bg-green-100">
              <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="mt-2 text-gray-600">No SLA breaches detected</p>
          </div>
        )}

        {!isLoading && !error && violations.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Organization ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Violation Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Delay (seconds)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Threshold (seconds)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {violations.map((violation) => (
                  <tr key={violation.document_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {violation.document_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {violation.file_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {violation.organization_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getViolationBadge(violation.violation_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="font-mono">{violation.delay_seconds.toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="font-mono">{violation.threshold_seconds.toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatTimestamp(violation.created_at || violation.processing_started_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
