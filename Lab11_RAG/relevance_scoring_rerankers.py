from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from lab11_functions import (
    extract_structure,
    build_pinecone_vectors,
    json_safe,
    build_documents_for_embedding,
    ensure_pinecone_index,
    build_relevance_scorer,
    rerank_documents_by_relevance,
    filter_by_metadata,
    evaluate_retrieval_performance,
    RetrievalMetrics,
)

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "ai_hleg_ethics_guidelines_for_trustworthy_ai-en_87F84A41-A6E8-F38C-BFF661481B40077B_60419.pdf"
PINECONE_INDEX_NAME = "trustworthy-ai"
PINECONE_CLOUD_DEFAULT = "aws"
PINECONE_REGION_DEFAULT = "us-east-1"
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

def load_environment() -> None:
    """Load .env values if python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()

def build_baseline_retriever(
    pdf_path: Path,
    index_name: str = PINECONE_INDEX_NAME,
) -> tuple[list[dict[str, Any]], Any]:
    """
    Build the baseline vector search setup used for initial retrieval.

    Returns the extracted records and a LangChain vector store backed by Pinecone.
    """
    load_environment()

    from langchain_openai import OpenAIEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone, ServerlessSpec

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pinecone_cloud = os.environ.get("PINECONE_CLOUD", PINECONE_CLOUD_DEFAULT)
    pinecone_region = os.environ.get("PINECONE_REGION", PINECONE_REGION_DEFAULT)

    embedding_model = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        dimensions=EMBEDDING_DIMENSIONS,
    )

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is required")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY is required")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    chunks = extract_structure(str(pdf_path))
    # records = [chunk for chunk in chunks if str(chunk.get("heading", "")).strip() or str(chunk.get("body", "")).strip()]
    records = [chunk for chunk in chunks if str(chunk.get("heading", "")).strip()]
    documents = build_documents_for_embedding(records)
    embeddings = embedding_model.embed_documents(documents)

    pc = Pinecone(api_key=pinecone_api_key)
    
    try:
        index_description = pc.describe_index(index_name)
    except:
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSIONS,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=pinecone_cloud,
                region=pinecone_region,
            ),
        )
        index_description = pc.describe_index(index_name)

    index_dimension = (
        index_description["dimension"]
        if isinstance(index_description, dict)
        else getattr(index_description, "dimension", None)
    )
    if index_dimension != EMBEDDING_DIMENSIONS:
        raise ValueError(f"Pinecone index dimension {index_dimension} does not match embedding dimension {EMBEDDING_DIMENSIONS}")

    index = ensure_pinecone_index(
        pc=pc,
        index_name=index_name,
        dimension=EMBEDDING_DIMENSIONS,
        cloud=pinecone_cloud,
        region=pinecone_region
    )
    
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embedding_model,
        text_key="text",
    )

    vectors = build_pinecone_vectors(records, embeddings)
    index.upsert(vectors=vectors)
    index_stats = index.describe_index_stats()
    total_vector_count = (
        index_stats["total_vector_count"]
        if isinstance(index_stats, dict)
        else getattr(index_stats, "total_vector_count", None)
    )
    print(f"Index: {index_name}")
    print(f"Dimension: {index_dimension}")
    print(f"Vectors stored: {total_vector_count}")

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding_model,
        text_key="text",
    ) 

    return chunks, records, vectorstore


def main() -> None:
    load_environment()
    chunks, records, vectorstore = build_baseline_retriever(PDF_PATH)

    for i in range(20):
        print(f"Chunk {i}:")
        print(f"Heading: {chunks[i].get('heading', '')}")
        print(f"Body: {chunks[i].get('body', '')[:200]}...")
        print("=" * 40)

    # ========== Evaluate Performance ==========
    print("\n" + "=" * 60)
    print("Evaluate Performance (With & Without Reranking)")
    print("=" * 60)
    
    sample_query = "What are the components of Trustworthy AI?"
    
    # Retrieve and evaluate WITHOUT reranking
    print(f"\nQuery: {sample_query}")
    print("\n--- Retrieval WITHOUT Reranking ---")
    results_without, metrics_without = evaluate_retrieval_performance(
        query=sample_query,
        vectorstore=vectorstore,
        use_reranking=False,
        k=6,
    )
    
    print(f"Results: {metrics_without.num_results}")
    print(f"Top score: {metrics_without.top_score_without_reranking:.4f}")
    
    # Retrieve and evaluate WITH reranking
    print("\n--- Retrieval WITH Reranking ---")
    results_with, metrics_with = evaluate_retrieval_performance(
        query=sample_query,
        vectorstore=vectorstore,
        use_reranking=True,
        k=6,
    )
    
    print(f"Results: {metrics_with.num_results}")
    print(f"Top score: {metrics_with.top_score_with_reranking:.4f}")
    print(f"Score improvement: {metrics_with.improvement_percentage:.2f}%")
    
    # Display detailed comparison
    print("\n--- Detailed Results Comparison ---")
    print(json.dumps(
        {
            "without_reranking": [
                {
                    "metadata": json_safe(item["document"].metadata),
                    "page_content": item["document"].page_content[:150],
                    "combined_score": item["combined_score"],
                }
                for item in results_without[:3]
            ],
            "with_reranking": [
                {
                    "metadata": json_safe(item["document"].metadata),
                    "page_content": item["document"].page_content[:150],
                    "combined_score": item["combined_score"],
                }
                for item in results_with[:3]
            ],
        },
        indent=2,
        ensure_ascii=True,
    ))




if __name__ == "__main__":
    main()
