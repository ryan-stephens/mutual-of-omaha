import type { ExtractionResult, MedicalData, LabValue } from '../generated/types.gen';

/**
 * Export medical data in various formats
 */

export const exportToJSON = (result: ExtractionResult): void => {
  const dataStr = JSON.stringify(result, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `medical-extraction-${result.document_id}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const flattenMedicalData = (data: MedicalData): Record<string, string> => {
  const flattened: Record<string, string> = {};
  
  // Basic fields
  if (data.patient_name) flattened['Patient Name'] = data.patient_name;
  if (data.date_of_birth) flattened['Date of Birth'] = data.date_of_birth;
  if (data.notes) flattened['Clinical Notes'] = data.notes;
  
  // Diagnoses
  if (data.diagnoses && data.diagnoses.length > 0) {
    data.diagnoses.forEach((diagnosis, idx) => {
      if (typeof diagnosis === 'string') {
        flattened[`Diagnosis ${idx + 1}`] = diagnosis;
      } else {
        flattened[`Diagnosis ${idx + 1} - Condition`] = diagnosis.condition;
        if (diagnosis.icd_code) flattened[`Diagnosis ${idx + 1} - ICD Code`] = diagnosis.icd_code;
        if (diagnosis.severity) flattened[`Diagnosis ${idx + 1} - Severity`] = diagnosis.severity;
        if (diagnosis.date_diagnosed) flattened[`Diagnosis ${idx + 1} - Date`] = diagnosis.date_diagnosed;
      }
    });
  }
  
  // Medications
  if (data.medications && data.medications.length > 0) {
    data.medications.forEach((med, idx) => {
      if (typeof med === 'string') {
        flattened[`Medication ${idx + 1}`] = med;
      } else {
        flattened[`Medication ${idx + 1} - Name`] = med.name;
        if (med.dosage) flattened[`Medication ${idx + 1} - Dosage`] = med.dosage;
        if (med.frequency) flattened[`Medication ${idx + 1} - Frequency`] = med.frequency;
        if (med.route) flattened[`Medication ${idx + 1} - Route`] = med.route;
        if (med.indication) flattened[`Medication ${idx + 1} - Indication`] = med.indication;
      }
    });
  }
  
  // Lab Values
  if (data.lab_values) {
    Object.entries(data.lab_values).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number') {
        flattened[`Lab - ${key}`] = String(value);
      } else {
        const labValue = value as LabValue;
        if (labValue.value) flattened[`Lab - ${key} - Value`] = labValue.value;
        if (labValue.reference_range) flattened[`Lab - ${key} - Range`] = labValue.reference_range;
        if (labValue.flag) flattened[`Lab - ${key} - Flag`] = labValue.flag;
        if (labValue.date) flattened[`Lab - ${key} - Date`] = labValue.date;
      }
    });
  }
  
  // Procedures
  if (data.procedures && data.procedures.length > 0) {
    data.procedures.forEach((proc, idx) => {
      if (typeof proc === 'string') {
        flattened[`Procedure ${idx + 1}`] = proc;
      } else {
        flattened[`Procedure ${idx + 1} - Name`] = proc.name;
        if (proc.date) flattened[`Procedure ${idx + 1} - Date`] = proc.date;
        if (proc.outcome) flattened[`Procedure ${idx + 1} - Outcome`] = proc.outcome;
      }
    });
  }
  
  // Allergies
  if (data.allergies && data.allergies.length > 0) {
    data.allergies.forEach((allergy, idx) => {
      if (typeof allergy === 'string') {
        flattened[`Allergy ${idx + 1}`] = allergy;
      } else {
        flattened[`Allergy ${idx + 1} - Allergen`] = allergy.allergen;
        if (allergy.reaction) flattened[`Allergy ${idx + 1} - Reaction`] = allergy.reaction;
        if (allergy.severity) flattened[`Allergy ${idx + 1} - Severity`] = allergy.severity;
      }
    });
  }
  
  // Vital Signs
  if (data.vital_signs) {
    Object.entries(data.vital_signs).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number') {
        flattened[`Vital - ${key}`] = String(value);
      } else {
        const vitalSign = value as { value?: string; date?: string };
        if (vitalSign.value) flattened[`Vital - ${key} - Value`] = vitalSign.value;
        if (vitalSign.date) flattened[`Vital - ${key} - Date`] = vitalSign.date;
      }
    });
  }
  
  // Risk Factors
  if (data.risk_factors && data.risk_factors.length > 0) {
    flattened['Risk Factors'] = data.risk_factors.join('; ');
  }
  
  return flattened;
};

export const exportToCSV = (result: ExtractionResult): void => {
  if (!result.medical_data) return;
  
  const flattened = flattenMedicalData(result.medical_data);
  
  // Add metadata
  const metadata: Record<string, string> = {
    'Document ID': result.document_id,
    'Filename': result.filename,
    'Status': result.status,
    'Model': result.model_id || 'N/A',
    'Prompt Version': result.prompt_version || 'N/A',
    'Processing Time (ms)': result.processing_time_ms?.toString() || 'N/A',
    'Extracted At': result.extracted_at?.toString() || 'N/A',
  };
  
  const combined = { ...metadata, ...flattened };
  
  // Create CSV
  const headers = Object.keys(combined);
  const values = Object.values(combined);
  
  const csvContent = [
    headers.join(','),
    values.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `medical-extraction-${result.document_id}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const exportToXML = (result: ExtractionResult): void => {
  if (!result.medical_data) return;
  
  const escapeXml = (str: string): string => {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  };
  
  const data = result.medical_data;
  
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<MedicalExtraction>\n';
  xml += '  <Metadata>\n';
  xml += `    <DocumentId>${escapeXml(result.document_id)}</DocumentId>\n`;
  xml += `    <Filename>${escapeXml(result.filename)}</Filename>\n`;
  xml += `    <Status>${escapeXml(result.status)}</Status>\n`;
  if (result.model_id) xml += `    <ModelId>${escapeXml(result.model_id)}</ModelId>\n`;
  if (result.prompt_version) xml += `    <PromptVersion>${escapeXml(result.prompt_version)}</PromptVersion>\n`;
  if (result.processing_time_ms) xml += `    <ProcessingTimeMs>${result.processing_time_ms}</ProcessingTimeMs>\n`;
  if (result.extracted_at) xml += `    <ExtractedAt>${escapeXml(result.extracted_at.toString())}</ExtractedAt>\n`;
  xml += '  </Metadata>\n';
  
  xml += '  <PatientInformation>\n';
  if (data.patient_name) xml += `    <Name>${escapeXml(data.patient_name)}</Name>\n`;
  if (data.date_of_birth) xml += `    <DateOfBirth>${escapeXml(data.date_of_birth)}</DateOfBirth>\n`;
  xml += '  </PatientInformation>\n';
  
  if (data.diagnoses && data.diagnoses.length > 0) {
    xml += '  <Diagnoses>\n';
    data.diagnoses.forEach((diagnosis) => {
      if (typeof diagnosis === 'string') {
        xml += `    <Diagnosis>${escapeXml(diagnosis)}</Diagnosis>\n`;
      } else {
        xml += '    <Diagnosis>\n';
        xml += `      <Condition>${escapeXml(diagnosis.condition)}</Condition>\n`;
        if (diagnosis.icd_code) xml += `      <IcdCode>${escapeXml(diagnosis.icd_code)}</IcdCode>\n`;
        if (diagnosis.severity) xml += `      <Severity>${escapeXml(diagnosis.severity)}</Severity>\n`;
        if (diagnosis.date_diagnosed) xml += `      <DateDiagnosed>${escapeXml(diagnosis.date_diagnosed)}</DateDiagnosed>\n`;
        xml += '    </Diagnosis>\n';
      }
    });
    xml += '  </Diagnoses>\n';
  }
  
  if (data.medications && data.medications.length > 0) {
    xml += '  <Medications>\n';
    data.medications.forEach((med) => {
      if (typeof med === 'string') {
        xml += `    <Medication>${escapeXml(med)}</Medication>\n`;
      } else {
        xml += '    <Medication>\n';
        xml += `      <Name>${escapeXml(med.name)}</Name>\n`;
        if (med.dosage) xml += `      <Dosage>${escapeXml(med.dosage)}</Dosage>\n`;
        if (med.frequency) xml += `      <Frequency>${escapeXml(med.frequency)}</Frequency>\n`;
        if (med.route) xml += `      <Route>${escapeXml(med.route)}</Route>\n`;
        if (med.indication) xml += `      <Indication>${escapeXml(med.indication)}</Indication>\n`;
        xml += '    </Medication>\n';
      }
    });
    xml += '  </Medications>\n';
  }
  
  if (data.lab_values && Object.keys(data.lab_values).length > 0) {
    xml += '  <LabValues>\n';
    Object.entries(data.lab_values).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number') {
        xml += `    <LabValue name="${escapeXml(key)}">${escapeXml(String(value))}</LabValue>\n`;
      } else {
        const labValue = value as LabValue;
        xml += `    <LabValue name="${escapeXml(key)}">\n`;
        if (labValue.value) xml += `      <Value>${escapeXml(labValue.value)}</Value>\n`;
        if (labValue.reference_range) xml += `      <ReferenceRange>${escapeXml(labValue.reference_range)}</ReferenceRange>\n`;
        if (labValue.flag) xml += `      <Flag>${escapeXml(labValue.flag)}</Flag>\n`;
        if (labValue.date) xml += `      <Date>${escapeXml(labValue.date)}</Date>\n`;
        xml += '    </LabValue>\n';
      }
    });
    xml += '  </LabValues>\n';
  }
  
  if (data.procedures && data.procedures.length > 0) {
    xml += '  <Procedures>\n';
    data.procedures.forEach((proc) => {
      if (typeof proc === 'string') {
        xml += `    <Procedure>${escapeXml(proc)}</Procedure>\n`;
      } else {
        xml += '    <Procedure>\n';
        xml += `      <Name>${escapeXml(proc.name)}</Name>\n`;
        if (proc.date) xml += `      <Date>${escapeXml(proc.date)}</Date>\n`;
        if (proc.outcome) xml += `      <Outcome>${escapeXml(proc.outcome)}</Outcome>\n`;
        xml += '    </Procedure>\n';
      }
    });
    xml += '  </Procedures>\n';
  }
  
  if (data.allergies && data.allergies.length > 0) {
    xml += '  <Allergies>\n';
    data.allergies.forEach((allergy) => {
      if (typeof allergy === 'string') {
        xml += `    <Allergy>${escapeXml(allergy)}</Allergy>\n`;
      } else {
        xml += '    <Allergy>\n';
        xml += `      <Allergen>${escapeXml(allergy.allergen)}</Allergen>\n`;
        if (allergy.reaction) xml += `      <Reaction>${escapeXml(allergy.reaction)}</Reaction>\n`;
        if (allergy.severity) xml += `      <Severity>${escapeXml(allergy.severity)}</Severity>\n`;
        xml += '    </Allergy>\n';
      }
    });
    xml += '  </Allergies>\n';
  }
  
  if (data.vital_signs && Object.keys(data.vital_signs).length > 0) {
    xml += '  <VitalSigns>\n';
    Object.entries(data.vital_signs).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number') {
        xml += `    <VitalSign name="${escapeXml(key)}">${escapeXml(String(value))}</VitalSign>\n`;
      } else {
        const vitalSign = value as { value?: string; date?: string };
        xml += `    <VitalSign name="${escapeXml(key)}">\n`;
        if (vitalSign.value) xml += `      <Value>${escapeXml(vitalSign.value)}</Value>\n`;
        if (vitalSign.date) xml += `      <Date>${escapeXml(vitalSign.date)}</Date>\n`;
        xml += '    </VitalSign>\n';
      }
    });
    xml += '  </VitalSigns>\n';
  }
  
  if (data.risk_factors && data.risk_factors.length > 0) {
    xml += '  <RiskFactors>\n';
    data.risk_factors.forEach((risk) => {
      xml += `    <RiskFactor>${escapeXml(risk)}</RiskFactor>\n`;
    });
    xml += '  </RiskFactors>\n';
  }
  
  if (data.notes) {
    xml += '  <ClinicalNotes>\n';
    xml += `    ${escapeXml(data.notes)}\n`;
    xml += '  </ClinicalNotes>\n';
  }
  
  xml += '</MedicalExtraction>';
  
  const blob = new Blob([xml], { type: 'application/xml;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `medical-extraction-${result.document_id}.xml`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
