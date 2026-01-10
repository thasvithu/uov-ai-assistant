---
title: UOV AI Assistant Backend
emoji: 🚀
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# UOV AI Assistant - Backend API

FastAPI backend for the UOV AI Assistant chatbot.

## Features
- RAG-based question answering
- Qdrant vector search
- Groq LLM integration
- Response caching
- Rate limiting

## API Endpoints
- `GET /health` - Health check
- `POST /chat` - Chat endpoint
- `POST /feedback` - Submit feedback
- `GET /session/{session_id}/history` - Get chat history
