from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import ChatMessage, ChatSource
from ..services.ai_service import generate_answer
from ..services.retrieval import retrieve_documents

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    question: str


@router.post("")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if len(question) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Question is too long.",
        )

    retrieved = retrieve_documents(
        question=question,
        db=db,
        top_k=5,
    )

    answer = await generate_answer(
        question=question,
        snippets=retrieved,
    )

    chat_message = ChatMessage(
        question=question,
        answer=answer,
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    sources = []

    for item in retrieved:
        document = item["document"]

        source = ChatSource(
            chat_message_id=chat_message.id,
            document_id=document.id,
            score=item["score"],
        )

        db.add(source)

        sources.append(
            {
                "document_id": document.id,
                "filename": document.filename,
                "score": item["score"],
                "snippet": item["snippet"],
            }
        )

    db.commit()

    return {
        "id": chat_message.id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "created_at": chat_message.created_at,
    }