import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface Props {
  promptVersion: string; // For future backend integration
}

export default function CostTrends({ promptVersion }: Props) {
  // Mock historical data - in production, this would come from the backend
  // promptVersion will be used to fetch version-specific cost data
  void promptVersion;
  
  const costData = [
    { date: 'Day 1', cost: 0.0012, requests: 15 },
    { date: 'Day 2', cost: 0.0025, requests: 28 },
    { date: 'Day 3', cost: 0.0038, requests: 42 },
    { date: 'Day 4', cost: 0.0051, requests: 56 },
    { date: 'Day 5', cost: 0.0062, requests: 67 },
    { date: 'Day 6', cost: 0.0074, requests: 81 },
    { date: 'Day 7', cost: 0.0085, requests: 93 },
  ];

  const totalCost = costData.reduce((sum, d) => sum + d.cost, 0);
  const totalRequests = costData.reduce((sum, d) => sum + d.requests, 0);
  const avgCostPerRequest = totalCost / totalRequests;

  // Cost breakdown by model pricing
  const inputTokenCost = 0.00025 / 1000; // per token
  const outputTokenCost = 0.00125 / 1000; // per token
  const avgInputTokens = 1500;
  const avgOutputTokens = 300;

  const costBreakdown = [
    { 
      component: 'Input Tokens',
      cost: avgInputTokens * inputTokenCost,
      percentage: (avgInputTokens * inputTokenCost) / (avgInputTokens * inputTokenCost + avgOutputTokens * outputTokenCost) * 100
    },
    { 
      component: 'Output Tokens',
      cost: avgOutputTokens * outputTokenCost,
      percentage: (avgOutputTokens * outputTokenCost) / (avgInputTokens * inputTokenCost + avgOutputTokens * outputTokenCost) * 100
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Cost Summary Cards */}
      <div className="lg:col-span-1 space-y-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Total Spend (7 Days)</h4>
          <p className="text-3xl font-bold text-purple-600">${totalCost.toFixed(4)}</p>
          <p className="text-xs text-gray-500 mt-1">{totalRequests} requests</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Avg Cost per Request</h4>
          <p className="text-3xl font-bold text-blue-600">${avgCostPerRequest.toFixed(6)}</p>
          <p className="text-xs text-gray-500 mt-1">
            ${(avgCostPerRequest * 1000).toFixed(4)} per 1K
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-600 mb-4">Cost Breakdown</h4>
          <div className="space-y-3">
            {costBreakdown.map(item => (
              <div key={item.component}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{item.component}</span>
                  <span className="font-semibold">{item.percentage.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">${item.cost.toFixed(6)} avg</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cost Trend Chart */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-md font-semibold text-gray-900 mb-4">Cost Trends (Last 7 Days)</h4>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={costData}>
              <defs>
                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis 
                yAxisId="left"
                label={{ value: 'Cost ($)', angle: -90, position: 'insideLeft' }}
                tickFormatter={(value) => `$${value.toFixed(4)}`}
              />
              <YAxis 
                yAxisId="right" 
                orientation="right"
                label={{ value: 'Requests', angle: 90, position: 'insideRight' }}
              />
              <Tooltip 
                formatter={(value: number, name: string) => {
                  if (name === 'cost') return [`$${value.toFixed(4)}`, 'Cost'];
                  return [value, 'Requests'];
                }}
              />
              <Legend />
              <Area 
                yAxisId="left"
                type="monotone" 
                dataKey="cost" 
                stroke="#8b5cf6" 
                fillOpacity={1}
                fill="url(#colorCost)"
                name="Cost"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="requests" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Requests"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Projections */}
        <div className="bg-white rounded-lg shadow p-6 mt-6">
          <h4 className="text-md font-semibold text-gray-900 mb-4">Monthly Projection</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">Current Rate</p>
              <p className="text-2xl font-bold text-blue-900 mt-2">
                ${(totalCost * 4.3).toFixed(2)}/mo
              </p>
              <p className="text-xs text-blue-600 mt-1">Based on 7-day average</p>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Low Usage</p>
              <p className="text-2xl font-bold text-green-900 mt-2">
                ${(totalCost * 2).toFixed(2)}/mo
              </p>
              <p className="text-xs text-green-600 mt-1">~50% reduction</p>
            </div>

            <div className="bg-orange-50 rounded-lg p-4">
              <p className="text-sm text-orange-600 font-medium">High Usage</p>
              <p className="text-2xl font-bold text-orange-900 mt-2">
                ${(totalCost * 8.6).toFixed(2)}/mo
              </p>
              <p className="text-xs text-orange-600 mt-1">2x current rate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
