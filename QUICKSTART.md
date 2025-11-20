# 🚀 HireHubAI Quick Start Guide

## ⏱️ 5-Minute Setup

### 1. Get Your Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

### 3. Start Backend (Docker)

```bash
# Make sure Docker Desktop is running!
docker-compose up -d

# Check it's working
curl http://localhost:8000
# Should return: {"message":"HireHubAI API is running"...}
```

### 4. Start Frontend (Node.js)

```bash
cd frontend
npm install
npm run dev
```

### 5. Open Application

Open http://localhost:3000 in your browser!

---

## 📊 Complete 9-Phase User Journey

### Phase 1-3: Analysis & Scoring
1. **Upload CV + Paste JD** → AI parses both documents with Gemini 2.0
2. **Get Score** → See 0-100% compatibility score with detailed breakdown
3. **Review Results** → See strengths, gaps, and areas to improve

### Phase 4-6: CV Optimization
4. **Answer Questions** → 5-8 smart questions to uncover hidden skills
5. **Get Optimized CV** → AI enhances your CV based on JD requirements
6. **Download PDF** → Get ATS-friendly, professionally formatted PDF

### Phase 7: Cover Letter
7. **Generate Cover Letter** → AI creates personalized cover letter
8. **Download PDF** → Get matching cover letter document

### Phase 8: Learning Path
9. **View Learning Plan** → Personalized course recommendations
10. **Follow Roadmap** → 10-week plan with specific courses (Udemy, Coursera, etc.)

### Phase 9: Interview Preparation
11. **Review Interview Guide** → Stage-by-stage preparation (Phone, Technical, Behavioral, Final)
12. **Practice Answers** → Suggested answers based on YOUR actual experience
13. **STAR Examples** → Ready-to-use behavioral interview examples
14. **Prepare Questions** → Smart questions to ask interviewers

---

## 🛠️ Troubleshooting

### Backend won't start

```bash
docker-compose logs backend
# Check for errors about GEMINI_API_KEY
```

### Frontend errors

```bash
cd frontend
rm -rf node_modules .nuxt
npm install
npm run dev
```

### "Can't connect to backend"

- Backend must be running on http://localhost:8000
- Check Docker: `docker ps | grep hirehub`
- Restart: `docker-compose restart backend`

---

## 🔑 Important URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Backend Docs | http://localhost:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## 📁 File Locations

- **Uploaded CVs**: `backend/uploads/`
- **Generated PDFs**: `backend/outputs/` (optimized CVs + cover letters)
- **Database**: `backend/data/hirehub.db` (SQLite)
- **Vector DB**: Qdrant (in-memory, resets on container restart)

---

## 🎯 Example Usage

### Test with Sample Data

**Sample Job Description:**
```
Senior Software Engineer
New York, NY | $150K-200K

Requirements:
- 5+ years experience with React, TypeScript, Node.js
- Strong background in full-stack development
- Experience with cloud platforms (AWS/GCP)
- Excellent communication skills

Responsibilities:
- Build scalable web applications
- Mentor junior developers
- Collaborate with product team
```

Upload any PDF/DOCX CV and paste the above JD to test!

---

## 🚨 Common Issues

### 1. "Gemini API Error"
- Check your API key in `.env`
- Verify key is valid at https://makersuite.google.com
- Check API quota limits

### 2. "Qdrant Connection Failed"
```bash
docker-compose restart qdrant
```

### 3. "Frontend build fails"
```bash
cd frontend
rm -rf node_modules .nuxt .output
npm install
npm run dev
```

---

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Need help?** Check the logs:
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
# (shown in terminal where you ran npm run dev)
```

---

**🎉 Happy CV optimizing!**
