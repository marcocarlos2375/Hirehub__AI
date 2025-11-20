# HireHubAI Setup & Testing Guide

## 🎉 Congratulations! Your System is Built

All backend and frontend files have been created. Follow these steps to get everything running.

---

## Step 1: Add Your Gemini API Key

**IMPORTANT:** Before starting, you must add your actual Gemini API key.

Edit the `.env` file in the project root:

```bash
# Open the file in your editor
open .env

# Or use nano
nano .env
```

Replace `your_gemini_api_key_here` with your actual key from:
https://makersuite.google.com/app/apikey

The `.env` file should look like:
```
GEMINI_API_KEY=AIzaSy...your_actual_key_here
QDRANT_HOST=qdrant
QDRANT_PORT=6333
DATABASE_URL=sqlite:////app/data/hirehub.db
```

---

## Step 2: Start the Backend (Docker)

```bash
# Navigate to project root
cd /Users/carlosid/Desktop/HireHub__AI

# Stop any existing containers that might conflict
docker stop hirehub-qdrant hirehub-backend 2>/dev/null || true
docker rm hirehub-qdrant hirehub-backend 2>/dev/null || true

# Build and start the services
docker-compose up --build -d

# Watch the logs to confirm startup
docker-compose logs -f backend
```

**Expected output:**
```
🚀 Initializing Qdrant collections...
✓ Collection 'cv_embeddings' already exists (or created)
✓ Collection 'jd_embeddings' already exists (or created)
✓ Collection 'skills_embeddings' already exists (or created)
✅ HireHubAI Backend Ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Press `Ctrl+C` to exit log view (containers keep running).

---

## Step 3: Test Backend Endpoints

```bash
# Test health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test root endpoint
curl http://localhost:8000/
# Expected: JSON with version info

# Test Qdrant
curl http://localhost:6333/collections
# Expected: JSON with 3 collections
```

If all three work, **backend is ready!** ✅

---

## Step 4: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install all dependencies (this will take a few minutes)
npm install

# This should install:
# - Nuxt 3
# - Tailwind CSS
# - Pinia
# - TypeScript
# - All dev dependencies
```

---

## Step 5: Start Frontend Dev Server

```bash
# From the frontend directory
npm run dev
```

**Expected output:**
```
Nuxt 3.10.0 with Nitro 2.8.0

  > Local:    http://localhost:3000/
  > Network:  use --host to expose

ℹ Using Tailwind CSS from ~/assets/css/main.css
✔ Vite client built in 2.5s
✔ Nuxt Nitro built in 1.2s

✔ Ready in 4s
```

---

## Step 6: Test the Complete Flow

### 6.1 Open the App
Visit: **http://localhost:3000**

You should see the HireHubAI home page with:
- Large "HireHubAI" heading
- CV upload input
- Job description textarea
- "Analyze & Optimize" button

### 6.2 Prepare Test Data

**Test CV:** Create a simple test file or use your own CV (PDF or DOCX)

**Test Job Description:** Copy a real job posting or use this sample:

```
Software Engineer - Full Stack
Company: TechCorp
Location: San Francisco, CA

Requirements:
- 3+ years of experience with JavaScript/TypeScript
- Strong experience with React, Node.js
- Experience with databases (MongoDB, PostgreSQL)
- Excellent problem-solving skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Build and maintain web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews

Nice to have:
- Experience with Docker
- Cloud deployment experience (AWS, GCP)
- Knowledge of CI/CD pipelines
```

### 6.3 Complete the Flow

1. **Upload CV** - Click file input and select your CV
2. **Paste JD** - Copy/paste job description
3. **Click "Analyze & Optimize"** - Should show loading spinner
4. **Wait for Analysis** - Takes 15-30 seconds (AI processing)
5. **View Results Page** - Should redirect to `/analysis/{id}` with:
   - Compatibility score (0-100%)
   - Score breakdown by category
   - Strengths list
   - Gaps list
   - Smart questions
6. **Answer Questions** - Click "Answer Questions & Optimize CV"
7. **Fill Answers** - Type responses to generated questions
8. **Generate Optimized CV** - Click "Generate Optimized CV"
9. **Download PDF** - Browser should download optimized CV as PDF

---

## Step 7: Verify Everything Works

### Backend Health Checks

```bash
# Check backend container is running
docker ps | grep hirehub

# Check Qdrant container is running
docker ps | grep qdrant

# View backend logs
docker-compose logs backend | tail -20

# View Qdrant logs
docker-compose logs qdrant | tail -20
```

### Frontend Health Checks

```bash
# From frontend directory, check dev server is running
lsof -i :3000

# Check for any console errors in browser:
# Open browser DevTools (F12) > Console tab
# Should have no red errors
```

### Database Check

```bash
# Check SQLite database was created
ls -lh backend/data/
# Should see: hirehub.db

# Check uploaded files
ls -lh backend/uploads/
# Should see your test CV

# Check generated PDFs
ls -lh backend/outputs/
# Should see optimized_cv_*.pdf files
```

---

## Troubleshooting

### Problem: "Port already in use" errors

**Solution:**
```bash
# Find and kill processes on conflicting ports
lsof -ti:8000 | xargs kill -9  # Backend port
lsof -ti:3000 | xargs kill -9  # Frontend port
lsof -ti:6333 | xargs kill -9  # Qdrant port

# Then restart services
docker-compose up -d
cd frontend && npm run dev
```

### Problem: "Gemini API error" in backend logs

**Solution:**
1. Check your `.env` file has the correct API key
2. Verify the key works: Visit https://makersuite.google.com/app/apikey
3. Restart backend:
   ```bash
   docker-compose restart backend
   ```

### Problem: Frontend can't connect to backend (CORS error)

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/app/main.py` (line 40)
3. Restart both services

### Problem: "Module not found" errors in frontend

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Problem: Qdrant connection errors

**Solution:**
```bash
# Restart Qdrant
docker-compose restart qdrant

# Check Qdrant is accessible
curl http://localhost:6333/collections

# If still failing, rebuild:
docker-compose down -v
docker-compose up -d
```

---

## Stopping the Services

### Stop Backend (Docker)
```bash
cd /Users/carlosid/Desktop/HireHub__AI
docker-compose down
```

### Stop Frontend
```bash
# In terminal running npm run dev, press: Ctrl+C
```

---

## Restarting Later

### Start Backend
```bash
cd /Users/carlosid/Desktop/HireHub__AI
docker-compose up -d
```

### Start Frontend
```bash
cd frontend
npm run dev
```

---

## Next Steps

Once everything is working, you can:

1. **Add Production Improvements** (see README.md "Potential Considerations")
   - Error handling enhancements
   - Rate limiting
   - File cleanup automation
   - Monitoring/logging

2. **Deploy to Production**
   - Update CORS origins in backend
   - Set up proper environment variables
   - Deploy backend to cloud (AWS, GCP, Railway)
   - Deploy frontend to Vercel/Netlify
   - Use managed Qdrant Cloud

3. **Enhance Features**
   - Add cover letter generation
   - Implement LinkedIn profile optimization
   - Add interview prep questions
   - Build feedback loop for outcome tracking

---

## File Structure Reference

```
HireHub__AI/
├── .env                      # ⚠️ Add your Gemini API key here!
├── .env.example
├── docker-compose.yml
├── SETUP_GUIDE.md           # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── data/                # SQLite database
│   ├── uploads/             # Uploaded CVs
│   ├── outputs/             # Generated PDFs
│   └── app/
│       ├── main.py          # FastAPI routes
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       └── services/        # 7 AI services
│
└── frontend/
    ├── package.json
    ├── nuxt.config.ts
    ├── pages/              # 3 pages (index, analysis, questions)
    └── composables/        # useApi.ts

---

## Success Indicators

✅ Backend running on http://localhost:8000
✅ Frontend running on http://localhost:3000
✅ Qdrant running on http://localhost:6333
✅ Can upload CV and get analysis
✅ Can answer questions
✅ Can download optimized PDF
✅ SQLite database created in backend/data/
✅ No errors in console or logs

**If all above are ✅, you're ready to use HireHubAI!** 🎉

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs backend`
2. Check frontend console (F12 in browser)
3. Verify all prerequisites are installed
4. Ensure .env has valid Gemini API key
5. Try rebuilding: `docker-compose up --build -d`

Happy optimizing! 🚀
