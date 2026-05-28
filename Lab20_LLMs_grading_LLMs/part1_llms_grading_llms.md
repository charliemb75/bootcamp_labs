# Benchmark Audit & Evaluation Design

## Step 1 — Client Scenario

**Chosen option:** Healthcare
* A hospital wants to summarize patient records
* Requirements: Must preserve critical medical information
* Key concerns: Accuracy, completeness, medical terminology

A regional hospital network wants to deploy an LLM system that summarizes patient records to help doctors quickly review medical histories, diagnoses, medications, and recent treatments. The primary requirement is that the summaries preserve all critical medical information with high accuracy and completeness while using correct medical terminology and maintaining clinical context. Key concerns include omission of important details such as allergies or medications, hallucinated diagnoses or treatments, and incorrect interpretation of specialized medical language that could lead to unsafe clinical decisions.

## Step 2 — Find & Critique 3 Existing Benchmarks

### 1 - PubMedQA

**Year:** 2019  
**Source:** Jin et al., "PubMedQA: A Dataset for Biomedical Research Question Answering"  
https://arxiv.org/abs/1909.06146

**Why it seemed relevant:**  
PubMedQA evaluates biomedical comprehension using research abstracts and clinical evidence. It is useful for testing whether a model can correctly interpret nuanced medical information and avoid hallucinating unsupported conclusions.

**Contamination risk:** Medium - Some overlap possible  
**Explanation:** PubMed abstracts are likely included in training data, but exact QA pairs may not be memorized.

**Saturation risk:** Medium - Some models perform well  
**Explanation:** Models have improved substantially, but biomedical inference remains difficult.

**Format:** Multiple Choice, Free-form text

**Verdict:** Use it as-is

---

### 2 - Needle-in-a-Haystack

**Year:** 2023  
**Source:** Greg Kamradt, "LLM Test: Needle in a Haystack"  
https://github.com/gkamradt/LLMTest_NeedleInAHaystack  

**Why it seemed relevant:**  
Needle-in-a-Haystack evaluates whether a model can reliably retrieve a small but critical piece of information hidden within very long context. This directly mirrors patient record summarization, where essential details such as allergies, medications, or prior diagnoses may be buried deep within lengthy clinical notes.

**Contamination risk:** Low - Model likely not trained on this data  
**Explanation:** The benchmark is synthetic and dynamically generated, making direct memorization unlikely.

**Saturation risk:** Low - Benchmark is challenging  
**Explanation:** Even state-of-the-art models struggle with consistent retrieval in long-context settings, especially when irrelevant information dominates.

**Format:** Free-form text, Other: Long-context retrieval

**Verdict:** Use it as-is

---

### 3 - HaluEval

**Year:** 2023  
**Source:** Li et al., "HaluEval: A Large-Scale Hallucination Evaluation Benchmark"  
https://arxiv.org/abs/2305.11747  

**Why it seemed relevant:**  
HaluEval is designed to measure hallucination behavior in large language models, i.e., the tendency to generate plausible but ungrounded or incorrect information. This is critical in medical record summarization, where fabricated diagnoses, medications, or clinical details could directly impact patient safety.

**Contamination risk:** Medium - Some overlap possible  
**Explanation:** Portions of the dataset are publicly available and may have been included in training corpora, but exact evaluation instances are unlikely to be memorized.

**Saturation risk:** Low - Benchmark is challenging  
**Explanation:** Hallucination reduction remains an open problem, particularly in high-stakes domains like healthcare.

**Format:** Multiple Choice, Free-form text

**Verdict:** Use it as-is

## Step 3 — Write 5 Evaluation Prompts

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
Extract all medications mentioned in the patient record, including dosage, frequency, and route of administration.  
[Copy or attach patient record]

**Ground Truth:** Yes - Exact list of medications exists in the record  
Correct output is a structured list of all medications exactly as documented.

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

## Step 4 - Design your Judge

**Chosen prompt:** Timeline of Critical Events

### Task Description:
You are evaluating a model that has been asked to reconstruct a chronological timeline of key clinical events from a patient record.

The model output should summarize and order events such as admissions, diagnoses, procedures, lab results, and treatment changes in a medically accurate timeline.  

The goal is to ensure that the timeline is both **complete and temporally correct**, without introducing hallucinated or unsupported events.

---

### Evaluation Criteria:

1. **Completeness of Clinical Events:**  
   The response includes all major clinical events present in the source record (e.g., admissions, diagnoses, procedures, significant lab changes, medication changes).

2. **Temporal Correctness:**  
   Events are ordered correctly in time, with no incorrect sequencing or contradictions in the timeline.

3. **Factual Faithfulness (No Hallucination):**  
   The response does not introduce any events, diagnoses, or treatments not explicitly supported by the patient record.

---

### Reasoning Steps:

**Step 1:**  
Check the source patient record and extract all clinically relevant events that should appear in the timeline.

**Step 2:**  
Compare the model’s output against the extracted event list to determine:
- Missing events (omissions)
- Extra events (hallucinations)

**Step 3:**  
Verify chronological ordering:
- Are events in correct sequence?
- Are there any temporal contradictions (e.g., treatment before diagnosis)?

**Step 4:**  
Aggregate findings into criterion-level judgments and assign an overall score.

---

### Output Format:

```json
{
  "score": 1-5,
  "reasoning": "Explanation of how the score was determined, including missing or hallucinated events and ordering issues.",
  "criteria_met": {
    "completeness_of_clinical_events": true/false,
    "temporal_correctness": true/false,
    "factual_faithfulness": true/false
  }
}
```
---
### Bias analysis
A key hidden bias in this judge design is the assumption that clinical records are always structured and unambiguous. In reality, medical notes often contain fragmented, redundant, or temporally vague information (e.g., “patient previously treated last winter”), which may cause the judge to unfairly penalize valid but imprecise model outputs. Another bias is toward Western clinical documentation norms, which may not generalize well across hospitals or countries with different record-keeping styles.

There is also a potential language bias: if patient records or model outputs include non-English terms, abbreviations, or shorthand, the judge may incorrectly interpret them as missing or incorrect information. Additionally, style bias may favor overly detailed or structured timelines even when a concise summary would be clinically acceptable.

---

### Calibration Strategy

To calibrate the judge, I would first create a gold-standard evaluation set of patient records with clinician-annotated timelines. These would serve as reference examples for expected completeness and ordering granularity. The judge’s scoring would be tested against clinician ratings to ensure alignment, particularly focusing on sensitivity to omissions versus harmless paraphrasing differences.

Edge cases should include:
* Ambiguous timing (e.g., “recently,” “last month”)
* Repeated or chronic conditions appearing multiple times
* Partially missing documentation

If the judge is too strict, it will over-penalize minor omissions or formatting differences; in that case, thresholds should be relaxed for “minor completeness errors” that do not affect clinical meaning. If too lenient, additional constraints should be added requiring explicit event-level matching and stricter hallucination detection rules. Regular calibration against clinician feedback loops is essential to maintain reliability in a high-stakes medical setting.

## Step 5 - 1-Page "Evaluation Memo"

**TO:** Hospital X Digital Health Team  
**FROM:** Carlos Martínez Boto - AI Consultant  
**DATE:** 2026-05-28  
**SUBJECT:** LLM Evaluation Results - Clinical Patient Record Summarization System  

### Executive Summary  
We evaluated two large language models (Model A and Model B) for clinical patient record summarization with a focus on accuracy, completeness, and hallucination risk. The goal was to determine which system best preserves critical medical information such as diagnoses, medications, allergies, and clinical timelines in long electronic health records.

Overall, Model B demonstrated stronger performance in completeness and long-context retention, while Model A showed slightly better fluency but higher omission risk. Both models require additional safety constraints before clinical deployment.

---

### Methodology  
The evaluation combined public medical and reasoning benchmarks (PubMedQA, HaluEval) with long-context and retrieval-focused tests (Needle-in-a-Haystack), along with a custom hospital-style dataset simulating real electronic health records. We also included structured prompt-based evaluations targeting medication extraction, allergy detection, discharge summarization, and clinical timeline reconstruction.

Model outputs were assessed using a hybrid approach: rule-based checks for structured fields (e.g., medications, allergies), and LLM-as-judge evaluation for free-form outputs such as summaries and timelines. Human clinician review was used for a subset of cases to validate safety-critical judgments, particularly around hallucinations and missing information.

Two models were tested under identical prompting conditions with temperature control and identical context windows. Evaluation focused on both benchmark performance and real-world clinical fidelity rather than benchmark-only accuracy.

---

### Results  
Model B outperformed Model A on long-context retention tasks, particularly in the Needle-in-a-Haystack evaluation, where it consistently retrieved critical details embedded deep within patient records. It also showed lower hallucination rates in HaluEval-based testing, producing fewer unsupported clinical assertions.

Model A performed comparably on PubMedQA-style reasoning tasks and produced more fluent, well-structured summaries. However, it showed higher rates of omission in medication and allergy extraction tasks, indicating weaker reliability for safety-critical completeness requirements.

Across the custom clinical timeline task, Model B achieved higher temporal consistency and fewer missing events. Model A occasionally misordered events or omitted intermediate clinical steps, especially in longer records.

---

### Caveats & Limitations  
These results are based on a mixture of public benchmarks and synthetic clinical simulations, which may not fully reflect real hospital documentation complexity. Benchmark contamination is possible for PubMedQA and HaluEval, potentially inflating absolute performance scores. Additionally, synthetic long-context tests may not capture real-world noise, abbreviations, or inconsistent physician documentation styles.

LLM-as-judge evaluations introduce additional uncertainty, particularly in subjective assessments of completeness and clinical relevance. While human review was used for calibration, it was limited in scope due to resource constraints, and thus some evaluation variance should be expected.

---

### Recommendation  
Under the current evaluation conditions, Model B is recommended for pilot deployment in clinical summarization tasks due to its stronger performance in completeness, long-context retention, and hallucination resistance. However, both models should be constrained with additional guardrails and post-processing validation before production use. Confidence in this recommendation is moderate, pending validation on real-world hospital data.

---

### Additional metrics  
Beyond accuracy, Model B exhibited slightly higher token usage (approximately +12%) and marginally higher latency, though both models remained within acceptable clinical response-time thresholds. Estimated operational cost differences are small but may scale significantly at hospital-wide deployment volumes. From an environmental standpoint, Model B’s higher compute usage should be considered in large-scale continuous inference settings, though this is offset by its improved safety profile.

## Step 6 - Reflection

### Question 1: What would change if the client data was in French?

If the clinical data were in French, the evaluation design would need to shift significantly to ensure linguistic and medical equivalence. Many existing benchmarks such as MMLU, MedQA, or PubMedQA are English-centric, so their direct use would become less reliable. I would introduce multilingual medical benchmarks such as French-language clinical QA datasets (where available) and translate or adapt a subset of existing benchmarks using controlled human-validated translation pipelines. However, translation alone is risky because subtle clinical meaning can be lost or distorted, especially for medication instructions and diagnostic nuance.

New challenges would include handling French clinical abbreviations, regional medical terminology differences (e.g., France vs. Canada francophone documentation), and potential degradation in model performance due to reduced training representation. Additionally, hallucination detection becomes harder because LLM-as-judge systems are often less reliable in non-English contexts unless explicitly multilingual. To address this, I would use bilingual clinician reviewers and back-translation checks to validate semantic fidelity.

---

### Question 2: Client asks "is this model AGI-level?"

**AGI implies broad human-level intelligence across domains**, which is far beyond the scope of this highly task-specific evaluation. Although the model demonstrates robust performance across clinical tasks without failure in safety-critical conditions, **high performance on medical QA or summarization tasks does not generalize to general intelligence**.

To properly assess something closer to “AGI-level,” we would need a far broader evaluation suite covering cross-domain reasoning, long-horizon planning, tool use, adaptation to unseen tasks, and consistent real-world decision-making under uncertainty.

---

### Question 3: What is the one thing you could not evaluate without a human, and why?

The most critical aspect that cannot be fully evaluated without humans is **clinical safety judgment in ambiguous or incomplete cases**. This includes determining whether a summary is “clinically safe enough” when information is missing, ambiguous, or indirectly implied in the patient record. These decisions require contextual understanding of medical risk, institutional practice, and acceptable levels of uncertainty, which cannot be reliably encoded in rule-based systems or fully delegated to LLM-as-judge models.

Rule-based systems fail here because they cannot interpret nuanced clinical meaning, and LLM judges may hallucinate or inconsistently weight risks depending on phrasing. For example, omitting a medication might be harmless in one context but life-threatening in another, depending on comorbidities not explicitly stated.

In practice, human evaluation would be incorporated through structured clinician review panels, sampling high-risk cases (e.g., ICU patients, polypharmacy, allergy-heavy records), and using annotated rubrics for omission severity, hallucination risk, and clinical usability. These human judgments would then be used to calibrate automated evaluators, ensuring alignment between model metrics and real-world patient safety expectations.