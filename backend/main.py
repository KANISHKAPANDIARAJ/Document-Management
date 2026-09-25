from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routes.documents import router as documents_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Management & AI Assistant",
    description="Full-Stack Document Management System with AI Question Answering",
    version="1.0.0",
)

app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}