import json
import os
import uuid

from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Document

router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}
UPLOAD_DIR = "backend/uploads"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: .txt, .md, .json",
        )

    content_bytes = await file.read()

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded.",
        )

    if extension == ".json":
        try:
            json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON file.",
            )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}{extension}"
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)

    with open(stored_path, "wb") as output_file:
        output_file.write(content_bytes)

    document = Document(
        filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(content_bytes),
        content=content,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "stored_filename": document.stored_filename,
        "content_type": document.content_type,
        "size": document.size,
        "created_at": document.created_at,
    }

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.created_at.desc()).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "content_type": document.content_type,
            "size": document.size,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "stored_filename": document.stored_filename,
        "content_type": document.content_type,
        "size": document.size,
        "content": document.content,
        "created_at": document.created_at,
    }


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        document.stored_filename,
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Stored file not found.",
        )

    return FileResponse(
        path=file_path,
        filename=document.filename,
        media_type=document.content_type,
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        document.stored_filename,
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully.",
        "id": document_id,
    }