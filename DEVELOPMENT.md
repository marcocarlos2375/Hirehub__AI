# 🛠️ HireHubAI Development Guide

## 🏗️ Architecture Overview

### Backend (FastAPI + Python)

```
backend/
├── app/
│   ├── main.py          # API routes & FastAPI app
│   ├── models.py        # SQLAlchemy database models
│   ├── database.py      # Database configuration
│   ├── config.py        # Settings (Pydantic)
│   └── services/        # Business logic
│       ├── cv_parser.py      # PDF/DOCX → JSON
│       ├── jd_analyzer.py    # Job description analysis
│       ├── embeddings.py     # Vector embeddings
│       ├── qdrant_service.py # Vector database
│       ├── scorer.py         # Compatibility scoring
│       ├── question_gen.py   # Question generation
│       └── cv_optimizer.py   # CV optimization + PDF
```

### Frontend (Nuxt 3 + Vue.js)

```
frontend/
├── pages/
│   ├── index.vue            # Home (upload)
│   ├── analysis/[id].vue    # Results page
│   └── questions/[id].vue   # Questions page
├── composables/
│   └── useApi.ts            # API client
└── assets/css/
    └── main.css             # Tailwind CSS
```

## 🔧 Development Workflow

### Backend Development

1. **Make changes to Python files**
2. **Container auto-reloads** (uvicorn --reload)
3. **Test API**: http://localhost:8000/docs

### Frontend Development

1. **Make changes to Vue files**
2. **HMR auto-reloads** (Nuxt 3 dev server)
3. **View changes**: http://localhost:3000

## 📝 Adding New Features

### Add a New API Endpoint

**1. Create service in `backend/app/services/`**

```python
# backend/app/services/my_service.py
from app.config import get_settings
import google.generativeai as genai

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def my_feature(data: dict) -> dict:
    # Your logic here
    return {"result": "success"}
```

**2. Add route in `backend/app/main.py`**

```python
from app.services.my_service import my_feature

@app.post("/api/my-endpoint")
async def my_endpoint(data: dict):
    result = my_feature(data)
    return result
```

**3. Use in frontend `composables/useApi.ts`**

```typescript
const myFeature = async (data: any) => {
  return await $fetch(`${apiBase}/api/my-endpoint`, {
    method: 'POST',
    body: data
  })
}
```

### Add a New Page

**1. Create Vue file in `frontend/pages/`**

```vue
<!-- frontend/pages/my-page.vue -->
<template>
  <div class="container">
    <h1>My Page</h1>
  </div>
</template>

<script setup lang="ts">
// Your logic here
</script>
```

**2. Navigate to it**

```typescript
await navigateTo('/my-page')
```

## 🧪 Testing

### Test Backend Locally (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key_here
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export DATABASE_URL=sqlite:///data/hirehub.db

# Run server
uvicorn app.main:app --reload
```

### Test Frontend Standalone

```bash
cd frontend
npm run dev
# Frontend will proxy API calls to localhost:8000
```

### Manual Testing Checklist

- [ ] Upload PDF CV
- [ ] Upload DOCX CV
- [ ] Paste long job description
- [ ] Verify compatibility score appears
- [ ] Check gaps and strengths
- [ ] Answer questions
- [ ] Download optimized PDF
- [ ] Verify PDF opens correctly

## 🐛 Debugging

### Backend Debugging

**View logs:**
```bash
docker-compose logs -f backend
```

**Access container:**
```bash
docker exec -it hirehub-backend bash
python
>>> from app.services.cv_parser import parse_cv_with_gemini
>>> # Test functions interactively
```

**Check database:**
```bash
docker exec -it hirehub-backend bash
cd /app/data
sqlite3 hirehub.db
.tables
SELECT * FROM cv_analyses;
```

### Frontend Debugging

**Vue DevTools:**
- Install Vue DevTools browser extension
- Open browser dev tools
- Check Vue tab

**Check API calls:**
- Open Network tab
- Filter by "Fetch/XHR"
- Inspect request/response

### Qdrant Debugging

**Check collections:**
```bash
curl http://localhost:6333/collections
```

**View collection info:**
```bash
curl http://localhost:6333/collections/cv_embeddings
```

**Dashboard:**
http://localhost:6333/dashboard

## 🔍 Code Quality

### Python (Backend)

```bash
# Format code
black backend/app/

# Lint
flake8 backend/app/

# Type checking
mypy backend/app/
```

### TypeScript (Frontend)

```bash
cd frontend

# Type checking
npx nuxi typecheck

# Lint
npm run lint
```

## 📚 Key Dependencies

### Backend

| Package | Purpose |
|---------|---------|
| fastapi | Web framework |
| google-generativeai | Gemini API |
| qdrant-client | Vector database |
| sentence-transformers | Embeddings |
| pymupdf | PDF parsing |
| python-docx | DOCX parsing |
| reportlab | PDF generation |
| sqlalchemy | ORM |

### Frontend

| Package | Purpose |
|---------|---------|
| nuxt | Framework |
| @nuxtjs/tailwindcss | Styling |
| @pinia/nuxt | State management |
| typescript | Type safety |

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Replace SQLite with PostgreSQL
- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Add error tracking (Sentry)
- [ ] Configure CORS for production domain
- [ ] Set up file cleanup cron job
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Enable HTTPS
- [ ] Set up CDN for frontend
- [ ] Configure environment variables securely
- [ ] Add backup strategy for database
- [ ] Implement logging aggregation

### Environment Variables (Production)

```bash
# Backend
GEMINI_API_KEY=secret
QDRANT_HOST=qdrant.production.com
QDRANT_PORT=6333
DATABASE_URL=postgresql://user:pass@host:5432/db

# Frontend
NUXT_PUBLIC_API_BASE=https://api.hirehubai.com
```

## 📈 Performance Optimization

### Backend

- Cache Gemini responses (Redis)
- Batch embedding generation
- Database connection pooling
- Use Celery for async tasks

### Frontend

- Enable SSR/SSG for static pages
- Lazy load routes
- Optimize images (nuxt/image)
- Enable compression

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📞 Support

- Check logs first
- Search existing issues
- Create detailed bug report

---

**Happy coding! 🎉**
