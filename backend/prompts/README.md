# Prompt Versioning

This directory contains versioned prompts for medical data extraction. Each prompt version is designed to improve extraction accuracy, completeness, and relevance for underwriting workflows.

## Version History

### v1.0.0 (Initial)
- **Released:** Initial implementation
- **Focus:** Basic medical data extraction
- **Structure:** Simple flat JSON schema
- **Performance Baseline:** Establishes baseline metrics

### v1.1.0 (Enhanced)
- **Released:** Iterative improvement
- **Improvements:**
  - Added reference ranges for lab values
  - Enhanced medication details (dosage, route, frequency)
  - Improved allergy severity tracking
  - Better clinical terminology normalization
- **Expected Impact:** +15% completeness, +10% accuracy

### v2.0.0 (Underwriting-Optimized)
- **Released:** Production-ready for underwriting
- **Major Changes:**
  - Nested JSON structure for complex data
  - Added risk factor identification
  - Enhanced diagnosis tracking (ICD codes, severity, dates)
  - Structured medications and procedures
  - Underwriting-specific focus
- **Expected Impact:** +25% completeness, +20% accuracy, better underwriting relevance

## Prompt Selection Strategy

- **Default:** v2.0.0 (latest production version)
- **A/B Testing:** Compare v1.1.0 vs v2.0.0 for new use cases
- **Rollback:** v1.1.0 available if issues detected in v2.0.0

## Experimentation Guidelines

1. **Test with control set:** Use consistent document set for comparison
2. **Track metrics:**
   - Extraction accuracy (manual validation)
   - Field completeness (% fields populated)
   - Processing time (ms)
   - Token usage (cost)
3. **Statistical significance:** Require p < 0.05 for version promotion
4. **Monitor in production:** Track success rates, user feedback

## Adding New Versions

1. Create `vX.Y.Z.txt` following semantic versioning
2. Document changes in this README
3. Run A/B test against current production version
4. Update default version in `PromptManager` after validation

## Naming Convention

- **Major (X):** Breaking changes to output schema or extraction approach
- **Minor (Y):** New features, improved instructions, non-breaking enhancements
- **Patch (Z):** Bug fixes, typo corrections, minor wording improvements
