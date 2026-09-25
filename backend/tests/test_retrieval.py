from backend.services.retrieval import (
    calculate_overlap,
    tokenize,
    extract_snippet
)


def test_tokenize():
    tokens = tokenize("FastAPI is a Python framework.")

    assert "fastapi" in tokens
    assert "python" in tokens
    assert "framework" in tokens


def test_calculate_overlap():
    question_tokens = {
        "fastapi",
        "python",
        "framework",
    }

    document_tokens = {
        "fastapi",
        "python",
        "database",
    }

    assert calculate_overlap(
        question_tokens,
        document_tokens,
    ) == 2

def test_extract_snippet():
    content = (
        "Python is a programming language. "
        "FastAPI is a Python framework for building APIs. "
        "SQLite is a lightweight database."
    )

    question_tokens = {
        "fastapi",
        "python",
        "framework",
    }

    snippet = extract_snippet(
        content,
        question_tokens,
    )

    assert "FastAPI" in snippet
    assert "framework" in snippet