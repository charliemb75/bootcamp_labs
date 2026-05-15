# Autonomous Agent Project Plan
 
## 1. Use Case - Option C: Document Q&A System
Answer questions about internal company documents
Support multiple document types (PDFs, Word, web pages)
Provide citations and source tracking

- Last job:
    - Creation implementation of test specifications
    - Execution of tests following them
    - Verification that they have been followed by third parties
- Internal database of documents. Examples:
    - Test standards
    - Design standards and requirements
    - Assembly procedures
    - Quality specifications
    - Lessons learned
    - Old test reports
- Examples of frequent questions that an agent could answer by researching those documents:
    - I am writing the specification for a vibration test for the components [...]. Which standard lists the general requirements for such a test?
    - I want to verify a bolted joint after an endurance test. It bolts a plastic part into a casted aluminium part with an M6x20 bolt. Which residual torque should the joint still have after the test?
    - I have a .csv file with a summary of the measurements during a temperature cycling test (max and min temp in each cycle, cycle duration, total number of cycles...). Was the test executed according to specification XY?
    - I see corrosion in some parts of the cooling circuit after a test. Are there any documented precedents? How were they solved or who could I contact for an exchange?
- Target users: company colleagues (internal use)
 
## 2. Technology Stack
- Does it need external knowledge?
    - Yes, it analyzes company internal documentation → Needs RAG
- Does it need to interact with external systems?
    - No → Can be standalone
- Does it need multi-step reasoning?
    - Yes. Classifying the question beforehand would be helpful → LangGraph for structured workflows
- Does it need to integrate with business systems?
    - No → Can be standalone Python application
- Does it need to be autonomous (run without human input)?
    - No → Intrinsically on-demand only
- Technology stack:
    - Core LLM: Mistral (important that it is EU-based)
    - RAG components: Vector DB, embeddings, chunking strategy
    - Agent framework: LangGraph
    - Orchestration: None
    - Tools/integrations: None
 
## 3. MVP Scope
- Must-have (MVP):
    - Answer questions from knowledge base (RAG)
    - Support PDF only
    - Languages: English and German
    - Version for engineers --> runnable Python script is enough
- Should-have (V2):
    - UI
    - Additional languages
    - Basic conversation memory
- Nice-to-have (V3):
    - Full test specification generation
    - Connection to tools like FMEA, FRACAS, PLM, drawing databases
    - Computer vision feature to classify defects and provide related documentation (causes, consequences, possible solutions...)
 
## 4. Risk Assessment
- Technical Risks:
    - API rate limits or costs
        - Probability: Medium
        - Impact: Low
        - Mitigation:
            - Implement caching for common queries
            - Use cheaper models for simple tasks
            - Set up cost monitoring and alerts
            - Optimize prompts to reduce token usage
    - Model accuracy/hallucination
        - Probability: Medium
        - Impact: High
        - Mitigation:
            - Second "review" call to an LLM to check if the response answers the question and if the retrieved information is accurate against the provided sources
            - Alternatively: Provide only metadata (document name, section/page, link...), make the users retrieve the information from the sources themselves

- Business Risks:
    - User adoption
        - Probability: High
        - Impact: Low
        - Mitigation:
            - Provide documentation or offer a short training with varied examples
    - Change management
        - Probability: High
        - Impact: High
        - Mitigation:
            - Clear statement of the document version or release date with the retrieval, prompt the user to check for latest versions manually
            - Train the document creators to always contact the development team to update the vector stores

- Data Risks:
    - Data quality and availability
        - Probability: High
        - Impact: High
        - Mitigation:
            - Manual review of the chunking of the documents
            - Testing after embedding
            - Enforce use of document templates
            - Use of md files or similar instead of PDF/word...
    - Privacy/security
        - Probability: High
        - Impact: High
        - Mitigation:
            - Use of the tool exclusively by internal colleagues and in the internal network/VPN
            - Run it internally as far as possible, use EU-based services
 
## 5. Implementation Plan
- Implementation Phases:
    - Phase 1 - Data preparation:
        - Gather relevant files (at least for some departments), implement chunking strategy, embed
    - Phase 2 - Core agent development:
        - Implementation of the agent that can take a question by the user and retrieve the corresponding documents
    - Phase 3 - Integration and testing:
        - Verify the accurate retrieval of information
    - Phase 4 - Deployment and monitoring

- Timeline:
    - Estimated time for each phase:
        - Phase 1: 1-2 months
        - Phase 2: 2 weeks
        - Phase 3: 2 weeks
    - Key milestones:
        - Definition of the document chunking strategy
        - First set of documents embedded
        - Agent working with one type of documents
        - Agent correctly classifying the user requests and referring to a set of documents
        - Working UI
        - ...

- Resources Needed:
    - Internal documents
    - LLM subscription to use the API
    - Tool development team, representatives of some specialized departments that provide the documentation and can verify the correct retrieval
 
## 6. Success Metrics
- Time to find the correct piece of information manually vs. with the tool
- Time to generate a new specification by searching documents manually vs. with the tool