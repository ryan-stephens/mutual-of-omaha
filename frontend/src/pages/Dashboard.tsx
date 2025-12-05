import { useState, useEffect } from 'react';
import MetricsOverview from '../components/dashboard/MetricsOverview';
import ExperimentComparison from '../components/dashboard/ExperimentComparison';
import PromptVersionSelector from '../components/dashboard/PromptVersionSelector';
import CostTrends from '../components/dashboard/CostTrends';
import LambdaMetrics from '../components/dashboard/LambdaMetrics';
import { getPromptVersions } from '../services/api';

interface PromptVersion {
  version: string;
  is_default: boolean;
}

type TabType = 'mlops' | 'lambda';

export default function Dashboard() {
  const [selectedVersion, setSelectedVersion] = useState<string>('v2.0.0');
  const [availableVersions, setAvailableVersions] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('mlops');

  useEffect(() => {
    // Fetch available prompt versions using centralized API
    getPromptVersions()
      .then(data => {
        setAvailableVersions(
          data.versions.map((v: string) => ({
            version: v,
            is_default: v === data.default_version
          }))
        );
        setSelectedVersion(data.default_version);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load versions:', err);
        // Fallback to hardcoded versions
        setAvailableVersions([
          { version: 'v1.0.0', is_default: false },
          { version: 'v1.1.0', is_default: false },
          { version: 'v2.0.0', is_default: true },
        ]);
        setSelectedVersion('v2.0.0');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">MLOps Dashboard</h1>
              <p className="text-sm text-gray-500">Medical Document Intelligence Metrics</p>
            </div>
            <PromptVersionSelector
              versions={availableVersions}
              selectedVersion={selectedVersion}
              onVersionChange={setSelectedVersion}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('mlops')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'mlops'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              MLOps Metrics
            </button>
            <button
              onClick={() => setActiveTab('lambda')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'lambda'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Lambda Performance
            </button>
          </nav>
        </div>

        {/* MLOps Tab Content */}
        {activeTab === 'mlops' && (
          <div className="space-y-8">
            {/* Metrics Overview */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Performance Metrics
              </h2>
              <MetricsOverview promptVersion={selectedVersion} />
            </section>

            {/* Cost Trends */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Cost Analysis
              </h2>
              <CostTrends promptVersion={selectedVersion} />
            </section>

            {/* Experiment Comparison */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                A/B Test Comparison
              </h2>
              <ExperimentComparison />
            </section>
          </div>
        )}

        {/* Lambda Tab Content */}
        {activeTab === 'lambda' && (
          <div>
            <LambdaMetrics />
          </div>
        )}
      </main>
    </div>
  );
}
