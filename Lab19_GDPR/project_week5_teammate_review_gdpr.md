# GDPR Audit Review — job_search_automation

## Phase 1: Recognize (data, special categories, EU transfer)

### Personal data categories identified
The system processes a wide range of **candidate/job applicant personal data**, including:

- Identity and contact data (name, email, possibly phone)
- CV-derived professional history (employment, education, projects)
- Skills, languages, certifications
- Career preferences (target roles, locations, salary expectations, work authorization)
- Uploaded documents (CVs, supporting documents)
- Generated outputs (cover letters, application answers)
- Interaction data (recruiter messages, application tracker notes)
- Job-related inferred data (match scores, suitability assessments, ranking outputs)

It also processes **job-related data**, which is usually non-personal for GDPR purposes, but may become personal if linked to recruiters or small companies (not central here).

### Special-category data (Article 9)
Not explicitly stated, but **could potentially be inferred** from CVs and documents:
- Health status or disability (if disclosed in CV gaps or accommodations)
- Trade union membership, political engagement (rare but not possible in CVs or free-text documents)
- Ethnicity, nationality or religious views (if derived from name, visa/work authorization, previous work experience, cover/recommendation letters...)

Conclusion: **No intentional Article 9 processing, but meaningful inference risk exists via unstructured CV + LLM processing.**

### EU / non-EU data flows
- Explicit **cross-border transfer risk via OpenAI API**
- Likely processing outside EEA unless EU-region API contracts are confirmed
- Job data itself is not sensitive for transfers, but **candidate personal data is clearly transferred internationally**

Conclusion: **Yes, EU → non-EU transfer likely via API usage unless EU hosting is contractually guaranteed.**

---


## Phase 2: Personal Data and Role Map

### Personal Data Summary

| Data category | Source | Purpose(s) | Crosses EU border? | Special category? |
|--------------|--------|------------|---------------------|--------------------|
| Identity & contact data (name, email, possibly phone) | Candidate input / CV upload | Account creation, job matching, application generation | Possibly (via OpenAI API) | No (but could enable inference) |
| Employment history (roles, employers, dates) | CV / uploaded documents | Job matching, suitability scoring, CV parsing | Possibly | No (but could enable inference) |
| Education, certifications, skills | CV / user input | Job matching, ranking, application tailoring | Possibly | No (but could enable inference) |
| Job preferences (salary, location, work authorization) | User input | Filtering and recommendation | Possibly | No |
| Application documents (CV, cover letters, forms) | System-generated + user-provided | Application submission support | Possibly | No |
| Generated outputs (cover letters, answers, summaries) | LLM API output | Application automation and personalization | Possibly | No |
| Match scores / rankings / suitability assessments | AI model output | Profiling, ranking, job prioritisation | Possibly | No (but profiling risk high) |
| Recruiter messages / application notes | Job platforms / user input | Application tracking and communication | Possibly | No |
| Job listings / job metadata | Job boards (external sources) | Matching and extraction | No (usually public data) | No |

---

### Role Map

| Entity | Role | Processing activity | DPA needed? |
|--------|------|---------------------|-------------|
| Client (system operator / app owner) | Controller | Defines purposes: job matching, profiling, application generation, tracking | Yes |
| Candidate / user | Data subject (or sole controller in household use case) | Provides CV, preferences, and uses system outputs | No |
| OpenAI API | Processor | CV parsing, extraction, job matching support, text generation, scoring assistance | Yes |
| Local application (Python system) | Processor (under controller instruction) | Data orchestration, storage, workflow execution | Yes (internal governance equivalent if in-house) |
| Cloud/storage provider (if any external hosting) | Processor | Data storage of structured JSON and outputs | Yes |
| Job boards / LinkedIn / external job APIs | Independent controllers | Provide job listings and application endpoints | No |

---

### International transfer note
- OpenAI API likely involves **EU → US data transfer**
- Requires:
  - SCCs (Standard Contractual Clauses)
  - Transfer Impact Assessment (TIA)
  - Technical safeguards (pseudonymisation/minimisation recommended)

- No evidence provided of existing transfer mechanism in brief

---

## Phase 3: Clarifying questions

### Q1 — Where exactly is OpenAI processing happening?
**Why it matters:** determines GDPR transfer mechanism (SCCs, adequacy, or none), and whether supplementary safeguards are required.

- **If unanswered assumption:** US-based processing under Standard Contractual Clauses (SCCs), requiring transfer risk assessment.

---

### Q2 — Is the system used only by a single individual or offered as a service to others?
**Why it matters:** determines whether GDPR applies fully (controller obligations) or falls under household exemption.

- **If unanswered assumption:** system is a SaaS-style product → full GDPR applicability.

---

### Q3 — Are AI-generated outputs used to influence final application submission decisions automatically?
**Why it matters:** triggers Article 22 automated decision-making and DPIA requirement severity.

- **If unanswered assumption:** human reviews all applications before submission, but AI strongly influences ranking.

---






## Phase 4: GDPR Audit Report

### Section 1: System Summary

The system is a job search and application automation tool that processes candidate data to support CV ingestion, job matching, and generation of tailored application materials. It ingests structured and unstructured personal data from CVs, user inputs, job descriptions, and application forms, and uses an LLM API to extract, normalize, and generate outputs such as cover letters, application answers, and suitability scores. The system also tracks applications and stores derived data locally in JSON files and Markdown exports. A key feature is automated ranking and matching of candidates to job listings, with human review before final submission. Some processing involves third-party APIs, including OpenAI, which may involve cross-border data transfers outside the EU.

---

### Section 2: Data and Role Map

**Personal data categories:**  
- Identity and contact data (name, email)
- Employment history and CV content
- Education, skills, certifications, languages
- Job preferences (salary, location, role type, work authorization)
- Application materials (cover letters, form answers)
- Behavioral inference data (match scores, ranking outputs)
- Recruiter messages and notes
- Job application metadata (status tracking)

**Controller / processor split:**  
- Client (system operator): **Controller**
- Candidate/user: **Data subject (sometimes sole user depending on deployment model)**
- OpenAI API: **Processor**
- Local storage system: **Processor under controller instruction**
- Any cloud infrastructure (if used): **Processor**
- Job boards: **Independent controllers (no direct candidate data processing by system)**

**International transfers:**  
- OpenAI API likely involves **EU → US data transfer**
- No explicit evidence of adequacy decision or SCCs provided in brief
- Transfer mechanism: **assumed SCCs required but not confirmed**

---

### Section 3: Compliance Findings

**Finding 1 — Lawful Basis for Profiling and Scoring**
* **Severity:** Significant
* **Description:** Multiple processing activities involve profiling (CV analysis, job matching, ranking, suitability scoring). The brief does not clearly assign a lawful basis per processing purpose, particularly for automated scoring.
* **Recommended action:** Define lawful basis per activity:
    * Contract or legitimate interests for core job-matching functionality
    * Conduct a Legitimate Interests Assessment (LIA) for profiling and ranking
* **Escalation needed:** Yes — Legal / DPO review required

---

**Finding 2 — Article 22 Automated Decision-Making Risk**
* **Severity:** Significant
* **Description:** The system produces ranking and suitability scores that may significantly influence employment outcomes. Even with human review, there is a risk of “automation bias” leading to de facto automated decision-making.
* **Recommended action:** Implement safeguards:
    * Meaningful human review (not rubber-stamping)
    * Right for user to contest or override AI-generated ranking
    * Explainability layer for scoring outputs
* **Escalation needed:** Yes — DPO and HR/legal coordination required

---

**Finding 3 — International Data Transfers (OpenAI API)**
* **Severity:** Blocking
* **Description:** Personal data is processed via OpenAI API, which likely involves transfer outside the EEA. No evidence is provided of SCCs, transfer impact assessment, or supplementary safeguards.
* **Recommended action:**  
    * Execute SCCs with OpenAI (or verify adequacy mechanism if available)
    * Conduct Transfer Impact Assessment (TIA)
    * Implement data minimisation before API calls (pseudonymisation where possible)
* **Escalation needed:** Yes — Legal + Procurement

---

**Finding 4 — Purpose Limitation and Secondary Use Risk**
* **Severity:** Significant
* **Description:**  
CV and application data originally collected for job search support is reused for AI scoring, ranking, and generation of derived behavioral assessments. This may exceed original user expectations.
* **Recommended action:**  
    - Update privacy notice to explicitly include profiling and AI scoring
    - Ensure compatibility assessment under Article 6(4) GDPR
    - Separate data uses: application support vs profiling vs model generation
* **Escalation needed:** Yes — DPO

---

**Finding 5 — DPIA Requirement Not Documented**
* **Severity:** Blocking
* **Description:** The system involves systematic profiling, large-scale CV processing, and automated ranking affecting employment opportunities. This triggers multiple EDPB DPIA criteria, but no DPIA is documented.
* **Recommended action:**  
    - Conduct DPIA before deployment
    - Include risk mitigation for Article 22, transfers, and profiling bias
    - Involve DPO in approval
* **Escalation needed:** Yes — Mandatory DPO sign-off

---

**Finding 6 — Special Category Data Inference Risk**
* **Severity:** Significant
* **Description:** CVs and free-text documents may contain or allow inference of Article 9 data (health, ethnicity, religion, trade union membership). LLM processing increases inference risk.
* **Recommended action:**
    - Implement filtering or minimisation of sensitive fields
    - Avoid using sensitive attributes in scoring models
    - Define explicit prohibition on using inferred Article 9 data in ranking
* **Escalation needed:** Yes — Legal + AI governance

---

### Section 4: GDPR Obligations Checklist

| Obligation | Assessment | Note |
|------------|------------|------|
| Lawful basis identified for each processing purpose | Gap identified | Not mapped per processing activity |
| Purpose limitation respected | Gap identified | Profiling use may exceed original collection purpose |
| Data minimisation | Cannot determine | Depends on preprocessing and API payload design |
| Controller/processor roles mapped and DPAs in place | Gap identified | OpenAI DPA assumed but not evidenced |
| International transfer mechanism documented | Gap identified | SCCs/TIA not confirmed |
| DPIA conducted if required | Gap identified | Likely required but not performed |
| Article 22 safeguard in place | Gap identified | Human review exists but not structurally guaranteed |
| Privacy notice covers AI processing | Cannot determine | Not provided |
| Data subject rights operationalised | Gap identified | No workflow described |

---

### Section 5: Overall Recommendation

**Proceed with conditions**  
The system can proceed only after GDPR foundational controls are implemented, particularly lawful basis documentation, DPIA completion, and formal international transfer safeguards.

**Rationale**  
The system is viable but currently lacks essential compliance architecture for profiling, cross-border transfers, and automated decision-making safeguards. These are not optional enhancements but legal prerequisites under GDPR.

---

### Section 6: What this report is not

This report is not a legal opinion, not a DPIA, and not a certification of compliance. It is a preliminary GDPR risk assessment based on a system brief. Formal legal review and DPO approval are required before any production deployment involving personal data.


---

## Phase 5: Debrief
This debrief shows that when you do GDPR self-assessments, the biggest blind spots are usually not the obvious risks but the hidden assumptions. It’s easy to say things like “we’ll handle transfers properly” or “humans review everything,” without noticing that there’s no real evidence or process behind it yet. An outside review is especially useful for catching these gaps, because it forces you to check whether what you think is happening is actually documented and enforceable.