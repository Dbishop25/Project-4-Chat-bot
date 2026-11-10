Documentation Digester

A full stack chatbot that answers questions about a body of documentation using semantic search and retrieval-augmented generation (RAG). Ask a question in plain English, and the system finds the most relevant sections of the docs and uses them to write a clear, grounded answer, even when your wording doesn't match the documentation exactly.

Theme: [Fill in: the documentation our chatbot covers, e.g. "Python FastAPI docs"]

What It Does
Ingests and cleans a collection of documentation
Splits it into meaningful chunks (by headers and logical sections, not raw character count)
Converts each chunk into a vector using a local embedding model and stores it in a vector database
Retrieves the top-K most semantically relevant chunks for any question
Generates a conversational answer that uses those chunks and shows its sources
Says "I don't know" (or politely refuses) when a question is irrelevant, inappropriate, or not covered by the docs
How It Works
Docs → Clean → Semantic Chunking → Embeddings → Vector DB
                                                    │
User question → FastAPI → Retriever (Top-K) → LLM → Answer + Sources → UI

Phase 1: The Digester (ETL)

Ingestion: collect the source documentation
Cleaning: strip noise and meaningless content
Semantic chunking: split by headers/sections so each chunk keeps its context
Vectorization: embed chunks with Sentence-Transformers and index them in Chroma/FAISS

Phase 2: The Searcher (API + UI)

Natural language querying through an async FastAPI backend
Top-K retrieval of the most relevant chunks via LangChain
Provenance: every answer is built from, and shows, the chunks it used
Chat interface that talks to the backend
Tech Stack
Layer	Tool
Language	Python
Orchestration	LangChain
API	FastAPI
Vector database	Chroma / FAISS
Embeddings	Sentence-Transformers (local)
Frontend	[React / Streamlit / etc.]
Project Structure
documentation-digester/
├── data/          # raw and cleaned documentation
├── ingest/        # cleaning, chunking, and embedding scripts
├── backend/       # FastAPI app and LangChain retrieval chain
├── frontend/      # chat UI
├── tests/         # evaluation questions and retrieval tests
└── README.md
Getting Started
bash
# Clone the repo
git clone https://github.com/<owner>/<repo-name>.git
cd <repo-name>

# Backend setup
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Build the vector index
python ingest/build_index.py

# Run the API
uvicorn backend.main:app --reload

# Run the frontend (see frontend/README for details)

Copy .env.example to .env and fill in any needed settings. Never commit .env.

Quality Goals
Natural responses: answers are understandable and realistic
Semantic precision: the system finds the right information for the question
Chunk integrity: chunks are complete enough to make sense on their own
Latency: fast question-to-answer time

# Team
| Role | Teammate |
| --- | --- |
| Frontend | David Villarreal |
| Data ingestion & Cleaning | Tuan Dinh |
| Chunking & Vectorization | Amen Akploh |
| Retrieval & RAG Chain | Yousef Abduas |
| Backend API | William Sancho |
| QA, Evaluation & Demo	| Nate Calderon | 
