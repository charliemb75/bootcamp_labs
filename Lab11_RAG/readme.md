# Lab11_RAG

This folder contains a small RAG pipeline experiment built around the EU AI ethics guidelines PDFs. The code extracts document structure from the source PDF, creates embeddings, stores them in Pinecone, and compares retrieval results with and without reranking.

## Contents

- `relevance_scoring_rerankers.py`: main script that builds the baseline retriever, runs retrieval, and compares results with reranking.
- `lab11_functions.py`: helper functions for structure extraction, Pinecone vector creation, relevance scoring, reranking, and evaluation.
- `lab_summary.md`: short write-up of the reranking experiment results.
- `*.pdf`: source documents used for the lab.

## How to run

1. Make sure your `.env` file includes:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - optional: `PINECONE_CLOUD`
   - optional: `PINECONE_REGION`

2. Install the required Python packages if they are not already available.

3. Run the script from this folder:

```bash
python relevance_scoring_rerankers.py
```

## What the script does

- Parses the PDF structure into sections.
- Creates embeddings with `text-embedding-3-small`.
- Creates or reuses a Pinecone index named `trustworthy-ai`.
- Retrieves relevant chunks for a sample query.
- Compares plain retrieval against reranked retrieval and prints the results.

## Notes

- The script expects the target PDF to be present in this folder.
- The first run may take longer because it can create the Pinecone index and upsert vectors.
