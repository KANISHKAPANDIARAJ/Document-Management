import pytest

from backend.services.ai_service import fallback_answer


def test_fallback_answer_with_snippet():
    snippets = [
        {
            "document": type(
                "Document",
                (),
                {"filename": "test.txt"},
            )(),
            "snippet": "FastAPI is a Python framework for building APIs.",
            "score": 3,
        }
    ]

    answer = fallback_answer(
        "What is FastAPI?",
        snippets,
    )

    assert "FastAPI" in answer
    assert "Python framework" in answer


def test_fallback_answer_without_snippets():
    answer = fallback_answer(
        "What is FastAPI?",
        [],
    )

    assert "could not find relevant information" in answer