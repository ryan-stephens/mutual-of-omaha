import { useState } from 'react';
import config from '../../config';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ComparisonResult {
  control_version: string;
  treatment_version: string;
  control_n: number;
  treatment_n: number;
  control_success_rate: number;
  treatment_success_rate: number;
  success_rate_delta: number;
  control_avg_time: number;
  treatment_avg_time: number;
  time_delta_ms: number;
  control_avg_cost: number;
  treatment_avg_cost: number;
  cost_delta_usd: number;
  cost_delta_pct: number;
  is_significant: boolean;
  recommendation: string;
}

export default function ExperimentComparison() {
  const [controlVersion, setControlVersion] = useState('v1.1.0');
  const [treatmentVersion, setTreatmentVersion] = useState('v2.0.0');
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runComparison = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/metrics/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          control_version: controlVersion,
          treatment_version: treatmentVersion,
          confidence_level: 0.95
        })
      });

      if (!response.ok) {
        throw new Error('Insufficient data for comparison');
      }

      const data = await response.json();
      setComparison(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('PROMOTE')) return 'text-green-600 bg-green-50 border-green-200';
    if (recommendation.includes('REVIEW')) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (recommendation.includes('KEEP CONTROL')) return 'text-blue-600 bg-blue-50 border-blue-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const comparisonData = comparison ? [
    {
      metric: 'Success Rate',
      control: comparison.control_success_rate,
      treatment: comparison.treatment_success_rate,
      unit: '%'
    },
    {
      metric: 'Latency',
      control: comparison.control_avg_time,
      treatment: comparison.treatment_avg_time,
      unit: 'ms'
    },
    {
      metric: 'Cost (×1000)',
      control: comparison.control_avg_cost * 1000,
      treatment: comparison.treatment_avg_cost * 1000,
      unit: '$'
    }
  ] : [];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compare Prompt Versions</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Control (Baseline)
            </label>
            <select
              value={controlVersion}
              onChange={(e) => setControlVersion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="v1.0.0">v1.0.0</option>
              <option value="v1.1.0">v1.1.0</option>
              <option value="v2.0.0">v2.0.0</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Treatment (New Version)
            </label>
            <select
              value={treatmentVersion}
              onChange={(e) => setTreatmentVersion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="v1.0.0">v1.0.0</option>
              <option value="v1.1.0">v1.1.0</option>
              <option value="v2.0.0">v2.0.0</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={runComparison}
              disabled={loading || controlVersion === treatmentVersion}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Comparing...' : 'Run Comparison'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-6 border-b border-gray-200 bg-red-50">
          <p className="text-sm text-red-600">⚠️ {error}</p>
        </div>
      )}

      {comparison && (
        <div className="p-6 space-y-6">
          {/* Recommendation Banner */}
          <div className={`p-4 border rounded-lg ${getRecommendationColor(comparison.recommendation)}`}>
            <div className="flex items-start">
              <svg className="h-5 w-5 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold">Recommendation</p>
                <p className="text-sm mt-1">{comparison.recommendation}</p>
              </div>
            </div>
          </div>

          {/* Sample Sizes */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Control Sample Size</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{comparison.control_n}</p>
              <p className="text-xs text-gray-500 mt-1">{comparison.control_version}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Treatment Sample Size</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{comparison.treatment_n}</p>
              <p className="text-xs text-gray-500 mt-1">{comparison.treatment_version}</p>
            </div>
          </div>

          {/* Comparison Chart */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-4">Side-by-Side Comparison</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <Tooltip 
                  formatter={(value: number, name: string) => {
                    const item = comparisonData.find(d => 
                      (name === 'control' && d.control === value) || 
                      (name === 'treatment' && d.treatment === value)
                    );
                    return [`${value.toFixed(2)}${item?.unit || ''}`, name === 'control' ? 'Control' : 'Treatment'];
                  }}
                />
                <Legend formatter={(value) => value === 'control' ? 'Control' : 'Treatment'} />
                <Bar dataKey="control" fill="#3b82f6" />
                <Bar dataKey="treatment" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Delta Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Success Rate Delta */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-sm text-gray-600">Success Rate Change</p>
              <p className={`text-2xl font-bold mt-2 ${comparison.success_rate_delta > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {comparison.success_rate_delta > 0 ? '+' : ''}{comparison.success_rate_delta.toFixed(2)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {comparison.treatment_success_rate.toFixed(1)}% vs {comparison.control_success_rate.toFixed(1)}%
              </p>
            </div>

            {/* Latency Delta */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-sm text-gray-600">Latency Change</p>
              <p className={`text-2xl font-bold mt-2 ${comparison.time_delta_ms < 0 ? 'text-green-600' : 'text-red-600'}`}>
                {comparison.time_delta_ms > 0 ? '+' : ''}{comparison.time_delta_ms.toFixed(0)}ms
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {comparison.treatment_avg_time.toFixed(0)}ms vs {comparison.control_avg_time.toFixed(0)}ms
              </p>
            </div>

            {/* Cost Delta */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-sm text-gray-600">Cost Change</p>
              <p className={`text-2xl font-bold mt-2 ${comparison.cost_delta_pct > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {comparison.cost_delta_pct > 0 ? '+' : ''}{comparison.cost_delta_pct.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                ${(comparison.cost_delta_usd * 1000).toFixed(4)} per 1K requests
              </p>
            </div>
          </div>

          {/* Statistical Significance */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold text-blue-900">
                  {comparison.is_significant ? 'Statistically Significant' : 'Not Yet Significant'}
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  {comparison.is_significant 
                    ? 'Results are reliable for decision-making (95% confidence)'
                    : 'Need more data for statistical significance'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {!comparison && !error && !loading && (
        <div className="p-12 text-center text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="mt-2">Select versions and run comparison to see results</p>
        </div>
      )}
    </div>
  );
}
