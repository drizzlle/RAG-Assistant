# Data Center RAG Assistant

A self-hosted Retrieval-Augmented Generation (RAG) assistant built for organizations that cannot afford to send internal documents to cloud AI services. Ingest any PDF, ask questions, get answers grounded in your own data — all running locally on your infrastructure. No API keys, no external calls, no data leaving your network.

## Why Self-Hosted RAG

Some industries handle documents that should never touch a third-party API. Data center operators work with infrastructure blueprints and client SLAs. Law firms handle privileged case files. Healthcare organizations process patient records under HIPAA. Defense contractors deal with classified specifications. Financial institutions manage audit reports bound by regulatory controls.

The common thread: these organizations need AI-powered knowledge retrieval, but the documents are too sensitive to upload anywhere.

This project runs **entirely on local infrastructure**. The embedding model and the LLM both run via Ollama on the same machine that hosts the data. No document content ever leaves the network. Whether you're querying data center standards, internal compliance policies, or engineering specifications — the privacy guarantee is the same.

## How It Works

The system has two pipelines:

**Ingestion (runs once per document)**

PDF → extract text (pdfplumber) → split into overlapping chunks → embed each chunk (Ollama nomic-embed-text) → store in Postgres with pgvector

**Query (runs on every question)**

User question → embed with same model → pgvector cosine similarity search → top 5 chunks → LLM generates answer grounded in context → response with source citation

The key insight: both pipelines use the **same embedding model**, so the question's vector lands in the same 768-dimensional space as the document chunks. Similar meaning = nearby vectors = relevant results.

## Screenshots

| Ask a question | Thinking | Answer with source |
|:-:|:-:|:-:|
| ![Search](screenshots/rag-search.png) | ![Searching](screenshots/rag-searching.png) | ![Answer](screenshots/rag-answer.png) |

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Backend | Django | Familiar, batteries-included, ORM handles pgvector natively |
| Database | PostgreSQL + pgvector | Vector similarity search without a separate vector DB |
| Embeddings | Ollama + nomic-embed-text (768 dims) | Runs locally, no API keys, no data leaves the machine |
| LLM | Ollama + llama3.2 | Local inference, suitable for on-prem deployment |
| PDF Parsing | pdfplumber | Reliable text extraction with table support |
| Frontend | Bootstrap 5 + vanilla JS | Clean chat interface with AJAX, no framework overhead |

## Project Structure

```
RAG-Assistant/
├── manage.py
├── core/                     # Django project settings
├── rag/                      # Main app
│   ├── models.py             # Document + Chunk (with VectorField)
│   ├── views.py              # Query endpoint (embed → search → LLM → respond)
│   ├── management/
│   │   └── commands/
│   │       └── ingest.py     # PDF ingestion pipeline
│   └── admin.py
├── templates/
│   └── search_results.html   # Chat interface
├── files/                    # Source PDFs
└── screenshots/
```

## Setup

**Prerequisites:** Python 3.10+, Docker, Ollama

1. Clone and install dependencies:
```bash
git clone https://github.com/drizzlle/RAG-Assistant.git
cd RAG-Assistant
python -m venv .venv
source .venv/bin/activate
pip install django psycopg2-binary pgvector pdfplumber requests
```

2. Start Postgres with pgvector:
```bash
docker run -d --name pgvector \
  -e POSTGRES_DB=rag_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

3. Pull the Ollama models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```
4. Add your own PDF documents to the `files/` folder. The ingest command will process any PDF placed there.

5. Run migrations and ingest:

```bash
python manage.py migrate
python manage.py ingest
```

6. Start the server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000/` and ask a question.

## Design Decisions

**pgvector over a dedicated vector DB** — Postgres is already in the stack. Adding Pinecone or Weaviate means another service to operate, another network hop, and another place data lives. pgvector keeps everything in one database.

**Local models over cloud APIs** — For organizations handling sensitive documents, sending content to OpenAI or Anthropic may be a non-starter. Ollama runs on-prem with zero external calls. Smaller local models also reduce energy consumption compared to repeatedly hitting large cloud models.

**Simple character-based chunking** — A fixed 1000-character window with 150-character overlap. No semantic chunking, no sentence boundary detection. For a standards document with structured prose, this works well and is trivially explainable.

**No fallback mechanisms** — If embedding fails or the LLM is down, the error surfaces directly. Silent fallbacks hide real failures and erode trust in enterprise tools.

**Idempotent ingestion** — A SHA-256 hash of the file content prevents duplicate ingestion. Re-running `python manage.py ingest` on the same PDF is a safe no-op.

## What I'd Improve in a Production Scenario

- **Incremental ingestion** — watch a folder or integrate with document management systems for automatic ingestion of new documents
- **Role-based access** — restrict which documents different users can query, critical when documents contain sensitive operational details
- **Feedback loops** — let users flag bad answers to identify weak chunks or prompt issues
- **Streaming responses** — stream the LLM output token-by-token for better UX on longer answers
- **Hybrid search** — combine vector similarity with keyword search (BM25) for higher retrieval accuracy
- **Chunk metadata** — store page numbers and section headings so citations point to exact locations in the source PDF
- **Multiple document support** — UI for uploading and managing multiple PDFs with per-document filtering
- **Authentication** — user login and audit logging for compliance

## License

MIT