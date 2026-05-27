<h1 align="center">CortexFlow</h1>

AI document chat backend with FastAPI, MongoDB Atlas Vector Search, Agno agents, OpenRouter models, JWT authentication, REST APIs, and WebSocket streaming.

CortexFlow was built as a practical Retrieval-Augmented Generation (RAG) backend: users can register, upload documents, transform those documents into vector embeddings, and chat with an AI assistant that can retrieve evidence from their own files.

The project is intentionally backend-focused. It demonstrates API design, authentication, document ingestion, vector search, LLM integration, streaming responses, and clear separation between routers, services, schemas, and data access code.

---

## Why This Project Matters

Many AI demos stop at a single prompt. CortexFlow goes further by connecting the pieces required for a real document-based assistant:

- User accounts and JWT-based access control
- Document upload and text extraction
- Configurable chunking strategies
- Embedding generation through OpenRouter
- MongoDB Atlas Vector Search for semantic retrieval
- Agno agent with a custom document-search tool
- REST endpoints for synchronous chat
- WebSocket endpoint for streaming assistant responses
- Chat history stored through Agno's MongoDB integration
- Interactive FastAPI documentation through Swagger UI and ReDoc

For a junior developer portfolio, this project shows more than framework knowledge. It shows how several moving parts can be combined into a working AI backend with realistic engineering tradeoffs.

---

## Feature Highlights

| Area               | What CortexFlow Does                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Authentication     | Registers users, hashes passwords with bcrypt, issues JWT access tokens, and stores refresh tokens in HTTP-only cookies. |
| Document ingestion | Accepts uploaded files, extracts text, chunks content, generates embeddings, and stores metadata per user.               |
| File parsing       | Supports PDF, DOCX, HTML, HTM, and TXT files.                                                                            |
| Chunking           | Supports fixed, recursive, semantic, and markdown-based chunking strategies through Agno chunkers.                       |
| Embeddings         | Calls OpenRouter's embeddings API and stores vectors with model metadata.                                                |
| Vector search      | Uses MongoDB Atlas Vector Search to retrieve relevant chunks from the authenticated user's documents.                    |
| RAG chat           | Gives the Agno agent a `search_user_documents` tool so answers can be grounded in uploaded files.                        |
| Streaming          | Provides a WebSocket chat endpoint that streams chunks as the model generates them.                                      |
| Model discovery    | Lists chat and reranking-capable models from OpenRouter, and embedding models from MongoDB.                              |
| API docs           | Exposes Swagger UI at `/docs` and ReDoc at `/redoc`.                                                                     |

---

## Architecture

```text
Client / API Consumer
        |
        | HTTP + WebSocket
        v
FastAPI Application
        |
        +-- Auth Router
        |      - register
        |      - login
        |      - refresh
        |
        +-- Documents Router
        |      - upload document
        |      - parse text
        |      - chunk content
        |      - generate embeddings
        |      - store vectors and metadata
        |
        +-- Chat Router
        |      - REST chat
        |      - WebSocket streaming chat
        |      - chat history lookup
        |
        +-- Models Router
               - chat models
               - embedding models
               - reranking model candidates

MongoDB Atlas (Closter0)
        |
        +-- CortexFlow (database)
        |      - users
        |      - documents
        |      - openrouter_available_embedding_models
        |      - documents_1024
        |      - documents_1536
        |      - documents_3072
        |
        +-- agno (database)
               - agno_memories
               - agno_sessions

OpenRouter
        |
        +-- chat models
        +-- embedding models

Agno Agent
        |
        +-- OpenRouter model provider
        +-- MongoDB session storage
        +-- custom tool fot document search tool
```

### Backend Structure

```text
src/
├── agents/
│   └── conversation_agent.py
├── core/
│   ├── database.py
│   ├── security.py
│   └── settings.py
├── models/
│   └── auth.py
├── routers/
│   ├── auth.py
│   ├── chat.py
│   ├── documents.py
│   └── models.py
├── schemas/
│   ├── auth.py
│   ├── chat.py
│   ├── documents.py
│   ├── embeddings.py
│   └── models.py
├── services/
│   ├── database/
│   ├── chat.py
│   ├── chuncking.py
│   ├── embeddings.py
│   ├── parsers.py
│   └── vector_search.py
└── main.py
```

The code is split by responsibility:

- `routers/` define HTTP and WebSocket interfaces.
- `schemas/` define request and response validation with Pydantic.
- `services/` contain application logic such as parsing, chunking, embeddings, chat, and vector search.
- `services/database/` isolates MongoDB access.
- `core/` centralizes configuration, database clients, and security helpers.
- `agents/` builds the Agno conversation agent and attaches tools.

---

## How It Works

### 1. Document Ingestion Flow

```text
User uploads a file
        |
        v
FastAPI validates JWT and reads multipart data
        |
        v
Parser extracts text from PDF, DOCX, HTML, HTM, or TXT
        |
        v
Selected chunking strategy splits the text
        |
        v
OpenRouter generates embeddings for each chunk
        |
        v
Vectors are stored in MongoDB by embedding dimension
        |
        v
MongoDB Atlas Vector Search index is created if needed
        |
        v
Document metadata is saved for the authenticated user
```

### 2. RAG Chat Flow

```text
User sends a message
        |
        v
FastAPI creates or reuses a chat id
        |
        v
Agno agent receives the user message
        |
        v
Agent can call search_user_documents
        |
        v
Question is embedded with the same model used by uploaded documents
        |
        v
MongoDB Atlas Vector Search retrieves user-specific chunks
        |
        v
Retrieved evidence is formatted and returned to the agent
        |
        v
The model answers with document-grounded context
        |
        v
Chat session is stored through Agno MongoDB storage
```

### 3. Streaming Chat Flow

The WebSocket endpoint accepts a JWT token, model id, optional RAG settings, and model parameters. After the connection is accepted, CortexFlow streams response chunks as they arrive from the Agno agent.

If the selected model does not support tool calling, CortexFlow detects the failure, informs the user, disables RAG for that response, and continues as a normal chat instead of fully failing the interaction.

---

## Tech Stack

| Category            | Technology                        |
| ------------------- | --------------------------------- |
| Language            | Python                            |
| API framework       | FastAPI                           |
| Data validation     | Pydantic                          |
| ASGI server         | Uvicorn                           |
| Database client     | Motor                             |
| Database            | MongoDB / MongoDB Atlas           |
| Vector search       | MongoDB Atlas Vector Search       |
| Agent framework     | Agno                              |
| LLM provider        | OpenRouter                        |
| Embeddings provider | OpenRouter Embeddings API         |
| Authentication      | JWT and bcrypt                    |
| HTTP client         | httpx                             |
| File parsing        | pypdf, python-docx, BeautifulSoup |
| Streaming           | FastAPI WebSockets                |

---

## API Overview

### Authentication

| Method | Endpoint         | Description                                              |
| ------ | ---------------- | -------------------------------------------------------- |
| `POST` | `/auth/register` | Creates a user account.                                  |
| `POST` | `/auth/login`    | Validates credentials and returns a bearer access token. |
| `POST` | `/auth/refresh`  | Issues a new access token from a refresh cookie.         |

### Documents

| Method   | Endpoint            | Description                                              |
| -------- | ------------------- | -------------------------------------------------------- |
| `POST`   | `/documents/upload` | Uploads, parses, chunks, embeds, and indexes a document. |
| `GET`    | `/documents/`       | Lists documents for the authenticated user.              |
| `GET`    | `/documents/{id}`   | Returns document metadata and stored chunks/embeddings.  |
| `DELETE` | `/documents/{id}`   | Deletes document metadata and its vector chunks.         |

### Chat

| Method | Endpoint       | Description                                              |
| ------ | -------------- | -------------------------------------------------------- |
| `POST` | `/chat/`       | Sends one chat message and receives a complete response. |
| `GET`  | `/chat/`       | Lists chat ids for the authenticated user.               |
| `GET`  | `/chat/{id}`   | Returns messages from a stored chat session.             |
| `WS`   | `/chat/stream` | Streams chat responses over WebSocket.                   |

### Models

| Method | Endpoint             | Description                                               |
| ------ | -------------------- | --------------------------------------------------------- |
| `GET`  | `/models/embeddings` | Lists available embedding models stored in MongoDB.       |
| `GET`  | `/models/rerancking` | Lists reranking-capable model candidates from OpenRouter. |
| `GET`  | `/models/chat`       | Lists text-to-text chat models from OpenRouter.           |

Note: the current endpoint path is `/models/rerancking`, matching the implemented router.

### Interactive API Documentation

FastAPI automatically generates documentation from the route definitions, Pydantic request schemas, and response models.

After starting the app, open:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

These pages are useful for exploring request bodies, response models, authentication requirements, and manual API testing.

---

## Getting Started

### Prerequisites

- Python 3.11 or newer recommended
- MongoDB Atlas cluster with Vector Search support
- OpenRouter API key
- A terminal with access to this repository

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file:

```bash
# Windows
copy .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Fill in:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
MONGODB_URL=your_mongodb_connection_string
JWT_SECRET_TOKEN=your_jwt_secret
```

### 4. Run the API

```bash
python -m src.main
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Example Usage

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Rafa\",\"email\":\"rafa@example.com\",\"password\":\"strong-password\"}"
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"rafa@example.com\",\"password\":\"strong-password\"}"
```

Use the returned `access_token` as a bearer token for protected endpoints.

### Upload a Document

`document_data` is a JSON string inside a multipart form request.

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@example.pdf" \
  -F "document_data={\"embedding\":{\"model_id\":\"openai/text-embedding-3-small\",\"model_params\":{}},\"chunking\":{\"strategy\":\"recursive\",\"config\":{\"chunk_size\":1000,\"overlap\":150}}}"
```

### Ask a RAG Question

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"model_id\":\"openai/gpt-4o-mini\",\"user_message\":\"What are the key points from my uploaded document?\",\"model_params\":{},\"use_rag\":true,\"rag_limit\":5}"
```

---

## Engineering Problems Solved

### User-specific RAG isolation

Uploaded documents are stored with the authenticated user's id. Vector search also filters by user id, so one user's chat cannot retrieve chunks from another user's files.

### Multiple embedding dimensions

Different embedding models can produce vectors with different dimensions. CortexFlow stores embeddings in dimension-based collections such as `documents_1536`, allowing each MongoDB vector index to use the correct number of dimensions.

### Configurable chunking

The upload API accepts chunking configuration instead of hardcoding one strategy. This makes it possible to compare fixed, recursive, semantic, and markdown-aware chunking depending on the document type.

### Streaming user experience

The WebSocket endpoint streams model output chunk by chunk. This makes the chat feel responsive and avoids waiting for the entire model response before showing anything to the user.

### Graceful fallback for non-tool models

Some OpenRouter chat models do not support tool use. CortexFlow detects tool-use failures related to document search and falls back to a normal chat response, keeping the conversation usable.

### Clear API contracts

Pydantic schemas define request and response shapes for auth, documents, chat, embeddings, and model discovery. FastAPI uses those schemas to validate data and generate interactive documentation.

---

## Current Limitations

This is a strong backend MVP, but it is not presented as a finished production platform.

- Automated tests are not implemented yet.
- Docker and Docker Compose are planned but not included.
- Background workers are planned; document ingestion currently runs during the upload request.
- Redis caching and queueing are not implemented yet.
- Observability, metrics, and structured logging are roadmap items.
- Re-ranking and query rewriting are planned, not implemented in the current RAG flow.
- MongoDB Atlas Vector Search is required for full document retrieval behavior.
- The refresh-token flow exists, but authentication should be hardened before production use.

---

## Roadmap

### Near Term

- Add automated tests for auth, document upload, vector search, and chat.
- Add Docker Compose for local development.
- Move document ingestion to background workers.
- Add better validation for uploaded files and model parameters.
- Improve error messages for unsupported OpenRouter models.

### RAG Improvements

- Add query rewriting before vector search.
- Add re-ranking after retrieval.
- Add citation formatting in final answers.
- Add context compression for long retrieved chunks.
- Add hybrid search with text and vector retrieval.

### Production Readiness

- Add structured logs.
- Add metrics for latency, token usage, and retrieval quality.
- Add rate limiting.
- Add CI checks.
- Add API integration tests.
- Add dashboard or frontend client.

---

## What This Project Demonstrates

CortexFlow demonstrates the ability to:

- Design a FastAPI backend with modular routers and services
- Work with async Python and async MongoDB access
- Implement JWT authentication and password hashing
- Integrate external AI APIs
- Build a RAG pipeline from document upload to grounded chat
- Use vector databases and semantic search concepts
- Stream AI responses over WebSockets
- Document APIs clearly for other developers
- Separate implemented features from future roadmap work

For an interviewer, the most important signal is that this is not only a prompt wrapper. It is a backend system that connects authentication, file processing, embeddings, vector search, agents, and streaming into one coherent project.
