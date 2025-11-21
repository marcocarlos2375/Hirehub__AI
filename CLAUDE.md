# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HireHub__AI is an AI-powered CV optimization platform that uses Google Gemini 2.0 Flash-Lite for AI analysis and Qdrant vector database for RAG (Retrieval-Augmented Generation). The application follows a 9-phase workflow to help job seekers optimize their CVs, generate cover letters, create learning paths, and prepare for interviews.

**Tech Stack:**
- Backend: FastAPI (Python), Google Gemini 2.0 Flash-Lite, Qdrant, SQLite, Docker
- Frontend: Nuxt 3, Vue 3, Tailwind CSS, TypeScript
- Deployment: Docker Compose with backend and Qdrant services

## Development Commands

### Backend (Docker-based)

```bash
# Start all services (backend + Qdrant)
docker-compose up -d

# View backend logs
docker-compose logs -f backend

# Rebuild backend after code changes
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Access backend shell for debugging
docker exec -it hirehub-backend bash

# Check Qdrant collections
curl http://localhost:6333/collections
```

Backend runs on: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs
Qdrant runs on: http://localhost:6333

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server (with HMR)
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check
# or
npx nuxi typecheck

# Preview production build
npm run preview
```

Frontend runs on: http://localhost:3000

### Local Backend Development (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key_here
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export DATABASE_URL=sqlite:///data/hirehub.db

# Run with auto-reload
uvicorn app.main:app --reload
```

## Architecture

### Backend Services Layer

The backend uses a services-based architecture where `backend/app/main.py` contains all FastAPI routes, and business logic is separated into specialized services in `backend/app/services/`:

- **cv_parser.py**: Extracts text from PDF/DOCX files and parses CVs using Gemini into structured JSON
- **jd_analyzer.py**: Analyzes job descriptions with Gemini to extract requirements
- **embeddings.py**: Generates vector embeddings using sentence-transformers (all-MiniLM-L6-v2)
- **qdrant_service.py**: Manages Qdrant vector database operations and RAG context retrieval
- **scorer.py**: Calculates compatibility scores (0-100%) between CV and job description
- **question_gen.py**: Generates smart questions to uncover hidden experience
- **cv_optimizer.py**: Optimizes CVs based on answers and generates PDF output
- **cover_letter_gen.py**: Generates personalized cover letters (Phase 7)
- **learning_recommender.py**: Creates personalized learning paths (Phase 8)
- **interview_prep.py**: Generates interview preparation guides (Phase 9)
- **toon_serializer.py**: Handles TOON format serialization (experimental)

### Database Schema

The application uses a single SQLAlchemy model (`backend/app/models.py`):

**CVAnalysis** model stores the complete analysis lifecycle:
- CV data: `cv_filename`, `cv_text`, `cv_parsed` (JSON)
- JD data: `jd_text`, `jd_parsed` (JSON)
- Embeddings: `cv_embedding_id`, `jd_embedding_id` (Qdrant point IDs)
- Scoring: `compatibility_score`, `score_breakdown`, `gaps`, `strengths`
- Workflow: `questions`, `answers`, `optimized_cv`
- Extended features: `cover_letter`, `learning_recommendations`, `interview_prep`

### Vector Database (Qdrant)

Three collections are initialized on startup:
- **cv_embeddings**: Stores CV section embeddings for similarity search
- **jd_embeddings**: Stores job description requirement embeddings
- **skills_embeddings**: Reserved for skills matching

RAG implementation in `qdrant_service.py`:
- Embeddings use 384-dimensional vectors (sentence-transformers/all-MiniLM-L6-v2)
- Similarity search uses cosine distance
- RAG context retrieval filters by relevance threshold (>0.7)
- Context is used to enhance Gemini responses with similar CVs/JDs

### Frontend Architecture

Nuxt 3 app with file-based routing:

**Pages:**
- `pages/index.vue`: Home page with CV upload form
- `pages/analysis/[id].vue`: Shows analysis results (Phases 1-3)
- `pages/questions/[id].vue`: Smart questions interface (Phase 4)
- `pages/cover-letter/[id].vue`: Cover letter generation (Phase 7)
- `pages/learning/[id].vue`: Learning recommendations (Phase 8)
- `pages/interview/[id].vue`: Interview preparation (Phase 9)

**API Client:**
- `composables/useApi.ts`: Centralized API calls to backend
- Uses Nuxt's `$fetch` with runtime config for API base URL

### 9-Phase Workflow

1. **Phase 1-3** (Analysis): Upload CV → Parse with Gemini → Analyze JD → Calculate compatibility score with RAG
2. **Phase 4** (Questions): Generate smart questions based on gaps
3. **Phase 5-6** (Optimization): Process answers → Optimize CV → Generate PDF
4. **Phase 7** (Cover Letter): Generate personalized cover letter PDF
5. **Phase 8** (Learning Path): Recommend courses and 10-week roadmap
6. **Phase 9** (Interview Prep): Stage-by-stage interview guide with STAR examples

## Configuration

### Environment Variables

Required in `.env` file (root directory):
```bash
GEMINI_API_KEY=your_key_here  # Get from https://makersuite.google.com/app/apikey
```

Docker Compose sets:
```bash
QDRANT_HOST=qdrant
QDRANT_PORT=6333
DATABASE_URL=sqlite:////app/data/hirehub.db
USE_TOON_FORMAT=true  # Experimental feature
```

### Settings Management

`backend/app/config.py` uses Pydantic settings:
- Loads from `.env` file
- Provides type-safe configuration
- Cached with `@lru_cache()` for performance

## Common Development Tasks

### Adding a New API Endpoint

1. Create service function in `backend/app/services/your_service.py`
2. Import and use in `backend/app/main.py` route
3. Add corresponding method in `frontend/composables/useApi.ts`
4. Create/update page in `frontend/pages/` to use the API

### Debugging Gemini API Issues

- Check API key in `.env`
- View backend logs: `docker-compose logs -f backend`
- Verify quota at https://makersuite.google.com
- Check rate limits (Gemini 2.0 Flash-Lite has generous free tier)

### Debugging Qdrant Issues

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# View collections
curl http://localhost:6333/collections

# Get collection details
curl http://localhost:6333/collections/cv_embeddings

# Access Qdrant dashboard
open http://localhost:6333/dashboard
```

### Inspecting Database

```bash
# Access SQLite database
docker exec -it hirehub-backend bash
cd /app/data
sqlite3 hirehub.db

# Useful queries
.tables
.schema cv_analyses
SELECT id, cv_filename, compatibility_score FROM cv_analyses;
```

### File Storage Locations

Docker volumes map to local directories:
- `backend/data/`: SQLite database (hirehub.db)
- `backend/uploads/`: Uploaded CV files (PDF/DOCX)
- `backend/outputs/`: Generated PDFs (optimized CVs and cover letters)

## Known Limitations (MVP)

- No authentication or user accounts (single-user at a time)
- No rate limiting (Gemini API quotas can be exceeded)
- No file cleanup (uploaded/generated files accumulate)
- SQLite not suitable for concurrent users
- CORS hardcoded to localhost:3000
- Cold start problem (empty Qdrant on first run - RAG improves over time)

## Troubleshooting

**Backend won't start:**
```bash
docker-compose logs backend
docker-compose down && docker-compose up -d --build
```

**Frontend errors:**
```bash
cd frontend
rm -rf node_modules .nuxt
npm install && npm run dev
```

**Type errors:**
```bash
cd frontend
npx nuxi typecheck
```

**Qdrant connection timeout:**
```bash
docker-compose restart qdrant
# Wait 5-10 seconds for Qdrant to initialize
docker-compose restart backend
```
