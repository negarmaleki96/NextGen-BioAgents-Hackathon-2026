PASS_1_IDENTITY = """Extract device identity and intended use from the source documents.
Return JSON with this structure for each field:
{"value": <value or null>, "confidence": 0.0-1.0, "provenance": "explicit|inferred|missing", "snippet": "<quote if explicit>", "notes": "<optional>"}

Fields:
- device_trade_name (string)
- device_common_name (string)
- model_numbers (list of strings)
- product_code (string, 3-letter FDA code if mentioned)
- regulation_number (string)
- device_class (string: 1, 2, or 3)
- advisory_committee (string)
- submission_type (Traditional, Special, or Abbreviated)
- indications_for_use (string)
- intended_use_population (string)
- intended_use_environment (string)
- contraindications (string)
"""

PASS_2_TECHNOLOGY = """Extract technology and design characteristics.
Return JSON with same per-field structure as before.

Fields:
- principle_of_operation (string)
- energy_source (string)
- materials (list of strings)
- software_present (boolean)
- cybersecurity_features (string)
- sterilization (string)
- shelf_life (string)
- components_accessories (string)
- patient_contact (boolean — does device contact patient?)
- electrical_powered (boolean)
"""

PASS_3_TESTING = """Extract testing, standards, labeling, and administrative info.
Return JSON with same per-field structure.

Fields:
- bench_testing (string summary)
- biocompatibility (string summary)
- emc (string summary)
- software_vv (string summary)
- clinical_data (string summary)
- risk_analysis (string summary)
- design_controls (string summary)
- labeling_draft (string summary)
- ifu_draft (string summary)
- consensus_standards_cited (list of strings)
- applicant_name (string)
- contact (string)
- manufacturing_sites (string)
"""

PASS_4_PREDICATES = """Extract predicate device hints and competitive references.
Return JSON with same per-field structure.

Fields:
- user_predicate_mentions (list — K-numbers, device names, or companies mentioned as predicates)
- competitive_devices (list of similar marketed devices mentioned)
"""
