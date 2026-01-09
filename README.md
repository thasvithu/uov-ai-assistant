# UoV AI Assistant

A RAG-based chatbot for the University of Vavuniya Faculty of Technology, providing intelligent answers from faculty documents with source citations.

## Features

- 🤖 **Intelligent Q&A**: Answer questions using faculty documents
- 📚 **Source Citations**: Every answer includes document references
- 🌍 **Multilingual**: Supports English, Tamil, and Sinhala
- ⚡ **Real-time Streaming**: Fast, streaming responses
- 👥 **Multi-user**: Concurrent user support with session management
- 📊 **Feedback System**: Track user satisfaction and improve responses

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **RAG Framework**: LangChain
- **Embeddings**: Sentence-Transformers (multilingual-e5-base)
- **Vector Store**: Qdrant
- **LLM**: Groq API
- **Database**: Supabase Postgres
- **Language**: Python 3.11+

## Project Structure

```
uov-ai-assistant/
├── streamlit_ui/          # Streamlit frontend application
├── backend_api/           # FastAPI backend service
├── ingestion/             # Document ingestion pipeline
├── shared/                # Shared utilities and models
├── tests/                 # Test files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Supabase account (for database)
- Qdrant instance (cloud or self-hosted)
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/uov-ai-assistant.git
   cd uov-ai-assistant
   ```

2. **Create virtual environment** (using uv)
   ```bash
   uv venv --python 3.11
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual credentials
   # - SUPABASE_URL and SUPABASE_KEY
   # - QDRANT_URL and QDRANT_API_KEY
   # - GROQ_API_KEY
   ```

## Usage

### Running the Backend

```bash
cd backend_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running the Frontend

```bash
cd streamlit_ui
streamlit run app.py --server.port 8501
```

### Document Ingestion

```bash
cd ingestion
python cli.py --input /path/to/documents
```

## Development Status

- [x] Phase 0: Project Initialization & Environment Setup
- [ ] Phase 1: Data Modeling (Storage Layer)
- [ ] Phase 2: Document Ingestion Pipeline
- [ ] Phase 3: Retrieval Layer
- [ ] Phase 4: RAG Orchestration
- [ ] Phase 5: FastAPI Backend Development
- [ ] Phase 6: Streamlit UI Development
- [ ] Phase 7: Integration & Testing
- [ ] Phase 8: Performance Stabilization
- [ ] Phase 9: Deployment
- [ ] Phase 10: Documentation

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Ingestion Guide](docs/INGESTION.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

MIT License - see LICENSE file for details

## Contact

University of Vavuniya - Faculty of Technology