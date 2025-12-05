import type { DocumentStatus } from '../generated/types.gen';

interface ProcessingStatusProps {
  status: DocumentStatus;
  filename: string;
}

export const ProcessingStatus = ({ status, filename }: ProcessingStatusProps) => {
  const statusConfig = {
    uploaded: {
      color: 'bg-blue-100 text-blue-800 border-blue-200',
      icon: '📤',
      label: 'Uploaded',
    },
    processing: {
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: '⚡',
      label: 'Processing with AI...',
    },
    completed: {
      color: 'bg-green-100 text-green-800 border-green-200',
      icon: '✅',
      label: 'Complete',
    },
    failed: {
      color: 'bg-red-100 text-red-800 border-red-200',
      icon: '❌',
      label: 'Failed',
    },
  };

  const config = statusConfig[status];

  return (
    <div className={`border rounded-lg p-4 ${config.color}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{config.icon}</span>
        <div className="flex-1">
          <p className="font-semibold">{filename}</p>
          <p className="text-sm">{config.label}</p>
        </div>
        {status === 'processing' && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current" />
        )}
      </div>
    </div>
  );
};
