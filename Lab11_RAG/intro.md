# Overview of our goal:
Create a RAG that is capable of answering questinos about a sport in an accurate and accessible manner for beginners.

Target pdf: 20171026174027.pdf (ONLY this pdf)
Coding style: native to langchain principles, beginner friendly code with explanations

# Steps:

1. Imports
    - Import our .env file with load_dot_env
    - Use langchain 1.0 and compatible librarires (langchain_openai, langchain_pinecone)
    - Process a pdf (library TBD)

2. Process the PDF
    [DONE]
    - Keep each section together (no/partial chunking)
    - Exclude: tables, lists, footnotes, empty pages, anything that would need OCR
    
    [MISSING]
    - Sections are defined by the number (i.e. 1. Governing Rules). The document has a structure that might be able to be explored to do this automatically (indents for subsections).
    - Metadata should contain: name, page, section, section name, previous section_id, forward_section_id
    - For the images in the pdf, call openai to provide a detail description of the image and embbed that description. Add the image to the metadata (raw image path).
    - Normalize the metadata

3. Embed the chunk
    - Embed small from openai [DONE]

4. Upsert them in pinecone
    - index_name = 'sports_rules' [DONE]
    - No existing pinecone index [DONE]

5. Build a retriever in langchain
    - langchain_pinecone
    - Add the retreiver as a tool for the agent (langchain_pinecone)
    - Retriever should return image and text

6. Test it
    - Manual process

# Technological stack
- dotenv
- langchain
- pinecone
- openai