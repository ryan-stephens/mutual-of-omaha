import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PromptMetrics {
  prompt_version: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate: number;
  avg_processing_time_ms: number;
  p50_processing_time_ms: number;
  p95_processing_time_ms: number;
  p99_processing_time_ms: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost_usd: number;
  avg_cost_per_request: number;
  avg_field_completeness: number;
  avg_fields_extracted: number;
  first_request: string;
  last_request: string;
}

interface Props {
  promptVersion: string;
}

export default function MetricsOverview({ promptVersion }: Props) {
  const [metrics, setMetrics] = useState<PromptMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(`http://localhost:8000/api/metrics/prompts/${promptVersion}`)
      .then(res => {
        if (!res.ok) {
          throw new Error('No metrics data available for this version');
        }
        return res.json();
      })
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [promptVersion]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-2">No metrics data available</p>
          <p className="text-sm text-gray-400 mt-1">Process some documents with this prompt version to see metrics</p>
        </div>
      </div>
    );
  }

  const latencyData = [
    { name: 'p50', value: metrics.p50_processing_time_ms, label: 'Median' },
    { name: 'Avg', value: metrics.avg_processing_time_ms, label: 'Average' },
    { name: 'p95', value: metrics.p95_processing_time_ms, label: '95th %ile' },
    { name: 'p99', value: metrics.p99_processing_time_ms, label: '99th %ile' },
  ];

  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Success Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {metrics.success_rate.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {metrics.successful_requests} / {metrics.total_requests} requests
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        {/* Avg Latency */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Latency</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {metrics.avg_processing_time_ms.toFixed(0)}ms
              </p>
              <p className="text-xs text-gray-500 mt-1">
                p95: {metrics.p95_processing_time_ms.toFixed(0)}ms
              </p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                ${metrics.total_cost_usd.toFixed(4)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                ${(metrics.avg_cost_per_request * 1000).toFixed(4)} per 1K
              </p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Field Completeness */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Quality Score</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {metrics.avg_field_completeness.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {metrics.avg_fields_extracted.toFixed(1)} / 9 fields avg
              </p>
            </div>
            <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Latency Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Latency Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={latencyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis label={{ value: 'Milliseconds', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Token Usage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Usage</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Input Tokens</span>
              <span className="text-lg font-semibold text-gray-900">
                {metrics.total_input_tokens.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Output Tokens</span>
              <span className="text-lg font-semibold text-gray-900">
                {metrics.total_output_tokens.toLocaleString()}
              </span>
            </div>
            <div className="border-t pt-3 mt-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Total Tokens</span>
                <span className="text-xl font-bold text-blue-600">
                  {(metrics.total_input_tokens + metrics.total_output_tokens).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Period</h3>
          <div className="space-y-3">
            <div>
              <span className="text-sm text-gray-600">First Request</span>
              <p className="text-sm font-medium text-gray-900 mt-1">
                {new Date(metrics.first_request).toLocaleString()}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Last Request</span>
              <p className="text-sm font-medium text-gray-900 mt-1">
                {new Date(metrics.last_request).toLocaleString()}
              </p>
            </div>
            <div className="border-t pt-3 mt-3">
              <span className="text-sm text-gray-600">Total Requests</span>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {metrics.total_requests}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
