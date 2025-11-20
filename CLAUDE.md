# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HireHubAI is an AI-powered CV optimization platform that helps users optimize their resumes for specific job descriptions. The system uses Google Gemini 2.0 Flash for AI processing, Qdrant for vector search/RAG, and provides a complete end-to-end workflow from CV upload to optimized PDF generation.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11), Dockerized with SQLite database
- **Frontend:** Nuxt 3 (Vue.js), TypeScript, Tailwind CSS
- **AI/ML:** Google Gemini 2.0 Flash API, sentence-transformers for embeddings
- **Vector DB:** Qdrant (for RAG-enhanced analysis)
- **Infrastructure:** Docker Compose orchestrating backend + Qdrant services

## Development Commands

### Backend (Docker)

```bash
# Start all services (backend + Qdrant)
docker-compose up -d

# View backend logs
docker-compose logs -f backend

# View Qdrant logs
docker-compose logs -f qdrant

# Rebuild backend after code changes
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Stop and remove volumes (full reset)
docker-compose down -v

# Access backend container shell
docker exec -it hirehub-backend bash

# Test backend health
curl http://localhost:8000/health

# Test Qdrant collections (note port mapping to 6335)
curl http://localhost:6335/collections
```

### Frontend (Nuxt 3)

```bash
# Install dependencies
cd frontend && npm install

# Start development server (runs on port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Generate static site
npm run generate
```

### Environment Setup

1. Copy `.env.example` to `.env` in the root directory
2. Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
3. Get API key from: https://makersuite.google.com/app/apikey

## Architecture

### System Flow

1. **Upload & Parse:** User uploads CV (PDF/DOCX) + pastes job description
2. **AI Parsing:** Gemini extracts structured data from both CV and JD
3. **Embedding Generation:** sentence-transformers creates vector embeddings
4. **Vector Storage:** Embeddings stored in Qdrant collections
5. **RAG-Enhanced Scoring:** Compatibility score calculated using vector similarity search
6. **Question Generation:** Smart questions generated to uncover hidden experience
7. **CV Optimization:** User answers feed into Gemini to rewrite CV with RAG context
8. **Additional Features:** Cover letter generation, learning recommendations, interview prep
9. **PDF Generation:** ReportLab creates downloadable optimized CV and cover letter

### Backend Architecture

**Core Services (backend/app/services/):**
- `embeddings.py` - SentenceTransformer wrapper, generates 384-dimensional vector embeddings
- `qdrant_service.py` - Qdrant client management, vector CRUD operations, RAG context retrieval
- `cv_parser.py` - PDF/DOCX text extraction + Gemini parsing to structured JSON
- `jd_analyzer.py` - Job description analysis and requirement extraction
- `scorer.py` - AI-based compatibility scoring with RAG context from similar CVs/JDs
- `vector_scorer.py` - Deterministic vector similarity scoring (objective backup to AI scorer)
- `question_gen.py` - Smart question generation using RAG patterns
- `cv_optimizer.py` - CV rewriting with RAG + PDF generation via ReportLab
- `cover_letter_gen.py` - Personalized cover letter generation with RAG + PDF export
- `learning_recommendations.py` - Skill gap analysis and learning path generation
- `interview_prep.py` - Interview question and answer generation based on JD

**Database Model (models.py):**
- Single table: `cv_analyses` stores everything
- Fields: cv_data, jd_data, scores, questions, answers, optimized_cv, cover_letter, learning_path, interview_prep
- SQLite file-based at `/app/data/hirehub.db` (Docker volume mounted)
- Qdrant embedding IDs (cv_embedding_id, jd_embedding_id) stored for cross-referencing

**API Endpoints (main.py):**
- `POST /api/upload-cv` - Upload CV + JD, returns analysis ID and initial score
- `GET /api/analysis/{id}` - Retrieve full analysis data
- `POST /api/submit-answers/{id}` - Submit question answers, triggers CV optimization
- `GET /api/download-cv/{id}` - Download optimized CV as PDF
- `POST /api/generate-cover-letter/{id}` - Generate cover letter after CV optimization
- `GET /api/download-cover-letter/{id}` - Download cover letter as PDF
- `POST /api/generate-learning-path/{id}` - Generate learning recommendations
- `POST /api/generate-interview-prep/{id}` - Generate interview preparation materials
- `GET /health` - Health check
- `GET /` - API info

### Frontend Architecture

**Pages:**
- `pages/index.vue` - Upload form (CV + job description)
- `pages/analysis/[id].vue` - Score display, breakdown, gaps, strengths
- `pages/questions/[id].vue` - Smart questions form

**Composables:**
- `composables/useApi.ts` - API client with methods for all backend endpoints

**Configuration:**
- `nuxt.config.ts` - Nuxt configuration, API base URL defaults to `http://localhost:8000`
- `tailwind.config.ts` - Tailwind + Geist font setup
- `assets/css/main.css` - Tailwind imports
- CORS allows both `localhost:3000` and `localhost:3001`

### RAG Implementation

**Collections in Qdrant:**
- `cv_embeddings` - Stores CV section embeddings with metadata (name, years_of_experience)
- `jd_embeddings` - Stores job description requirement embeddings (position, company)
- `skills_embeddings` - Reserved for future skill taxonomy

**RAG Context Retrieval:**
- Uses cosine similarity search (Qdrant native)
- Threshold: 0.7 similarity score for relevance
- Top 3 results used for context
- Context injected into Gemini prompts for scoring, questions, optimization, and cover letters

**Key Pattern:** All AI services follow this pattern:
1. Generate query embedding from current context
2. Search Qdrant for similar past cases (limit=3)
3. Filter results by similarity threshold (>0.7)
4. Inject RAG context into Gemini prompt
5. Return AI-generated result with JSON structure

### Port Configuration

**Important:** The actual docker-compose.yml maps ports differently than expected:
- Backend: `8000:8000` (standard)
- Qdrant REST API: `6335:6333` (mapped to avoid conflicts)
- Qdrant gRPC: `6336:6334` (mapped to avoid conflicts)

When testing Qdrant from host machine, use `localhost:6335`, not `6333`.
Inside containers, use `qdrant:6333` (internal network).

## Key Implementation Details

### Gemini API Usage

**Model:** `gemini-2.0-flash-exp` (fast, cost-effective)

**JSON Mode:** All services use `response_mime_type: "application/json"` for structured output

**Response Handling:**
- Strip markdown code blocks (```json) if present
- Parse with `json.loads()`
- Fallback to default structure on error
- Temperature varies by service (0.3 for parsing, 0.4 for creative tasks)

### File Handling

**Upload Flow:**
- Files temporarily saved to `/app/uploads/` during processing
- Files are deleted immediately after text extraction (see `main.py:76-80`)
- PDF parsing: PyMuPDF (fitz)
- DOCX parsing: python-docx
- Full text stored in database, files not retained

**PDF Generation:**
- ReportLab with custom styles
- Output to `/app/outputs/` (Docker volume)
- Files named: `optimized_cv_{analysis_id}.pdf` or `cover_letter_{analysis_id}.pdf`
- Custom ParagraphStyle for headings with blue color (#2563eb)

### Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Distance metric: Cosine similarity
- Cached globally in memory (singleton pattern via `_model` global)
- Batch processing available but typically used for single embeddings

### Database Operations

**Session Management:** FastAPI dependency injection via `get_db()`

**Lifecycle:**
1. Create analysis entry on CV upload
2. Store embeddings in Qdrant, save embedding IDs in database
3. Update with scores and questions after analysis
4. Update with answers and optimized CV after submission
5. Optionally update with cover_letter, learning_path, interview_prep as generated

### Scoring Architecture

**Dual Scoring Approach:**
1. `scorer.py` - AI-based scoring with Gemini (subjective, considers context)
2. `vector_scorer.py` - Deterministic vector similarity scoring (objective, reproducible)

The AI scorer is preferred for nuanced analysis, but vector scorer provides consistent baseline.

## Common Development Tasks

### Adding a New AI Service

1. Create service file in `backend/app/services/`
2. Import Gemini: `import google.generativeai as genai`
3. Configure: `genai.configure(api_key=settings.GEMINI_API_KEY)`
4. Create model: `model = genai.GenerativeModel('gemini-2.0-flash-exp')`
5. If using RAG: generate query embedding → search Qdrant → inject context
6. Set `generation_config` with `response_mime_type: "application/json"`
7. Handle response with markdown stripping
8. Import and use in `main.py` endpoint
9. Update `models.py` if storing new data

### Modifying Prompts

All AI prompts are inline in service files. Search for `prompt = f"""` to locate them:
- CV parsing: `cv_parser.py` (~line 560)
- JD analysis: `jd_analyzer.py` (~line 693)
- Scoring: `scorer.py` (~line 789)
- Questions: `question_gen.py` (~line 901)
- Optimization: `cv_optimizer.py` (~line 982)
- Cover letter: `cover_letter_gen.py` (~line 29)

**Best Practice:** Keep JSON schema in prompt, use `response_mime_type: "application/json"`

### Adding Frontend Pages

1. Create `.vue` file in `frontend/pages/`
2. Use `useApi()` composable for backend calls
3. Follow existing patterns (loading states, error handling, ref() for reactive data)
4. Tailwind classes for styling (Geist font is global via Google Fonts)
5. Use `navigateTo()` for routing

### Testing Backend Changes

```bash
# After code changes, rebuild
docker-compose up -d --build backend

# Watch logs
docker-compose logs -f backend

# Test endpoint
curl -X POST http://localhost:8000/api/upload-cv \
  -F "file=@test.pdf" \
  -F "jd_text=Senior Developer position..."
```

### Debugging Qdrant

```bash
# List collections (use port 6335 from host)
curl http://localhost:6335/collections

# Get collection info
curl http://localhost:6335/collections/cv_embeddings

# Search from backend container
docker exec -it hirehub-backend python
>>> from app.services.qdrant_service import get_qdrant_client
>>> client = get_qdrant_client()
>>> client.scroll("cv_embeddings", limit=5)
```

### Running Database Migrations

Scripts available in `backend/scripts/`:
- `add_new_columns.py` - Adds new columns to existing database
- `migrate_cv_structure.py` - Migrates CV data structures

Run inside container:
```bash
docker exec -it hirehub-backend python backend/scripts/add_new_columns.py
```

## Important Notes

### No Authentication
- This is an MVP with no user authentication
- Anyone with the URL can access any analysis ID
- Do not deploy to public internet without adding auth

### API Key Security
- Gemini API key in `.env` file (never commit)
- Backend reads from environment variables only
- API key required for all Gemini operations

### CORS Configuration
- Currently allows `localhost:3000` and `localhost:3001`
- Update `main.py:27-32` for production deployment
- Use environment variables for production origins

### Data Persistence
- SQLite database: `backend/data/hirehub.db` (volume mounted)
- Qdrant data: Docker volume `qdrant_storage`
- Uploaded files: Deleted after processing (not retained)
- Generated PDFs: `backend/outputs/` (volume mounted, persist indefinitely)
- All persisted across container restarts

### Cold Start Problem
- First users get no RAG context (empty Qdrant collections)
- System improves as more CVs are analyzed
- Consider pre-seeding with sample data for production
- RAG threshold (0.7) means low-quality matches are ignored

### Error Handling
- Backend: Try-catch in all endpoints, returns 500 with error message
- Frontend: Basic error states with user-facing messages
- Gemini errors: Fallback to default structures with error field
- File cleanup: Warnings logged but don't fail requests

## Testing the System

### Manual End-to-End Test

1. Ensure `.env` file exists with valid `GEMINI_API_KEY`
2. Start backend: `docker-compose up -d`
3. Wait for "✅ HireHubAI Backend Ready!" in logs: `docker-compose logs backend`
4. Start frontend: `cd frontend && npm run dev`
5. Navigate to http://localhost:3000
6. Upload CV (PDF/DOCX) and paste job description
7. Verify score displays (takes 15-30 seconds for AI processing)
8. Answer generated questions
9. Download optimized CV PDF
10. Optionally generate cover letter, learning path, interview prep

### Verifying RAG is Working

1. Upload 2-3 CVs with similar skills/experience
2. Check Qdrant has data: `curl http://localhost:6335/collections/cv_embeddings`
3. Upload a new CV and check backend logs for "Similar CV experience" messages
4. RAG context appears in Gemini prompts when similarity > 0.7
5. More data = better RAG context = better recommendations

### Common Issues

**"Gemini API error"**
- Check API key in `.env` is valid
- Verify quota at https://makersuite.google.com
- Check backend logs for specific error message

**"Qdrant connection refused"**
- Ensure Qdrant container running: `docker ps | grep qdrant`
- Check internal network: containers use `qdrant:6333`
- From host, use `localhost:6335` (note port mapping)

**"CORS error" in frontend**
- Verify backend is running on port 8000
- Check CORS origins in `main.py:27-32`
- Ensure `apiBase` in `nuxt.config.ts` matches backend URL

**"Module not found"**
- Run `npm install` in frontend directory
- Check Python dependencies: `docker-compose logs backend` for import errors

**Empty score/questions**
- Check backend logs for Gemini API errors
- Verify CV and JD were parsed (check database or API response)
- Ensure Gemini API key has sufficient quota

**Port conflicts**
- Qdrant mapped to 6335/6336 to avoid conflicts
- If port 8000 or 3000 busy, update docker-compose.yml and nuxt.config.ts

## Production Considerations

This is an MVP. Before production deployment:

1. **Add authentication** - Implement user accounts or JWT-based session management
2. **Rate limiting** - Protect Gemini API from abuse (use `slowapi` or similar)
3. **File validation** - Add size limits (5-10MB), content type verification, virus scanning
4. **Data cleanup** - Implement scheduled jobs to delete old analyses and PDFs (e.g., 30 days)
5. **Database migration** - Switch from SQLite to PostgreSQL for better concurrency
6. **Error monitoring** - Add Sentry or similar for error tracking
7. **Environment variables** - Externalize all config (CORS origins, API base URL, ports)
8. **HTTPS** - Use reverse proxy (nginx/Caddy) with SSL certificates
9. **API documentation** - Enable FastAPI Swagger UI at `/docs` in production
10. **Logging** - Implement structured JSON logs, centralized logging service (e.g., CloudWatch)
11. **Monitoring** - Add health checks, performance monitoring (response times, Gemini API usage)
12. **Caching** - Consider Redis for caching embeddings and API responses
13. **Qdrant scaling** - Move to Qdrant Cloud or separate instance for production
14. **Background jobs** - Use Celery + Redis for long-running tasks (learning path, interview prep)
15. **API versioning** - Add `/v1/` prefix to endpoints for future compatibility
