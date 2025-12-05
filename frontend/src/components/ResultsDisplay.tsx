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
        <div className="mt-2 space-y-1">
          <p className="text-sm text-gray-500">
            Processed by {result.model_id || 'Claude 3'} in{' '}
            {result.processing_time_ms ? `${result.processing_time_ms}ms` : 'N/A'}
          </p>
          {result.prompt_version && (
            <p className="text-sm text-gray-500">
              <span className="font-medium">Prompt Version:</span> {result.prompt_version}
            </p>
          )}
        </div>
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
          <ul className="bg-red-50 rounded-lg p-4 space-y-2">
            {medical_data.diagnoses.map((diagnosis, idx) => {
              // Handle both string and object formats
              if (typeof diagnosis === 'string') {
                return <li key={idx} className="text-red-900">• {diagnosis}</li>;
              }
              return (
                <li key={idx} className="text-red-900">
                  <div className="font-medium">• {diagnosis.condition}</div>
                  {diagnosis.icd_code && <div className="text-sm ml-4">ICD: {diagnosis.icd_code}</div>}
                  {diagnosis.severity && <div className="text-sm ml-4">Severity: {diagnosis.severity}</div>}
                  {diagnosis.date_diagnosed && <div className="text-sm ml-4">Diagnosed: {diagnosis.date_diagnosed}</div>}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {medical_data.medications && medical_data.medications.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Medications</h3>
          <ul className="bg-blue-50 rounded-lg p-4 space-y-2">
            {medical_data.medications.map((med, idx) => {
              // Handle both string and object formats
              if (typeof med === 'string') {
                return <li key={idx} className="text-blue-900">• {med}</li>;
              }
              return (
                <li key={idx} className="text-blue-900">
                  <div className="font-medium">• {med.name}</div>
                  {med.dosage && <div className="text-sm ml-4">Dosage: {med.dosage}</div>}
                  {med.frequency && <div className="text-sm ml-4">Frequency: {med.frequency}</div>}
                  {med.route && <div className="text-sm ml-4">Route: {med.route}</div>}
                  {med.indication && <div className="text-sm ml-4">For: {med.indication}</div>}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {medical_data.lab_values && Object.keys(medical_data.lab_values).length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Lab Values</h3>
          <div className="bg-purple-50 rounded-lg p-4 space-y-3">
            {Object.entries(medical_data.lab_values).map(([key, value]) => {
              // Handle both string and object formats
              if (typeof value === 'string' || typeof value === 'number') {
                return (
                  <div key={key}>
                    <span className="font-medium text-purple-900">{key}:</span>{' '}
                    <span className="text-purple-800">{String(value)}</span>
                  </div>
                );
              }
              const labValue = value as { value?: string; reference_range?: string; flag?: string; date?: string };
              return (
                <div key={key} className="border-l-2 border-purple-300 pl-3">
                  <div className="font-medium text-purple-900">{key}</div>
                  {labValue.value && <div className="text-sm text-purple-800">Value: {labValue.value}</div>}
                  {labValue.reference_range && <div className="text-sm text-purple-700">Range: {labValue.reference_range}</div>}
                  {labValue.flag && <div className="text-sm text-purple-700">Flag: {labValue.flag}</div>}
                  {labValue.date && <div className="text-sm text-purple-600">Date: {labValue.date}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {medical_data.vital_signs && Object.keys(medical_data.vital_signs).length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Vital Signs</h3>
          <div className="bg-green-50 rounded-lg p-4 space-y-2">
            {Object.entries(medical_data.vital_signs).map(([key, value]) => {
              // Handle both string and object formats
              if (typeof value === 'string' || typeof value === 'number') {
                return (
                  <div key={key}>
                    <span className="font-medium text-green-900">{key}:</span>{' '}
                    <span className="text-green-800">{String(value)}</span>
                  </div>
                );
              }
              const vitalSign = value as { value?: string; date?: string };
              return (
                <div key={key}>
                  <span className="font-medium text-green-900">{key}:</span>{' '}
                  <span className="text-green-800">{vitalSign.value}</span>
                  {vitalSign.date && <span className="text-sm text-green-700 ml-2">({vitalSign.date})</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {medical_data.procedures && medical_data.procedures.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Procedures</h3>
          <ul className="bg-indigo-50 rounded-lg p-4 space-y-2">
            {medical_data.procedures.map((proc, idx) => {
              if (typeof proc === 'string') {
                return <li key={idx} className="text-indigo-900">• {proc}</li>;
              }
              return (
                <li key={idx} className="text-indigo-900">
                  <div className="font-medium">• {proc.name}</div>
                  {proc.date && <div className="text-sm ml-4">Date: {proc.date}</div>}
                  {proc.outcome && <div className="text-sm ml-4">Outcome: {proc.outcome}</div>}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {medical_data.allergies && medical_data.allergies.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Allergies</h3>
          <ul className="bg-orange-50 rounded-lg p-4 space-y-2">
            {medical_data.allergies.map((allergy, idx) => {
              if (typeof allergy === 'string') {
                return <li key={idx} className="text-orange-900">• {allergy}</li>;
              }
              return (
                <li key={idx} className="text-orange-900">
                  <div className="font-medium">• {allergy.allergen}</div>
                  {allergy.reaction && <div className="text-sm ml-4">Reaction: {allergy.reaction}</div>}
                  {allergy.severity && <div className="text-sm ml-4">Severity: {allergy.severity}</div>}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {medical_data.risk_factors && medical_data.risk_factors.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Risk Factors</h3>
          <ul className="bg-yellow-50 rounded-lg p-4 space-y-1">
            {medical_data.risk_factors.map((risk, idx) => (
              <li key={idx} className="text-yellow-900">• {risk}</li>
            ))}
          </ul>
        </div>
      )}

      {medical_data.notes && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-800">{medical_data.notes}</p>
          </div>
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
