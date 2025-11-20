# HireHubAI - AI-Powered CV Optimization Platform

Built with **Nuxt 3**, **FastAPI**, **Google Gemini 2.0 Flash-Lite**, and **Qdrant Vector Database**.

## 🚀 Features

### Core Features (Phases 1-6)
- 🤖 AI-powered CV parsing with Gemini 2.0
- 📊 Compatibility scoring (0-100%)
- 🧠 RAG-enhanced analysis with Qdrant
- 💬 Smart question generation
- ✨ CV optimization
- 📄 PDF export

### Extended Features (Phases 7-9)
- 📝 AI-generated cover letters
- 🎓 Personalized learning recommendations
- 🎤 Comprehensive interview preparation
- ⭐ STAR method examples
- 🔧 Technical deep dive guides

### UI/UX
- 🎨 Beautiful UI with Geist font
- 📱 Responsive design
- ⚡ Fast and intuitive

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- Google Gemini 2.0 Flash-Lite
- Qdrant Vector Database
- SQLite
- Docker

**Frontend:**
- Nuxt 3
- Vue 3
- Tailwind CSS
- TypeScript
- Geist Font

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Gemini API Key (get from https://makersuite.google.com/app/apikey)

## ⚙️ Setup & Run

### 1. Clone and configure

```bash
# Create .env file in root
cp .env.example .env

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env
```

### 2. Start backend services (Docker)

```bash
# Start backend + Qdrant
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

Backend will run on: **http://localhost:8000**
Qdrant will run on: **http://localhost:6333**

### 3. Start frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: **http://localhost:3000**

## 🎯 Usage

### Complete 9-Phase Process

**Phase 1-3: Analysis**
1. Open **http://localhost:3000**
2. Upload your CV (PDF/DOCX)
3. Paste job description
4. Get compatibility score with breakdown

**Phase 4-6: Optimization**
5. Review strengths and gaps
6. Answer smart questions to uncover hidden experience
7. Download your optimized CV as PDF

**Phase 7: Cover Letter**
8. Generate personalized cover letter
9. Download cover letter as PDF

**Phase 8: Learning Path**
10. View personalized learning recommendations
11. See course suggestions (Udemy, Coursera, etc.)
12. Follow 10-week roadmap to improve skills

**Phase 9: Interview Prep**
13. Access stage-by-stage interview guide
14. Practice with suggested answers based on your experience
15. Review STAR method examples
16. Prepare smart questions to ask interviewers

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild backend
docker-compose up -d --build backend

# View logs
docker-compose logs -f

# Access backend shell
docker exec -it hirehub-backend bash

# Access Qdrant
curl http://localhost:6333/collections
```

## 📁 Project Structure

```
HireHub__AI/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app with all routes
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── database.py                # Database connection
│   │   ├── config.py                  # Settings
│   │   └── services/
│   │       ├── cv_parser.py           # PDF/DOCX → JSON (Phase 1)
│   │       ├── jd_analyzer.py         # JD analysis (Phase 2)
│   │       ├── embeddings.py          # Vector embeddings
│   │       ├── qdrant_service.py      # Qdrant operations + RAG
│   │       ├── scorer.py              # Compatibility scoring (Phase 3)
│   │       ├── question_gen.py        # Question generation (Phase 4)
│   │       ├── cv_optimizer.py        # CV optimization + PDF (Phase 5-6)
│   │       ├── cover_letter_gen.py    # Cover letter generation (Phase 7)
│   │       ├── learning_recommender.py # Learning path (Phase 8)
│   │       └── interview_prep.py      # Interview prep (Phase 9)
│   ├── data/                          # SQLite database
│   ├── uploads/                       # Uploaded CVs
│   ├── outputs/                       # Generated PDFs (CVs & cover letters)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   │   ├── index.vue                  # Home page - CV upload
│   │   ├── analysis/[id].vue          # Analysis results (Phases 1-3)
│   │   ├── questions/[id].vue         # Questions page (Phase 4)
│   │   ├── learning/[id].vue          # Learning path (Phase 8)
│   │   └── interview/[id].vue         # Interview prep (Phase 9)
│   ├── composables/
│   │   └── useApi.ts                  # API client
│   ├── assets/css/
│   │   └── main.css                   # Tailwind CSS
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔌 API Endpoints

### Backend API (http://localhost:8000)

| Endpoint | Method | Description | Phase |
|----------|--------|-------------|-------|
| `GET /` | GET | Health check | - |
| `GET /health` | GET | Health status | - |
| `POST /api/upload-cv` | POST | Upload CV + JD, get analysis | 1-3 |
| `GET /api/analysis/{id}` | GET | Get analysis results | 1-3 |
| `POST /api/submit-answers/{id}` | POST | Submit answers, optimize CV | 4-6 |
| `GET /api/download-cv/{id}` | GET | Download optimized CV PDF | 6 |
| `POST /api/generate-cover-letter/{id}` | POST | Generate cover letter | 7 |
| `GET /api/download-cover-letter/{id}` | GET | Download cover letter PDF | 7 |
| `GET /api/learning-recommendations/{id}` | GET | Get personalized learning path | 8 |
| `GET /api/interview-prep/{id}` | GET | Get interview preparation guide | 9 |

## ⚠️ Known Limitations

This is an MVP with the following limitations:

- ❌ No authentication or user accounts
- ❌ No rate limiting (Gemini API could hit quotas)
- ❌ No file cleanup (files accumulate)
- ❌ SQLite limitations (not for high concurrency)
- ❌ No error recovery UI
- ❌ Cold start problem (empty Qdrant initially)
- ❌ Hardcoded CORS (localhost only)

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check Docker logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down
docker-compose up -d --build
```

### Frontend errors

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .nuxt
npm install
npm run dev
```

### Gemini API errors

- Check your API key in `.env`
- Verify quota at https://makersuite.google.com
- Check API rate limits

### Qdrant connection issues

```bash
# Check Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker-compose restart qdrant
```

## 📈 Future Improvements

- Add authentication and user accounts
- Implement rate limiting
- Add file cleanup cron job
- PostgreSQL for production
- Implement feedback loop for RAG improvement
- Add multi-language support
- Create admin dashboard
- Add salary negotiation guidance
- Resume version control
- Application tracking system integration

## 📄 License

MIT

## 🙏 Acknowledgments

- Built with Google Gemini 2.0 Flash-Lite
- Vector search powered by Qdrant
- UI inspired by modern design principles
- Font: Geist by Vercel

---

**Made with ❤️ for job seekers everywhere**
