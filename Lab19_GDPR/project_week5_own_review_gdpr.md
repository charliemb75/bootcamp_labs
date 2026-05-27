# GDPR Audit Pack - Vehicle Test Report Automation (n8n Workflow)

## Data Processing Brief (for DPO)

This system automates the ingestion and analysis of vehicle component test reports submitted via email to a dedicated inbox (e.g., test_reports@company.com). The workflow extracts structured “issues” from engineering test reports and enriches them using AI-based analysis, including image interpretation, before storing results in a Google Drive-based database and notifying stakeholders via Slack.

### 1. Personal data processed
The system may process the following categories of data:

- Sender email addresses (engineering staff or testers submitting reports)
- Names or identifiers contained in test reports or email signatures
- Images attached to reports (may include identifiable individuals, workshop environments, license plates, or employee badges)
- Free-text issue descriptions written by engineers or testers (may contain names or contextual identifiers)
- AI-generated derived content (issue classification, causal analysis, risk assessment)
- Metadata from emails (timestamps, routing information, subject lines)

### 2. Data sources
- Incoming emails and attachments (primary source)
- Test report templates (input_template.md filled by engineers)
- Attached photos from testing environments
- Existing issue database in Google Drive
- Slack notifications (downstream dissemination channel)

### 3. Purpose of processing
- Extract and structure engineering test issues from unstructured reports
- Classify and semantically match issues against existing database entries
- Enrich issue records with AI-generated technical analysis (causes, consequences, mitigation suggestions)
- Maintain a centralized historical database of recurring vehicle component issues
- Notify stakeholders of new or updated issues

### 4. Processors involved
- n8n workflow system (orchestration layer)
- OpenAI API (text extraction, semantic matching, image analysis, generation of reports)
- Google Drive (storage of issue database and reports)
- Slack API (notifications to stakeholders)
- Email provider (ingestion channel)

### 5. Data storage and processing location
- Primary storage: Google Drive (location depends on tenant configuration; likely EU or US-based cloud region)
- Processing: n8n execution environment (location unknown unless self-hosted in EU)
- OpenAI API: processing occurs in external cloud infrastructure (non-EU transfer likely)
- Slack: US-based infrastructure
→ Therefore, personal data is likely transferred outside the EU/EEA

### 6. Automated decision-making / impact
The system does not make legal or employment decisions, but it does:
- Classify and match engineering issues
- Prioritize whether issues are “new” or “existing”
- Influence engineering follow-up actions via Slack notifications

While not legally significant in GDPR Article 22 terms, outputs may indirectly affect engineering prioritization, resource allocation, and safety-related design decisions.

---

# Phase 1 — Personal Data Inventory

| Data category | Source | Purpose(s) | Retention period | Crosses EU border? |
|---|---|---|---|---|
| Email addresses | Incoming email system | Identify sender, routing, traceability | TBD (likely linked to report lifecycle) | Yes (likely via Slack/OpenAI) |
| Names / identifiers in reports | Engineers/testers | Contextual understanding of issue reports | Same as report retention | Possibly |
| Issue report text | Email body / markdown template | Issue extraction, classification, storage | Long-term engineering database retention | Yes (OpenAI processing) |
| Images from test reports | Attachments | Visual analysis of component issues | Stored with issue record | Yes (OpenAI + Slack sharing) |
| Metadata (timestamps, subjects) | Email system | Traceability and indexing | Report lifecycle | Yes (platform-dependent) |
| AI-generated analysis | OpenAI output | Engineering decision support | Stored in database | Yes |

**Purpose overlap flag:**  
Test reports originally collected for engineering QA documentation are being reused for AI-driven classification, semantic matching, and causal inference. This is a functional extension beyond passive storage.

---

# Phase 2 — Role Map

| Entity | Role | Processing activity | DPA in place? |
|---|---|---|---|
| Client (vehicle manufacturer / engineering org) | Controller | Defines purpose, collects reports, uses outputs | TBD (should exist) |
| n8n workflow | Processor (or technical intermediary) | Orchestrates processing pipeline | Required |
| OpenAI API | Processor | Text + image analysis, generation | Required |
| Google Drive | Processor | Storage of issue database | Required |
| Slack | Processor | Notifications to stakeholders | Required |
| Email provider | Processor | Ingestion of reports | Required |

**International transfers:**  
Likely SCCs required for OpenAI and Slack (US-based processing). Google Drive depends on tenant region but commonly requires SCCs or adequacy assessment.

---

# Phase 3 — Lawful Basis Assessment

| Purpose | Lawful basis | Justification | Flag |
|---|---|---|---|
| Engineering issue processing | Legitimate interests | Necessary for product safety, quality control, and defect tracking | Yes (LIA required) |
| AI-based issue classification & matching | Legitimate interests | Efficiency and consistency in defect management | Yes (high sensitivity due to profiling + automation) |
| Image analysis of defects | Legitimate interests | Required for technical evaluation of component failures | Yes (image data risk) |
| Long-term issue database storage | Legal obligation / legitimate interests | Product liability and safety traceability requirements | Possibly legal obligation |
| Stakeholder notification (Slack) | Legitimate interests | Operational communication of engineering risks | Low risk |

**LIA note:**  
Must assess necessity (could manual QA suffice?), proportionality (AI vs human inspection), and impact on individuals (limited, but includes employees and potentially identifiable persons in images).

---

# Phase 4 — Risk and Rights Analysis

### Special category data (Article 9)
Not intentionally processed, but images may inadvertently reveal sensitive data such as biometric identifiers (faces), health/safety incidents, or worker identity badges. No explicit Article 9 condition is currently relied upon, so strict minimisation and redaction should be applied to images before processing.

### Automated decision-making (Article 22)
No legally significant automated decisions are made about individuals; however, the system automates classification and prioritisation of engineering issues. Human engineers still review outputs before action. Article 22 risk is low but explainability is still relevant for accountability and safety traceability.

### DPIA trigger
A DPIA is required. Criteria triggered include: innovative AI technology, systematic processing of potentially identifiable data, large-scale technical dataset aggregation, and cross-border data transfers. If images contain personnel or identifiable contexts, monitoring criteria may also apply.

### Data subject rights friction
- Access requests: difficulty reconstructing AI-generated outputs linked to individuals in images/text
- Erasure requests: complex due to propagation into issue database and historical logs
- Objection: low likelihood but possible from employees if personal data appears in reports

### Controller / processor split
Client is controller; all vendors are processors. Clear DPA chain required across OpenAI, Slack, Google, and n8n infrastructure.

---

# Phase 5 — Law Stacking Check

- **AI Act cross-check:** Likely minimal or limited risk AI system (engineering support tool). No high-risk classification unless used for safety-critical automated decisions. GDPR imposes stronger obligations than AI Act here.
- **ePrivacy check:** Applies indirectly via email processing and Slack communications; consent not required for internal business communications but confidentiality rules apply.
- **Data Act check:** Not applicable (no IoT product data access rights or cloud switching obligations relevant).

---

# Phase 6 — Compliance Memo (to DPO)

**Bottom line: Proceed with conditions.**  
The system is acceptable for deployment only if cross-border transfer mechanisms, DPIA, and strict data minimisation controls are implemented before any production use.

The highest compliance risk arises from uncontrolled personal data exposure in images and free-text engineering reports. While the system is primarily technical in nature, it processes identifiable personal data (emails, names, images) and therefore fully falls under GDPR scope.

**Top three actions:**
1. Conduct a DPIA before deployment, specifically addressing image processing, cross-border transfers, and AI-based semantic matching risks.  
2. Implement strict data minimisation: redact or exclude personal identifiers (names, faces, metadata) from images and reports before sending to OpenAI or Slack.  
3. Put SCCs and DPAs in place with OpenAI, Slack, Google, and ensure data residency and transfer impact assessments are completed.

**Residual risks:**
- Images may still inadvertently contain identifiable individuals or sensitive contextual data despite preprocessing controls.  
- AI-generated classifications may introduce traceability issues when reconstructing decision logic for audit or legal review.  
- Cross-border transfers to US-based processors remain a structural risk that cannot be fully eliminated, only mitigated.

The client should treat this as a regulated data processing pipeline rather than a simple automation workflow.

---

# Stretch — Data Protection by Design Checklist

| Design principle | Current state | Pass / Fail / Unknown |
|---|---|---|
| Data minimisation | System processes full emails, metadata, and images without clear filtering | Fail |
| Purpose binding | Data reused for AI analysis beyond original reporting purpose | Fail |
| Access controls | Not clearly defined across n8n, Drive, Slack, OpenAI | Unknown |
| Retention enforcement | No explicit automated deletion policy described | Fail |
| Subject rights workflow | No defined mechanism for access/erasure requests across pipeline | Unknown |
| Incident response | No documented breach detection / 72-hour notification process | Unknown |

**Required changes:**
- Introduce pre-processing layer to strip personal data before AI ingestion  
- Define strict retention schedules per data type (emails, images, logs)  
- Implement role-based access controls across all tools  
- Establish DPIA-backed incident response and logging framework  