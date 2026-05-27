# GDPR Audit Pack - Carlos Martínez Boto

## Audit Worksheet

### Transition Note
This case concerns an AI-assisted employee promotion and leadership assessment system. Under the EU AI Act, the system would likely qualify as a High-Risk AI system because it is used in employment-related decision-making involving promotion, role allocation, and employee evaluation. The scenario is particularly significant for GDPR analysis because it combines profiling, performance monitoring, inferred behavioural assessments, and potentially automated decision-making affecting employees’ professional opportunities.

---

## Phase 1: Fact Pattern

A company plans to deploy an AI-based internal promotion ranking system for assistant manager and leadership-track candidates. The system processes employee personal data including sales performance metrics, attendance and absence records, disciplinary history, customer complaints, training completion records, manager evaluations, and recorded interview responses. Employees affected are existing staff applying for promotions, leadership development programs, or higher-responsibility shifts. The company intends to use a US-based AI vendor providing cloud-hosted ranking and scoring infrastructure, with HR personnel accessing recommendations through a web dashboard hosted partly in the United States. The AI system generates candidate reliability and leadership suitability scores, automatically deprioritizes certain candidates, and produces ranked recommendations that HR managers generally follow unless they document a reason to override the output. The system therefore influences employment progression decisions with potentially significant professional effects on employees.

---

## Phase 2: Mini GDPR audit worksheet
### Section A — Data Map

| Field | Your Answer |
|---|---|
| Categories of personal data | Employee identification data, employment records, sales metrics, attendance and absence records, disciplinary records, customer complaint history, training completion records, manager comments, interview recordings, inferred behavioural/reliability assessments |
| Sources (where data comes from) | HR systems, store performance systems, training platforms, internal disciplinary records, customer service systems, recorded interviews, manager submissions |
| Purpose(s) — one row per purpose | 1. Rank promotion candidates  2. Standardize leadership assessments across stores  3. Identify employees for leadership training  4. Reduce perceived promotion risk and inconsistent management outcomes |
| Lawful basis per purpose — or TBD — legal review | Legitimate interests — employer has legitimate interest in workforce management and consistent promotion evaluation; balancing test required due to employee power imbalance and profiling concerns |
| Retention period per purpose | TBD — legal review; recommended: raw assessment data retained 12–24 months, audit logs retained for compliance purposes only, recordings minimized and deleted after review cycle unless legally required |
| Recipients and sub-processors | Internal HR teams, regional management, US-based AI vendor, cloud hosting providers, analytics sub-processors |
| International transfers and transfer mechanism | Transfer from EU/EEA to United States through SCCs (Standard Contractual Clauses) and supplementary transfer safeguards; vendor DPA required |

---

### Section B — Risk and Rights

**Are any special-category data present or inferable from the outputs (Article 9)?**  
Potentially yes. Absence records, disciplinary notes, manager comments, or interview responses may indirectly reveal health conditions, disability status, union activity, ethnicity, religious practices, or mental health indicators. The AI may also infer behavioural or psychological traits linked to protected characteristics.

**Is there automated decision-making with legal or similarly significant effects (Article 22)? If yes, what safeguard applies?**  
Yes, likely. Although HR managers formally approve decisions, the company intends to rely primarily on AI-generated rankings and only override with documented justification. This creates a strong risk that the process constitutes automated decision-making with similarly significant employment effects. Safeguards should include meaningful human review, employee contest rights, explanation procedures, and documented non-automated override authority.

**Is a DPIA required? Use the EDPB's nine criteria: explain which apply and why.**  
Yes, a DPIA is mandatory. Relevant EDPB criteria include: evaluation/scoring of employees, automated decision-making with significant effects, systematic monitoring of workers, sensitive or inferred special-category data, innovative AI technology use, large-scale employee processing, and imbalance of power between employer and employee. Multiple criteria clearly apply.

**What data subject friction points are most likely?**  
Likely friction points include employee objections to profiling, requests for access to scoring logic and performance profiles, disputes regarding inaccurate or biased rankings, and requests for erasure or correction of records influencing promotion decisions.

**What is the controller / processor split? Name each entity and its role.**  
The retail chain acts as the Data Controller because it determines the purpose and means of processing. The AI vendor and cloud infrastructure providers act as Data Processors or sub-processors processing employee data on the retailer’s behalf.

**Is a DPA (Data Processing Agreement) needed with any vendor? Which ones?**  
Yes. DPAs are required with the AI vendor, cloud hosting providers, analytics vendors, and any sub-processors involved in model hosting, storage, or assessment processing.

---

### Section C — Law Stacking

**AI Act cross-check**  
This system would likely qualify as High-Risk AI under the employment and worker management category of Annex III. The AI Act adds obligations including conformity assessment, technical documentation, bias testing, human oversight requirements, logging, and registration obligations beyond GDPR.

**ePrivacy check**  
No major ePrivacy trigger appears in the core scenario because the system relies mainly on internal HR and employment data rather than cookies or tracking technologies. If browser tracking or behavioural monitoring tools are added later, ePrivacy consent requirements may apply.

**Data Act check**  
Likely N/A. The scenario does not primarily involve connected products, IoT systems, or cloud switching obligations beyond standard processor portability concerns.

---

## Phase 3: Client Recommendation Memo (Advisory Note)

**Bottom line: Go with conditions.**

The proposed system presents substantial GDPR and AI Act compliance risks due to employee profiling, automated ranking, inferred behavioural analysis, and significant employment impacts. The project may proceed only if the company implements strong governance, meaningful human oversight, and formal risk assessment measures before deployment.

The first priority is to complete a full Data Protection Impact Assessment (DPIA) before any live employee data is processed. This is mandatory due to systematic employee evaluation, profiling, large-scale workforce monitoring, and potentially significant employment effects. The DPIA should specifically assess bias risks, explainability limitations, proportionality of the scoring model, and safeguards against discriminatory outcomes.

Second, the company must redesign the human review process so that HR managers exercise genuine independent judgment rather than rubber-stamping AI-generated rankings. Employees should have a clear right to request human review, challenge rankings, and obtain meaningful explanations of decisions affecting promotion eligibility. The current “override only with justification” structure creates significant Article 22 GDPR risk because it suggests the AI output drives the decision by default.

Third, the company must execute Data Processing Agreements with all AI and cloud vendors and implement lawful international transfer safeguards for any US-hosted infrastructure. Standard Contractual Clauses alone may not be sufficient without supplementary technical and organizational safeguards.

Residual risks remain even if these measures are implemented. First, inferred behavioural or reliability assessments may still create discrimination or unfairness concerns, especially where protected characteristics are indirectly correlated with performance indicators. Second, employee trust and workplace relations may deteriorate if workers perceive the system as opaque or punitive. Third, regulators may scrutinize the system aggressively because employment-related AI is considered a high-enforcement area under both GDPR and the EU AI Act.

The company should therefore treat this deployment as a high-risk governance program rather than a standard HR automation project.


## Phase 4: Peer review
**Partner: Javier Portero Aylagas**

| Criterion                                     | Score (1–3) | Comment                                                                                                                                                                                                                                                                                    |
| --------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Clear bottom-line recommendation              | 3           | The recommendation is clear, practical, and appropriately cautious. “Go with conditions” is justified and consistently supported throughout the memo.                                                                                                                                      |
| Lawful basis selection is justified           | 2           | The analysis correctly identifies legitimate interests concerns and flags legal uncertainty appropriately. However, the memo could be stronger by taking a firmer position on whether “contract” is realistically defensible for promotion scoring and profiling in an employment context. |
| Top actions are specific and sequenced        | 3           | The actions are concrete, operational, and logically ordered: DPIA first, lawful basis review second, workflow redesign third. This mirrors a realistic compliance implementation sequence.                                                                                                |
| Residual risks are named honestly             | 3           | The residual risks are realistic and well framed, especially around historic bias, opacity, and international transfers. The review does not overpromise compliance certainty.                                                                                                             |
| Law stacking is addressed (AI Act / ePrivacy) | 3           | Strong treatment of law stacking. The review correctly identifies the system as High-Risk under the AI Act and appropriately limits ePrivacy relevance to potential secondary tracking functionality.                                                                                      |

### Overall Feedback

This is a strong and realistic GDPR audit review that reads like a genuine consulting deliverable rather than an academic exercise. The strongest sections are the DPIA analysis, Article 22 discussion, and workflow redesign recommendations. One improvement would be to tighten the lawful basis analysis by explaining why employee “contract” may be weak for AI-driven ranking beyond ordinary HR administration, particularly given the imbalance of power in employment relationships.

### Client Response

We accept the overall recommendation and agree that the project should not proceed without a DPIA and stronger human oversight controls. However, we would like the consultant to rethink the recommendation around excluding absence records and disciplinary notes entirely. Our HR leadership believes those fields are important indicators for leadership reliability, so we need clearer guidance on whether they can be retained with safeguards rather than removed completely.


## Phase 5: Stretch - Mini Data Protection by Design Checklist

Highest-Risk Processing Activity

Activity: AI-driven employee scoring and ranking for promotion decisions (HR profiling + automated prioritisation)

Data minimisation: Fails / Partially unknown
The system aggregates broad HR datasets (sales, absence, disciplinary notes, interview recordings, complaints). No clear evidence that only strictly necessary fields are included per purpose. Likely over-collection “just in case”.

Purpose binding: Fails
Data collected for HR administration is reused for predictive scoring and behavioural inference. No technical enforcement preventing reuse for model training or secondary profiling. Purpose limitation is procedural, not enforced in system design.

Access controls: Unknown
Access is described at HR manager level, but unclear whether role-based access control is enforced across raw datasets, model outputs, and vendor-side processing. Vendor access controls not specified.

Retention enforcement: Fails / Unknown
Retention is described as “HR schedule” rather than system-enforced deletion. No indication of automated deletion of interview recordings, training datasets, or model logs. Model persistence risk not addressed.

Subject rights workflow: Unknown
No defined workflow for handling Article 15/17 requests. Particularly unclear how employees could access scoring logic, contest rankings, or request deletion from training datasets and downstream model effects.

Incident response: Unknown / Likely partial
No explicit breach detection, logging, or 72-hour notification workflow described. Given US vendor involvement, responsibility split and escalation timelines are unclear.

Overall: strongest weaknesses are purpose binding, minimisation, and retention enforcement — the core structural GDPR design gaps for AI HR profiling systems.