### 1 - Full Clinical Summary

**Prompt:**  
Summarize the following patient record into a concise clinical summary for a physician.  
Make sure to include diagnoses, medications, allergies, and recent lab results. Do not omit any critical medical information.  
[Copy or attach patient record]

**Ground Truth:** No single correct answer. Correctness is defined by inclusion of all key facts:
- All diagnoses listed in the record
- All current medications with dosage
- All documented allergies
- All abnormal lab results
- No hallucinated or extra conditions

**Verification Method:** Human evaluation  
Clinicians check whether all required fields are present and whether any incorrect or invented medical information appears.

**Primary Failure Mode:**  
Missing critical information (especially allergies, medications, or abnormal labs)

**Why this prompt matters:**  
This directly simulates real hospital usage where incomplete summaries could lead to unsafe clinical decisions such as prescribing contraindicated medications.

---

### 2 - Medication

**Prompt:**  
Extract all medications mentioned in the patient record, including dosage, frequency, and route of administration. If the patient is not currently under any treatment, explicitly state "No medication".  
[Copy or attach patient record]

**Ground Truth:** Yes - Exact list of medications exists in the record  
Correct output is a structured list of all current medications exactly as documented.  

**Verification Method:** Rule-based
- Exact match against medication names  
- Regex validation for dosage patterns (e.g., mg, ml, IU)  
- Checklist comparison against ground truth medication list

**Primary Failure Mode:**  
Hallucinated medications or incorrect dosage interpretation

**Why this prompt matters:**  
Medication errors are one of the highest-risk failure points in clinical summarization systems.

---

### 3 - Allergies

**Prompt:**  
List all patient allergies and indicate severity if available. If no allergies are present, explicitly state "No known allergies".  
[Insert or attach patient record]

**Ground Truth:** Yes - Allergy list is explicitly present in record  
Expected output must exactly reflect documented allergies, including severity notes.

**Verification Method:** Rule-based  
- Keyword match for allergy terms  
- Must not include allergies not present in record  
- Must explicitly include “No known allergies” if applicable

**Primary Failure Mode:**  
Omission of allergies or hallucinating allergies not in record

**Why this prompt matters:**  
Allergy omission is a critical patient safety risk, especially for drug administration.

---

### 4 - Timeline of Clinical Events

**Prompt:**  
Reconstruct a chronological timeline of the patient’s key clinical events, including admissions, diagnoses, procedures, and major test results.  
[Insert or attach patient record]

**Ground Truth:** No single correct answer  
Multiple valid outputs possible if ordering is correct and no events are missing or fabricated.

**Verification Method:** LLM-as-judge + Human evaluation  
- Correct chronological ordering
- Completeness of key events
- Absence of hallucinated events

**Primary Failure Mode:**  
Missing or added events and incorrect temporal ordering

**Why this prompt matters:**  
Clinical decision-making often depends on understanding progression over time (e.g., worsening labs or delayed diagnosis).

---

### 5 - Discharge Summary

**Prompt:**  
Generate a discharge summary for this patient suitable for transfer to another hospital. Include diagnosis, treatment course, medications at discharge, and follow-up recommendations.

**Ground Truth:** No single correct answer  
Correctness depends on faithful coverage of record without introducing new medical claims.

**Verification Method:** LLM-as-judge + Human evaluation  
- LLM checks structure completeness and internal consistency  
- Clinician verifies factual correctness and absence of hallucinations

**Primary Failure Mode:**  
Hallucination of treatment plans or follow-up recommendations not supported by record

**Why this prompt matters:**  
Discharge summaries are high-stakes documents used directly in continuity of care, making both hallucination and omission critical risks.