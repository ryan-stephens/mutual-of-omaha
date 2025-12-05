import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function LambdaMetrics() {
  // Mock Lambda metrics - in production, these would come from CloudWatch
  const functionMetrics = [
    {
      function: 'upload',
      invocations: 1245,
      errors: 3,
      throttles: 0,
      avg_duration_ms: 145,
      cold_starts: 12,
      memory_used_mb: 178,
      memory_allocated_mb: 512,
      cost_usd: 0.0023
    },
    {
      function: 'extract',
      invocations: 1198,
      errors: 8,
      throttles: 2,
      avg_duration_ms: 4523,
      cold_starts: 15,
      memory_used_mb: 1456,
      memory_allocated_mb: 2048,
      cost_usd: 0.1245
    },
    {
      function: 'metrics',
      invocations: 342,
      errors: 0,
      throttles: 0,
      avg_duration_ms: 823,
      cold_starts: 8,
      memory_used_mb: 645,
      memory_allocated_mb: 1024,
      cost_usd: 0.0089
    },
    {
      function: 'experiment',
      invocations: 156,
      errors: 1,
      throttles: 0,
      avg_duration_ms: 234,
      cold_starts: 4,
      memory_used_mb: 298,
      memory_allocated_mb: 512,
      cost_usd: 0.0012
    }
  ];

  // Duration trends over time
  const durationTrends = [
    { time: '00:00', upload: 142, extract: 4321, metrics: 812, experiment: 225 },
    { time: '04:00', upload: 138, extract: 4567, metrics: 834, experiment: 241 },
    { time: '08:00', upload: 151, extract: 4698, metrics: 845, experiment: 238 },
    { time: '12:00', upload: 147, extract: 4412, metrics: 819, experiment: 229 },
    { time: '16:00', upload: 143, extract: 4534, metrics: 827, experiment: 235 },
    { time: '20:00', upload: 149, extract: 4489, metrics: 821, experiment: 232 },
  ];

  // Cold start analysis
  const totalInvocations = functionMetrics.reduce((sum, f) => sum + f.invocations, 0);
  const totalColdStarts = functionMetrics.reduce((sum, f) => sum + f.cold_starts, 0);
  const coldStartPercentage = ((totalColdStarts / totalInvocations) * 100).toFixed(2);

  const coldStartData = [
    { name: 'Warm Starts', value: totalInvocations - totalColdStarts },
    { name: 'Cold Starts', value: totalColdStarts },
  ];

  const COLORS = ['#10b981', '#f59e0b'];

  // Memory utilization by function
  const memoryData = functionMetrics.map(f => ({
    name: f.function,
    used: f.memory_used_mb,
    allocated: f.memory_allocated_mb,
    efficiency: ((f.memory_used_mb / f.memory_allocated_mb) * 100).toFixed(1)
  }));

  // Total costs
  const totalCost = functionMetrics.reduce((sum, f) => sum + f.cost_usd, 0);
  const totalErrors = functionMetrics.reduce((sum, f) => sum + f.errors, 0);
  const totalThrottles = functionMetrics.reduce((sum, f) => sum + f.throttles, 0);
  const errorRate = ((totalErrors / totalInvocations) * 100).toFixed(2);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Invocations</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {totalInvocations.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cold Start Rate</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">{coldStartPercentage}%</p>
              <p className="text-xs text-gray-500 mt-1">{totalColdStarts} cold starts</p>
            </div>
            <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Error Rate</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{errorRate}%</p>
              <p className="text-xs text-gray-500 mt-1">{totalErrors} errors, {totalThrottles} throttles</p>
            </div>
            <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Lambda Cost</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">${totalCost.toFixed(4)}</p>
              <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Function-by-Function Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Function Performance</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Function</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invocations</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cold Starts</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Memory Used</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Errors</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {functionMetrics.map((func) => (
                <tr key={func.function} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-gray-900">{func.function}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {func.invocations.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {func.avg_duration_ms.toFixed(0)}ms
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      (func.cold_starts / func.invocations) > 0.02 
                        ? 'bg-orange-100 text-orange-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {func.cold_starts} ({((func.cold_starts / func.invocations) * 100).toFixed(1)}%)
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {func.memory_used_mb}MB / {func.memory_allocated_mb}MB
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {func.errors > 0 ? (
                      <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                        {func.errors}
                      </span>
                    ) : (
                      <span className="text-green-600">✓</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${func.cost_usd.toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Duration Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Duration Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={durationTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis label={{ value: 'Duration (ms)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="extract" stroke="#8b5cf6" strokeWidth={2} name="Extract (ML)" />
              <Line type="monotone" dataKey="metrics" stroke="#3b82f6" strokeWidth={2} name="Metrics" />
              <Line type="monotone" dataKey="experiment" stroke="#10b981" strokeWidth={2} name="Experiment" />
              <Line type="monotone" dataKey="upload" stroke="#f59e0b" strokeWidth={2} name="Upload" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cold Start Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cold Start Distribution</h3>
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={coldStartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(data) => `${data.name}: ${data.value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {coldStartData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Cold Start Optimization:</strong> Consider provisioned concurrency for 
              extract function (ML workload) to eliminate cold starts during peak hours.
            </p>
          </div>
        </div>
      </div>

      {/* Memory Utilization */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Utilization by Function</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={memoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Memory (MB)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="allocated" fill="#cbd5e1" name="Allocated" />
            <Bar dataKey="used" fill="#3b82f6" name="Used" />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-4 gap-4">
          {memoryData.map(func => (
            <div key={func.name} className="text-center">
              <p className="text-sm font-medium text-gray-700">{func.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                {func.efficiency}% utilized
              </p>
              {parseFloat(func.efficiency) < 50 && (
                <p className="text-xs text-orange-600 mt-1">⚠️ Over-provisioned</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Cost Optimization Recommendations */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Cost Optimization Recommendations</h3>
        <div className="space-y-3">
          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <p className="text-sm text-gray-700">
              <strong>Memory Right-Sizing:</strong> Upload function is using only 35% of allocated memory. 
              Reduce from 512MB to 256MB to save ~50% on costs.
            </p>
          </div>
          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <p className="text-sm text-gray-700">
              <strong>Provisioned Concurrency:</strong> Extract function has {coldStartPercentage}% cold starts. 
              Add 2-3 provisioned instances during business hours (9AM-5PM) for consistent performance.
            </p>
          </div>
          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <p className="text-sm text-gray-700">
              <strong>Batch Processing:</strong> Consider EventBridge scheduled rule to batch process 
              metrics calculations every hour instead of real-time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
