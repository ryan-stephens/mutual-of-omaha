import type { ExtractionResult } from '../generated/types.gen';

interface ResultsDisplayProps {
  result: ExtractionResult;
}

export const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  if (!result.medical_data) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <p className="text-yellow-800">No medical data extracted yet.</p>
      </div>
    );
  }

  const { medical_data } = result;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900">Extraction Results</h2>
        <p className="text-sm text-gray-500 mt-1">
          Processed by {result.model_id || 'Claude 3'} in{' '}
          {result.processing_time_ms ? `${result.processing_time_ms}ms` : 'N/A'}
        </p>
      </div>

      {medical_data.patient_name && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Patient Information</h3>
          <div className="bg-gray-50 rounded-lg p-4 space-y-1">
            <p><span className="font-medium">Name:</span> {medical_data.patient_name}</p>
            {medical_data.date_of_birth && (
              <p><span className="font-medium">DOB:</span> {medical_data.date_of_birth}</p>
            )}
          </div>
        </div>
      )}

      {medical_data.diagnoses && medical_data.diagnoses.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Diagnoses</h3>
          <ul className="bg-red-50 rounded-lg p-4 space-y-1">
            {medical_data.diagnoses.map((diagnosis, idx) => (
              <li key={idx} className="text-red-900">• {diagnosis}</li>
            ))}
          </ul>
        </div>
      )}

      {medical_data.medications && medical_data.medications.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Medications</h3>
          <ul className="bg-blue-50 rounded-lg p-4 space-y-1">
            {medical_data.medications.map((med, idx) => (
              <li key={idx} className="text-blue-900">• {med}</li>
            ))}
          </ul>
        </div>
      )}

      {medical_data.lab_values && Object.keys(medical_data.lab_values).length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Lab Values</h3>
          <div className="bg-purple-50 rounded-lg p-4 grid grid-cols-2 gap-2">
            {Object.entries(medical_data.lab_values).map(([key, value]) => (
              <div key={key}>
                <span className="font-medium text-purple-900">{key}:</span>{' '}
                <span className="text-purple-800">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {medical_data.vital_signs && Object.keys(medical_data.vital_signs).length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Vital Signs</h3>
          <div className="bg-green-50 rounded-lg p-4 grid grid-cols-2 gap-2">
            {Object.entries(medical_data.vital_signs).map(([key, value]) => (
              <div key={key}>
                <span className="font-medium text-green-900">{key}:</span>{' '}
                <span className="text-green-800">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {medical_data.allergies && medical_data.allergies.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Allergies</h3>
          <ul className="bg-orange-50 rounded-lg p-4 space-y-1">
            {medical_data.allergies.map((allergy, idx) => (
              <li key={idx} className="text-orange-900">• {allergy}</li>
            ))}
          </ul>
        </div>
      )}

      {result.token_usage && 'input_tokens' in result.token_usage && 'output_tokens' in result.token_usage && (
        <div className="border-t pt-4">
          <p className="text-xs text-gray-500">
            Token Usage: {String(result.token_usage.input_tokens)} in, {String(result.token_usage.output_tokens)} out
          </p>
        </div>
      )}
    </div>
  );
};
