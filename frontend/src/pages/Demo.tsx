import { Activity, BarChart3, Box, Cloud, Code2, Database, FileText, GitBranch, Layers, Lightbulb, Rocket, Server, Sparkles, Target, Zap } from 'lucide-react';

export default function Demo() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg shadow-xl p-8 mb-8 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="h-8 w-8" />
          <h1 className="text-4xl font-bold">Medical Data Extraction Platform</h1>
        </div>
        <p className="text-xl text-blue-100 mb-6">
          Enterprise-grade GenAI solution for structuring unstructured medical documents using AWS Bedrock, MLOps best practices, and full-stack engineering
        </p>
        <div className="flex flex-wrap gap-3">
          <span className="px-4 py-2 bg-white/20 rounded-full text-sm font-medium">Production-Ready</span>
          <span className="px-4 py-2 bg-white/20 rounded-full text-sm font-medium">AWS Cloud-Native</span>
          <span className="px-4 py-2 bg-white/20 rounded-full text-sm font-medium">MLOps Pipeline</span>
          <span className="px-4 py-2 bg-white/20 rounded-full text-sm font-medium">Full-Stack</span>
        </div>
      </div>

      {/* Business Problem */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Target className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Business Problem</h2>
        </div>
        <p className="text-gray-700 text-lg leading-relaxed">
          Insurance underwriters need to extract structured data from unstructured medical documents (doctor notes, lab reports, medical histories) to make informed underwriting decisions. Manual extraction is time-consuming, error-prone, and doesn't scale.
        </p>
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-blue-900 font-medium">
            <strong>Solution:</strong> Automated GenAI-powered extraction system that transforms unstructured medical text into structured, normalized data for underwriting workflows.
          </p>
        </div>
      </div>

      {/* Technical Architecture */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <Layers className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Technical Architecture</h2>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          {/* Frontend */}
          <div className="border border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-2 mb-3">
              <Code2 className="h-5 w-5 text-blue-600" />
              <h3 className="font-bold text-lg">Frontend</h3>
            </div>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span><strong>React 18</strong> with TypeScript</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span><strong>Vite</strong> for fast builds</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span><strong>TailwindCSS</strong> for styling</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span><strong>Lucide Icons</strong> for UI</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Real-time MLOps dashboard</span>
              </li>
            </ul>
          </div>

          {/* Backend */}
          <div className="border border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-2 mb-3">
              <Server className="h-5 w-5 text-green-600" />
              <h3 className="font-bold text-lg">Backend</h3>
            </div>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span><strong>Python 3.11</strong> with FastAPI</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span><strong>Pydantic</strong> for validation</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span><strong>AWS Lambda</strong> serverless</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span><strong>API Gateway</strong> REST API</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Structured logging & monitoring</span>
              </li>
            </ul>
          </div>

          {/* Cloud Infrastructure */}
          <div className="border border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-2 mb-3">
              <Cloud className="h-5 w-5 text-purple-600" />
              <h3 className="font-bold text-lg">AWS Cloud</h3>
            </div>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">•</span>
                <span><strong>Bedrock</strong> (Claude 3 Haiku)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">•</span>
                <span><strong>DynamoDB</strong> for storage</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">•</span>
                <span><strong>S3</strong> for documents</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">•</span>
                <span><strong>CloudWatch</strong> for logs</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">•</span>
                <span><strong>X-Ray</strong> for tracing</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Key Features & MLOps */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* MLOps Features */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="h-6 w-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">MLOps Pipeline</h2>
          </div>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <GitBranch className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Prompt Versioning</strong>
                <p className="text-gray-600 text-sm">Dynamic prompt management with version control (v1.0.0 → v2.1.0)</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <BarChart3 className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Performance Metrics</strong>
                <p className="text-gray-600 text-sm">Real-time tracking of accuracy, latency, success rates per version</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Zap className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">A/B Testing</strong>
                <p className="text-gray-600 text-sm">Statistical comparison between prompt versions with confidence intervals</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Database className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Experiment Tracking</strong>
                <p className="text-gray-600 text-sm">Full audit trail of all extractions with metadata and versioning</p>
              </div>
            </li>
          </ul>
        </div>

        {/* Engineering Excellence */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <Rocket className="h-6 w-6 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900">Engineering Excellence</h2>
          </div>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <Box className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Infrastructure as Code</strong>
                <p className="text-gray-600 text-sm">AWS CDK (TypeScript) for reproducible deployments</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <GitBranch className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">CI/CD Pipeline</strong>
                <p className="text-gray-600 text-sm">GitHub Actions for automated testing and deployment</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Type Safety</strong>
                <p className="text-gray-600 text-sm">End-to-end TypeScript + Pydantic validation</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Lightbulb className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="text-gray-900">Best Practices</strong>
                <p className="text-gray-600 text-sm">SOLID principles, DRY, comprehensive error handling</p>
              </div>
            </li>
          </ul>
        </div>
      </div>

      {/* Job Alignment */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-md p-6 mb-8 border border-green-200">
        <div className="flex items-center gap-3 mb-4">
          <Target className="h-6 w-6 text-green-600" />
          <h2 className="text-2xl font-bold text-gray-900">Alignment with Role Requirements</h2>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-bold text-lg text-gray-900 mb-3">Technical Skills Demonstrated</h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>GenAI/LLM:</strong> AWS Bedrock integration with Claude 3</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>Full-Stack:</strong> React/TypeScript frontend, Python/FastAPI backend</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>AWS Expertise:</strong> Lambda, Bedrock, DynamoDB, S3, API Gateway</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>IaC:</strong> AWS CDK with TypeScript for infrastructure</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>MLOps:</strong> Versioning, metrics, A/B testing, monitoring</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span><strong>DevOps:</strong> CI/CD, automated testing, logging</span>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg text-gray-900 mb-3">Business Value Delivered</h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>Underwriting Use Case:</strong> Directly addresses medical data structuring</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>End-to-End Ownership:</strong> From prototype to production-ready</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>Iterative Improvement:</strong> Prompt versioning enables continuous optimization</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>Data-Driven:</strong> Metrics and A/B testing for empirical validation</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>Scalable Architecture:</strong> Serverless design for cost optimization</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span><strong>Production-Ready:</strong> Security, monitoring, error handling</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Technical Highlights */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="h-6 w-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Technical Highlights</h2>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h3 className="font-bold text-purple-900 mb-2">Prompt Engineering</h3>
            <p className="text-sm text-purple-800">
              Iterative prompt refinement from v1.0.0 to v2.1.0, improving accuracy by emphasizing explicit extraction and reducing hallucination
            </p>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-bold text-blue-900 mb-2">Structured Extraction</h3>
            <p className="text-sm text-blue-800">
              Pydantic models ensure type-safe extraction of diagnoses, medications, lab values, allergies, and vital signs with validation
            </p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-bold text-green-900 mb-2">Export Capabilities</h3>
            <p className="text-sm text-green-800">
              Multi-format export (JSON, CSV, XML) for integration with downstream underwriting systems and workflows
            </p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="font-bold text-gray-900 mb-2">Code Quality & Maintainability</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
            <ul className="space-y-1">
              <li>• Comprehensive error handling and logging</li>
              <li>• SOLID principles and design patterns</li>
              <li>• Type safety across full stack</li>
            </ul>
            <ul className="space-y-1">
              <li>• Automated code formatting (Black, Prettier)</li>
              <li>• Modular, testable architecture</li>
              <li>• Documentation and inline comments</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
