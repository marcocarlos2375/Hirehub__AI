# Testing Instructions - 4 Refactored Services

## 🎯 What We're Testing

You now have 4 services refactored with LangChain:
1. ✅ **cv_parser.py** - Parses CV files (PDF/DOCX) into structured data
2. ✅ **jd_analyzer.py** - Analyzes job descriptions
3. ✅ **question_gen.py** - Generates smart questions
4. ✅ **cover_letter_gen.py** - Creates cover letters

The remaining 4 services still use the old approach, so the system will have mixed old/new code during this test.

---

## 🚀 Quick Test Steps

### Step 1: Rebuild Docker (Install LangChain)

```bash
cd /Users/carlosid/Desktop/HireHub__AI

# Stop existing containers
docker-compose down

# Rebuild with new dependencies (this will take 2-3 minutes)
docker-compose up --build -d
```

**Watch for:**
- ✅ "Building backend" - should complete without errors
- ✅ Installing langchain-core, langchain-google-genai, langchain-community
- ✅ "✅ HireHubAI Backend Ready!" in logs

### Step 2: Check Logs for Errors

```bash
# Watch backend startup
docker-compose logs -f backend

# Look for:
# ✅ No "ModuleNotFoundError"
# ✅ No "ImportError"
# ✅ "🚀 Initializing Qdrant collections..."
# ✅ "✅ HireHubAI Backend Ready!"

# Press Ctrl+C to exit logs
```

### Step 3: Test Backend Health

```bash
# Test API is responding
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Test Qdrant is running (note port 6335)
curl http://localhost:6335/collections

# Should return JSON with collections
```

### Step 4: Start Frontend

```bash
# In a new terminal
cd /Users/carlosid/Desktop/HireHub__AI/frontend

# Start dev server
npm run dev

# Should start on http://localhost:3000
```

### Step 5: End-to-End Test

1. **Open browser:** http://localhost:3000

2. **Prepare test files:**
   - Get a sample CV (PDF or DOCX)
   - Copy a job description from any job posting

3. **Upload and analyze:**
   - Upload your CV
   - Paste the job description
   - Click "Analyze & Optimize"

4. **What to watch for:**
   - ⏳ Loading indicator appears
   - ⏳ Wait 15-30 seconds (Gemini API processing)
   - ✅ Redirects to analysis page
   - ✅ **Compatibility score displays** (cv_parser + jd_analyzer working!)
   - ✅ Score breakdown shows
   - ✅ Gaps and strengths appear
   - ✅ **Smart questions are generated** (question_gen working!)

5. **Test questions (optional):**
   - Answer the generated questions
   - Submit answers
   - Check if optimized CV is created

6. **Test cover letter (optional):**
   - Generate cover letter
   - Check if it's created successfully
   - Download PDF

---

## ✅ Success Criteria

### Must Work:
- [x] Docker builds without errors
- [x] Backend starts successfully
- [x] No import errors for langchain modules
- [x] CV upload completes (tests cv_parser.py)
- [x] Job description analysis works (tests jd_analyzer.py)
- [x] Compatibility score displays
- [x] Questions are generated (tests question_gen.py)

### Should Work:
- [x] Answer questions and get optimized CV
- [x] Generate cover letter (tests cover_letter_gen.py)
- [x] Download cover letter PDF

### Known Behavior:
- ⚠️ **learning_recommendations, interview_prep, cv_optimizer, scorer** still use OLD code
- ⚠️ They should still work (not refactored yet)
- ⚠️ No regressions expected - just not using LangChain yet

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'langchain_google_genai'"

**Solution:**
```bash
# Force rebuild
docker-compose build --no-cache backend
docker-compose up -d
```

### Error: "ValidationError" in logs

**Cause:** Pydantic schema doesn't match Gemini output

**Check:**
```bash
# View full error
docker-compose logs backend | tail -100

# Look for the specific field that failed validation
```

**Fix:** The schemas should match, but if there's an issue, we can adjust them.

### Error: "Gemini API 429 - Rate Limit"

**Solution:**
- Wait 2-3 minutes
- Try again
- Check quota at https://makersuite.google.com

### Error: CV parsing fails silently

**Check:**
```bash
# Look for errors in backend logs
docker-compose logs backend | grep -i error

# Check if CV text was extracted
docker-compose logs backend | grep "Extract"
```

### Different output format than expected

**This shouldn't happen** because we use `.dict(by_alias=True)` to maintain backward compatibility, but if it does:

```bash
# Check the actual API response
# Open browser DevTools → Network tab → Look at API responses
```

---

## 📊 What Each Service Does

### cv_parser.py (REFACTORED ✅)
**What:** Extracts text from CV file and structures it with Gemini
**Input:** PDF or DOCX file
**Output:** JSON with personalInfo, employmentHistory, skills, etc.
**New features:**
- Type-safe with CVData schema
- Auto-retry on failures
- Better error messages

### jd_analyzer.py (REFACTORED ✅)
**What:** Analyzes job description text
**Input:** Raw JD text
**Output:** JSON with requirements, skills, company info
**New features:**
- Type-safe with JDData schema
- Auto-retry on failures
- Validates all required fields

### question_gen.py (REFACTORED ✅)
**What:** Generates smart questions to uncover hidden experience
**Input:** CV data, JD data, gaps from scoring
**Output:** Array of questions with suggested answers
**New features:**
- Type-safe with QuestionsList schema
- Validates suggested_answers array
- RAG context preserved

### cover_letter_gen.py (REFACTORED ✅)
**What:** Generates personalized cover letter
**Input:** Optimized CV, JD, user answers
**Output:** Cover letter with sections + full text
**New features:**
- Type-safe with CoverLetterData schema
- Complex nested structure validated
- PDF generation unchanged

---

## 🎯 Expected Improvements

### Reliability
- **Before:** Network errors → immediate failure
- **After:** Network errors → 3 automatic retries

### Error Messages
- **Before:** "Error parsing CV: Expecting value"
- **After:** "ValidationError: field 'firstName' required in personalInfo"

### Code Quality
- **Before:** 30+ lines of manual JSON/markdown parsing per service
- **After:** 2 lines with PydanticOutputParser

---

## 📞 Report Back

After testing, please share:

1. **✅ or ❌** - Did Docker build succeed?
2. **✅ or ❌** - Did backend start without import errors?
3. **✅ or ❌** - Did CV upload work?
4. **✅ or ❌** - Did score display correctly?
5. **✅ or ❌** - Were questions generated?
6. **Any error messages** you encountered

Based on your results:
- ✅ **If all pass** → I'll complete the remaining 4 services
- ❌ **If issues found** → I'll debug and fix before continuing

---

## 🔄 Rollback Plan (if needed)

If critical issues occur:

```bash
# Restore ALL original files
cp backend/app/services/cv_parser_old_backup.py backend/app/services/cv_parser.py
cp backend/app/services/jd_analyzer_old_backup.py backend/app/services/jd_analyzer.py
cp backend/app/services/question_gen_old_backup.py backend/app/services/question_gen.py
cp backend/app/services/cover_letter_gen_old_backup.py backend/app/services/cover_letter_gen.py

# Rebuild
docker-compose up --build -d
```

---

**Ready to test! 🚀**

Let me know the results and we'll proceed accordingly.
