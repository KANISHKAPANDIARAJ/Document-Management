import httpx

from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def fallback_answer(question: str, snippets: list[dict]) -> str:
    """Generate a deterministic answer when no LLM is configured."""

    if not snippets:
        return (
            "I could not find relevant information in the uploaded "
            "documents."
        )

    best_snippet = snippets[0]["snippet"]

    return (
        "Based on the uploaded documents, the relevant information is:\n\n"
        f"{best_snippet}"
    )


async def generate_answer(
    question: str,
    snippets: list[dict],
) -> str:

    if not LLM_API_KEY:
        return fallback_answer(question, snippets)

    context = "\n\n".join(
        f"Source: {item['document'].filename}\n"
        f"{item['snippet']}"
        for item in snippets
    )

    prompt = f"""
Answer the user's question using only the provided document context.

If the context does not contain enough information, say that clearly.

Question:
{question}

Document context:
{context}
""".strip()

    response = await httpx.AsyncClient().post(
        f"{LLM_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]