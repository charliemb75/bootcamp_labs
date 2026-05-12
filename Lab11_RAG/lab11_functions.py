from __future__ import annotations

import json
import re
from itertools import groupby
import os
from typing import Any, Iterable, Sequence, TYPE_CHECKING
from dataclasses import dataclass
from statistics import mean

if TYPE_CHECKING:
    from langchain_core.documents import Document

def is_bold(fontname: str) -> bool:
    return "Bold" in fontname or fontname.endswith("-BoldMT")

def is_ital(fontname: str) -> bool:
    return "Italic" in fontname or fontname.endswith("-ItalicMT")

def normalize_color(color): # Normalize PDF color representation so grouping is consistent.
    if color is None:
        return "unknown"
    if isinstance(color, (int, float)):
        return "k" if color < 0.1 else "b"
    if isinstance(color, (list, tuple)):
        return "b" if any(c >= 0.1 for c in color) else "k"
    return "unknown"

def identify_level(size, bold, ital, color):
    if size == 12.0:
        return "part"
    elif size == 11.0:
        return "chapter"
    elif size == 10.0:
        if bold and (not ital) and color == "b":
            return "section"
        else:
            return "body"
    else:
        return "ignore"

def json_safe(value: Any) -> Any:
    """Convert a value into something Pinecone metadata can store safely."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]

    return str(value)

def _min_max_normalize(values: Sequence[float]) -> list[float]:
    """Normalize values to 0-1 so similarity and relevance can be blended safely."""
    if not values:
        return []

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [1.0 for _ in values]

    span = maximum - minimum
    return [(value - minimum) / span for value in values]

def document_to_scoring_text(document: Document) -> str:
    """Build a compact text representation of a retrieved chunk for LLM scoring."""
    metadata = document.metadata or {}
    heading = str(document.page_content or "").strip()
    body = str(metadata.get("body", "")).strip()
    page = metadata.get("page")
    level = metadata.get("level")

    parts: list[str] = []
    if heading:
        parts.append(f"Heading: {heading}")
    if body:
        parts.append(f"Body: {body}")
    if level is not None:
        parts.append(f"Level: {level}")
    if page is not None:
        parts.append(f"Page: {page}")

    return "\n".join(parts).strip()

def build_relevance_scorer(model_name: str = "gpt-5.4-mini") -> Any:
    """Create a chat model used to score chunk relevance."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is required")

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=model_name, temperature=0)

def _extract_relevance_score(raw_output: Any) -> float:
    """Parse a numeric score from the model response."""
    content = getattr(raw_output, "content", raw_output)
    text = str(content).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "relevance_score" in parsed:
            return float(parsed["relevance_score"])
        if isinstance(parsed, (int, float)):
            return float(parsed)
    except Exception:
        pass

    match = re.search(r"\b(?:0(?:\.\d+)?|1(?:\.0+)?)\b", text)
    if match:
        return float(match.group(0))

    return 0.0

def score_chunk_relevance(query: str, chunk_text: str, scorer: Any) -> float:
    """
    Ask an LLM to score how relevant a chunk is to a query.

    The scorer is expected to return a RelevanceScore object.
    """
    prompt = (
        "You are ranking document chunks for a retrieval-augmented generation pipeline.\n"
        "Score the chunk's relevance to the query on a scale from 0 to 1.\n"
        "Use 1.0 when the chunk directly answers the query, 0.5 when it is somewhat related, "
        "and 0.0 when it is unrelated.\n\n"
        f"Query: {query}\n\n"
        f"Chunk:\n{chunk_text}"
    )

    result = scorer.invoke(prompt)
    score = _extract_relevance_score(result)

    return max(0.0, min(1.0, score))

def rerank_documents_by_relevance(
    query: str,
    matches_with_scores: Sequence[tuple[Document, float]],
    scorer: Any,
    similarity_weight: float = 0.5,
    relevance_weight: float = 0.5,
) -> list[dict[str, Any]]:
    """
    Blend vector similarity with LLM relevance scores and reorder the chunks.

    The return value includes the original document, the two component scores,
    and the final combined score.
    """
    if similarity_weight < 0 or relevance_weight < 0:
        raise ValueError("similarity_weight and relevance_weight must be non-negative")

    if similarity_weight == 0 and relevance_weight == 0:
        raise ValueError("At least one weight must be greater than zero")

    raw_similarity_scores = [float(score) for _, score in matches_with_scores]
    normalized_similarity_scores = _min_max_normalize(raw_similarity_scores)

    scored_matches: list[dict[str, Any]] = []
    for (document, similarity_score), normalized_similarity_score in zip(
        matches_with_scores,
        normalized_similarity_scores,
    ):
        chunk_text = document_to_scoring_text(document)
        relevance_score = score_chunk_relevance(query, chunk_text, scorer)
        combined_score = (
            (similarity_weight * normalized_similarity_score)
            + (relevance_weight * relevance_score)
        ) / (similarity_weight + relevance_weight)

        scored_matches.append(
            {
                "document": document,
                "similarity_score": float(similarity_score),
                "normalized_similarity_score": float(normalized_similarity_score),
                "relevance_score": relevance_score,
                "combined_score": combined_score,
            }
        )

    scored_matches.sort(key=lambda item: item["combined_score"], reverse=True)
    return scored_matches

def extract_structure(pdf_path: str):
    import pdfplumber

    sections = []
    current: dict | None = None

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages):

            words = page.extract_words(extra_attrs=["fontname", "size", "non_stroking_color"])

            # Group consecutive words sharing same style signature
            for (size, bold, ital, color), group in groupby(
                words,
                key=lambda w: (
                    round(w["size"], 1),
                    is_bold(w["fontname"]), is_ital(w["fontname"]),
                    normalize_color(w.get("non_stroking_color")),
                ),
            ):

                text = " ".join(w["text"] for w in group).strip()
                level = identify_level(size, bold, ital, color)

                if level == "part":          # top-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "part", "heading": text, "body": "", "page": page_num + 1}

                elif level == "chapter":     # mid-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "chapter", "heading": text, "body": "", "page": page_num + 1}

                elif level == "section":     # low-level heading
                    if current:
                        sections.append(current)
                    current = {"level": "section", "heading": text, "body": "", "page": page_num + 1}
                
                elif level == "ignore":      # citations etc (skip)
                    continue

                else:                        # body text
                    if current is None:
                        current = {"level": "body", "heading": "", "body": "", "page": page_num + 1}
                    current["body"] += text + " "

    if current:
        sections.append(current)
    return sections

def build_pinecone_vectors(
    records: Sequence[dict[str, Any]],
    embeddings: Sequence[Sequence[float]],
    id_prefix: str = "section",
) -> list[dict[str, Any]]:
    """
    Convert extracted sections and embeddings into Pinecone vector payloads.
    """
    if len(records) != len(embeddings):
        raise ValueError("records and embeddings must have the same length")

    vectors: list[dict[str, Any]] = []

    for i, (record, vector) in enumerate(zip(records, embeddings), start=1):
        if "heading" not in record:
            raise KeyError("Each record must contain a 'heading' field")
        
        metadata = {
            key: json_safe(value)
            for key, value in record.items() if key != "heading"
        }
        metadata["text"] = json_safe(record["heading"])

        vectors.append(
            {
                "id": f"{id_prefix}-{i}",
                "values": list(vector),
                "metadata": metadata,
            }
        )

    return vectors

def build_documents_for_embedding(records: Iterable[dict[str, Any]]) -> list[str]:
    """
    Build the text inputs sent to the embedding model.
    This keeps the full heading as the primary searchable text.

    # For the baseline, we embed the section's combined text so the retriever
    can search both the heading and the body together.
    """
    texts: list[str] = []
    for record in records:
        heading = str(record.get("heading", "")).strip()
        if heading:
            texts.append(heading)

        # heading = str(record.get("heading", "")).strip()
        # body = str(record.get("body", "")).strip()

        # # Keep the section together, but avoid empty documents.
        # text = " ".join(part for part in [heading, body] if part)
        # if text:
        #     texts.append(text)
    return texts

def ensure_pinecone_index(
    pc: Pinecone,
    index_name: str,
    dimension: int,
    cloud: str,
    region: str,
) -> Any:
    """Create the index if it does not exist and verify its dimension."""
    from pinecone import ServerlessSpec
    
    try:
        index_description = pc.describe_index(index_name)
    except Exception:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        index_description = pc.describe_index(index_name)

    index_dimension = (
        index_description["dimension"]
        if isinstance(index_description, dict)
        else getattr(index_description, "dimension", None)
    )

    if index_dimension != dimension:
        raise ValueError(
            f"Pinecone index dimension {index_dimension} does not match embedding dimension {dimension}"
        )

    return pc.Index(index_name)


@dataclass
class RetrievalMetrics:
    """Container for retrieval performance metrics."""
    query: str
    num_results: int
    avg_score_without_reranking: float
    avg_score_with_reranking: float
    top_score_without_reranking: float
    top_score_with_reranking: float
    improvement_percentage: float


def filter_by_metadata(
    documents: list[dict[str, Any]],
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Step 5: Add Metadata Filtering
    
    Filter results by metadata (source type, section, etc.).
    
    Args:
        documents: List of document dictionaries containing metadata
        metadata_filters: Dictionary of metadata field -> value to filter by
                         (e.g., {"section": "Risk Assessment", "level": 1})
    
    Returns:
        Filtered list of documents matching the metadata criteria
    """
    if not metadata_filters:
        return documents
    
    filtered = []
    for doc in documents:
        matches_all_filters = True
        for filter_key, filter_value in metadata_filters.items():
            doc_value = doc.get("metadata", {}).get(filter_key)
            if doc_value != filter_value:
                matches_all_filters = False
                break
        if matches_all_filters:
            filtered.append(doc)
    
    return filtered


def evaluate_retrieval_performance(
    query: str,
    vectorstore: Any,
    use_reranking: bool = True,
    k: int = 6,
) -> tuple[list[dict[str, Any]], RetrievalMetrics]:
    """
    Step 7: Evaluate Performance
    
    Compare retrieval quality with and without reranking.
    Allows user to choose whether to use reranking or not.
    
    Args:
        query: The search query
        vectorstore: The Pinecone vector store
        use_reranking: Whether to apply reranking or not
        k: Number of results to retrieve
    
    Returns:
        Tuple of (retrieved_documents, metrics)
    """
    # Get raw similarity search results
    raw_matches = vectorstore.similarity_search_with_score(query, k=k)
    
    # Extract scores without reranking
    scores_without_reranking = [score for _, score in raw_matches]
    avg_score_without = mean(scores_without_reranking) if scores_without_reranking else 0
    top_score_without = max(scores_without_reranking) if scores_without_reranking else 0
    
    # Apply reranking if requested
    if use_reranking:
        scorer = build_relevance_scorer()
        reranked_matches = rerank_documents_by_relevance(
            query=query,
            matches_with_scores=raw_matches,
            scorer=scorer,
        )
        
        # Extract combined scores from reranked results
        scores_with_reranking = [item["combined_score"] for item in reranked_matches]
        avg_score_with = mean(scores_with_reranking) if scores_with_reranking else 0
        top_score_with = max(scores_with_reranking) if scores_with_reranking else 0
        
        results = reranked_matches
    else:
        # Return raw results without reranking
        scores_with_reranking = scores_without_reranking
        avg_score_with = avg_score_without
        top_score_with = top_score_without
        
        results = [
            {
                "document": doc,
                "similarity_score": score,
                "normalized_similarity_score": score,
                "relevance_score": score,
                "combined_score": score,
            }
            for doc, score in raw_matches
        ]
    
    # Calculate improvement
    improvement = (
        ((top_score_with - top_score_without) / top_score_without * 100)
        if top_score_without > 0
        else 0
    )
    
    metrics = RetrievalMetrics(
        query=query,
        num_results=len(results),
        avg_score_without_reranking=avg_score_without,
        avg_score_with_reranking=avg_score_with,
        top_score_without_reranking=top_score_without,
        top_score_with_reranking=top_score_with,
        improvement_percentage=improvement,
    )
    
    return results, metrics

