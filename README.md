# Document Management & AI Assistant

A full-stack document management application with an AI-powered question-answering system. Users can upload documents, manage them, ask questions about their uploaded content, and receive answers with relevant document sources.

## Features

* Upload `.txt`, `.md`, and `.json` documents
* Validate uploaded file types
* Extract and store document content
* Preserve original uploaded files for download
* List all uploaded documents
* View document details
* Download uploaded documents
* Delete documents
* Search documents using keyword-based retrieval
* Rank documents based on keyword overlap
* Extract relevant text snippets
* Ask natural-language questions about uploaded documents
* Generate AI-powered answers using retrieved document content
* Provide source documents and snippets with each answer
* Deterministic fallback response when no AI API key is configured
* Interactive API documentation using Swagger UI

## System Architecture

```text
                    USER
                      |
                      v
              FRONTEND APPLICATION
             HTML + CSS + JavaScript
                      |
                  HTTP / REST
                      |
                      v
              FASTAPI BACKEND
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
   Documents      Retrieval      AI Service
     Routes         Service        Service
        |             |             |
        v             v             v
      SQLite       Keyword       LLM API
     Database      Matching
        |
        v
   Upload Storage
```

## Application Workflow

```text
Upload Document
       |
       v
Validate File
       |
       v
Extract / Read Content
       |
       v
Store File + Metadata + Content
       |
       v
      SQLite
       |
       v
User Asks Question
       |
       v
Keyword-Based Retrieval
       |
       v
Rank Relevant Documents
       |
       v
Extract Relevant Snippets
       |
       v
Generate Answer
       |
       v
Return Answer + Sources
```

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy
* SQLite
* HTTPX
* python-dotenv
* python-multipart

### Frontend

* HTML5
* CSS3
* JavaScript
* Fetch API

### AI

* External LLM API
* Configurable model and API endpoint
* Deterministic fallback response when an API key is unavailable

## Supported File Types

The application supports the following file formats:

| File Type | Support |
| --------- | ------- |
| `.txt`    | Yes     |
| `.md`     | Yes     |
| `.json`   | Yes     |
| `.pdf`    | No      |
| `.docx`   | No      |
| Images    | No      |

For `.txt` and `.md` files, the application reads the content directly as UTF-8 text.

For `.json` files, the application validates the JSON and converts its content into searchable text while preserving the original JSON file for download.

## Project Structure

```text
document-management-ai/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── retrieval.py
│   │   └── ai_service.py
│   │
│   ├── uploads/
│   └── tests/
│       ├── __init__.py
│       ├── test_retrieval.py
│       └── test_ai_service.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── documents.db
```

## Backend Components

### `main.py`

The main FastAPI application entry point.

Responsibilities:

* Create the FastAPI application
* Initialize database tables
* Register API routers
* Configure CORS
* Provide the application entry point

### `config.py`

Handles environment-based configuration.

The application reads values such as:

* LLM API key
* LLM base URL
* LLM model

Example:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### `database.py`

Configures the SQLite database and SQLAlchemy.

Responsibilities:

* Create the database engine
* Configure database sessions
* Create the SQLAlchemy declarative base

### `models.py`

Defines the database tables using SQLAlchemy ORM.

The application contains:

* `Document`
* `ChatMessage`
* `ChatSource`

### `routes/documents.py`

Handles document-related API operations.

Responsibilities:

* Upload documents
* Validate file extensions
* Read document content
* Store document metadata
* Save physical files
* List documents
* Retrieve document details
* Download documents
* Delete documents

### `routes/chat.py`

Handles question-answering requests.

Responsibilities:

1. Receive the user's question
2. Validate the question
3. Retrieve relevant documents
4. Generate an answer
5. Store the chat message
6. Store source information
7. Return the answer and sources

### `services/retrieval.py`

Implements the document retrieval system.

The retrieval process uses simple keyword overlap rather than vector embeddings.

Main responsibilities:

* Tokenize text into keywords
* Compare question keywords with document keywords
* Calculate overlap scores
* Rank relevant documents
* Extract relevant snippets

### `services/ai_service.py`

Handles answer generation.

If an LLM API key is configured, the service sends the question and retrieved document context to the configured LLM.

If no API key is available, the application uses a deterministic fallback response based on the retrieved document content.

## Document Processing

The application does not convert uploaded documents directly into LLM or embedding tokens.

The processing pipeline is:

```text
Uploaded File
      |
      v
Read / Extract Text
      |
      v
Store Text in SQLite
      |
      v
Keyword Tokenization
      |
      v
Document Retrieval
      |
      v
Relevant Snippets
      |
      v
LLM Prompt
      |
      v
AI Response
```

### Text Files

`.txt` and `.md` files are read directly as UTF-8 text.

Example:

```text
Employees receive 24 days of annual leave.
```

The text is stored in the database.

### JSON Files

JSON files are first validated to ensure that they contain valid JSON.

The JSON content is converted into searchable text for retrieval, while the original JSON file is preserved for download.

## Retrieval System

The application uses a simple keyword-based retrieval approach.


### Tokenization

The retrieval service uses a basic regular-expression tokenizer.

For example:

```text
Employees receive 24 days of annual leave.
```

becomes approximately:

```text
{
    "employees",
    "receive",
    "24",
    "days",
    "annual",
    "leave"
}
```

When the user asks:

```text
How many days of annual leave do employees receive?
```

the application extracts keywords from the question and compares them with the document keywords.

### Relevance Score

The relevance score is based on the number of overlapping keywords.

```text
Question Keywords
        |
        v
Compare with Document Keywords
        |
        v
Count Common Keywords
        |
        v
Overlap Score
```

Documents are then sorted by their overlap score.

## AI Answer Generation

After retrieving relevant documents, the application builds a prompt containing:

* User question
* Document filenames
* Relevant document snippets

Example:

```text
Question:
How many days of annual leave do employees receive?

Document context:

Source: employee_policy.txt

Employees receive 24 days of annual leave.
```

This context is sent to the configured LLM.

The LLM then generates the final answer using the retrieved document information.

## Fallback AI Response

The application can run without an LLM API key.

When `LLM_API_KEY` is not configured, the system returns a deterministic answer based on the best retrieved document snippet.

Example:

```text
Based on the uploaded documents, the relevant information is:

Employees receive 24 days of annual leave.
```

This allows the application to function even without an external AI service.

## Database

The application uses SQLite with SQLAlchemy.

### Document Table

Stores information such as:

* Document ID
* Original filename
* Stored filename
* Content type
* File size
* Extracted content
* Creation timestamp

### Chat Message Table

Stores:

* Chat message ID
* User question
* Generated answer
* Creation timestamp

### Chat Source Table

Stores the relationship between a chat message and the documents used to generate the answer.

It includes:

* Chat message ID
* Document ID
* Retrieval score

## API Endpoints

### Document APIs

| Method   | Endpoint                       | Description          |
| -------- | ------------------------------ | -------------------- |
| `POST`   | `/api/documents`               | Upload a document    |
| `GET`    | `/api/documents`               | List documents       |
| `GET`    | `/api/documents/{id}`          | Get document details |
| `GET`    | `/api/documents/{id}/download` | Download document    |
| `DELETE` | `/api/documents/{id}`          | Delete document      |

### Chat API

| Method | Endpoint    | Description                             |
| ------ | ----------- | --------------------------------------- |
| `POST` | `/api/chat` | Ask a question about uploaded documents |

## API Request Example

### Chat Request

```json
{
    "question": "How many days of annual leave do employees receive?"
}
```

### Chat Response

```json
{
    "id": 1,
    "question": "How many days of annual leave do employees receive?",
    "answer": "Employees receive 24 days of annual leave.",
    "sources": [
        {
            "document_id": 1,
            "filename": "employee_policy.txt",
            "score": 5,
            "snippet": "Employees receive 24 days of annual leave."
        }
    ]
}
```

## Frontend

The frontend is built using:

* HTML
* CSS
* Vanilla JavaScript
* Fetch API

No frontend framework is required.

The frontend provides:

### Document Management

* File upload
* Document listing
* Download functionality
* Delete functionality

### AI Chat

* Question input
* Answer display
* Source document display
* Relevant text snippets

## CORS

The backend enables CORS so that the frontend development server can communicate with the FastAPI backend.

For local development, the application currently allows requests from all origins.

For production deployment, the allowed origins should be restricted to the actual frontend domain.

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd document-management-ai
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root.

```env
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

The API key can be left empty if the fallback response mode is being used.

## Running the Backend

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

## Running the Frontend

Open another terminal and run:

```bash
python -m http.server 5500 --directory frontend
```

The frontend will be available at:

```text
http://127.0.0.1:5500
```

## API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```


## Testing

The project structure includes testing support using `pytest`.

The application was manually verified through:

* Document upload
* Document listing
* Document download
* Document deletion
* Question submission
* Retrieval
* Answer generation
* Source display

## Design Principles

The application follows several simple design principles:

### Separation of Concerns

Document management, retrieval, and AI generation are separated into different modules.

```text
Routes
  |
  +-- Document Management
  |
  +-- Chat Management
        |
        +-- Retrieval Service
        |
        +-- AI Service
```

### AI Provider Isolation

The AI provider is isolated inside:

```text
backend/services/ai_service.py
```

This makes it possible to change the AI provider without rewriting the rest of the application.

### Simple Retrieval

The retrieval system intentionally uses keyword matching rather than introducing unnecessary infrastructure.

### API-First Backend

The frontend communicates with the backend through REST APIs.

This keeps the backend independent from the frontend implementation.

## Project Summary

The application provides a complete workflow for document management and AI-assisted question answering:

```text
Upload
  ↓
Validate
  ↓
Extract / Read
  ↓
Store
  ↓
Retrieve
  ↓
Rank
  ↓
Extract Snippets
  ↓
Generate Answer
  ↓
Return Sources
```

The result is a lightweight full-stack document intelligence application built with Python, FastAPI, SQLite, Vanilla JavaScript, and an optional LLM service.
