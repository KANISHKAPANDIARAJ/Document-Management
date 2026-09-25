import re

from sqlalchemy.orm import Session

from ..models import Document


def tokenize(text: str) -> set[str]:
    """Convert text into normalized keyword tokens."""
    return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))


def calculate_overlap(
    question_tokens: set[str],
    document_tokens: set[str],
) -> int:
    """Calculate the number of shared keywords."""
    return len(question_tokens & document_tokens)


def retrieve_documents(
    question: str,
    db: Session,
    top_k: int = 5,
):
    """Retrieve documents using keyword-overlap matching."""

    question_tokens = tokenize(question)

    if not question_tokens:
        return []

    documents = db.query(Document).all()

    ranked_documents = []

    for document in documents:
        document_tokens = tokenize(document.content)

        overlap = calculate_overlap(
            question_tokens,
            document_tokens,
        )

        if overlap > 0:
            snippet = extract_snippet(
                document.content,
                question_tokens,
            )

            ranked_documents.append(
                {
                    "document": document,
                    "score": overlap,
                    "snippet": snippet,
            }
            )

    ranked_documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked_documents[:top_k]
def extract_snippet(
    content: str,
    question_tokens: set[str],
    max_length: int = 500,
) -> str:
    """Extract a relevant snippet from document content."""

    sentences = re.split(r"(?<=[.!?])\s+", content.strip())

    matching_sentences = []

    for sentence in sentences:
        sentence_tokens = tokenize(sentence)

        if question_tokens & sentence_tokens:
            matching_sentences.append(sentence)

    if matching_sentences:
        snippet = " ".join(matching_sentences)
    else:
        snippet = content[:max_length]

    return snippet[:max_length]