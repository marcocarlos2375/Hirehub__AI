# LangChain Integration - Testing Guide

## Current Status

### ✅ Completed
- Full Pydantic schema system (8 schema files)
- LangChain dependencies added to requirements.txt
- Prompt templates infrastructure created
- **cv_parser.py fully refactored with LangChain**
- Old cv_parser.py backed up as `cv_parser_old_backup.py`

### 🧪 Ready for Testing
The refactored cv_parser.py is now active and needs validation before we continue with the remaining 7 services.

---

## Testing Steps

### Step 1: Start Docker and Rebuild Backend

```bash
# Start Docker Desktop (or Docker daemon)
# Then run:

cd /Users/carlosid/Desktop/HireHub__AI

# Stop existing containers if any
docker-compose down

# Rebuild with new LangChain dependencies
docker-compose up --build -d

# This will install:
# - langchain-core==0.1.52
# - langchain-google-genai==0.0.11
# - langchain-community==0.0.38
```

### Step 2: Monitor Backend Logs

```bash
# Watch for successful startup
docker-compose logs -f backend

# Look for:
# ✓ "🚀 Initializing Qdrant collections..."
# ✓ "✅ HireHubAI Backend Ready!"
# ✗ Any import errors or dependency issues
```

### Step 3: Test Backend Health

```bash
# Test basic connectivity
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Test Qdrant connectivity (note port 6335 not 6333)
curl http://localhost:6335/collections

# Should return JSON with collections list
```

### Step 4: Start Frontend

```bash
cd frontend
npm install  # In case there are any updates
npm run dev

# Frontend should start on http://localhost:3000
```

### Step 5: End-to-End Test with CV Upload

#### Manual Test:
1. Open http://localhost:3000 in browser
2. Prepare a test CV (PDF or DOCX)
3. Prepare a test job description (copy from any job posting)
4. Upload CV and paste JD
5. Click "Analyze & Optimize"
6. **Expected behavior:**
   - Loading indicator appears
   - After 15-30 seconds, analysis page loads
   - Compatibility score displays (0-100%)
   - Score breakdown shows
   - Gaps and strengths appear
   - Smart questions are generated

#### What to Watch For:

**✅ Success Indicators:**
- CV parsing completes without errors
- Score displays correctly
- No "500 Internal Server Error" messages
- Questions are generated

**⚠️ Potential Issues:**
- **Pydantic validation errors** - Means CV schema doesn't match Gemini output
- **Import errors** - Missing LangChain dependencies
- **Timeout errors** - Gemini API taking too long (check API key, quota)
- **JSON parsing errors** - Shouldn't happen with PydanticOutputParser, but check logs

### Step 6: Check Backend Logs for Errors

```bash
docker-compose logs backend | grep -i error
docker-compose logs backend | grep -i exception

# If errors found, check:
# 1. Pydantic validation errors - schema mismatch
# 2. Gemini API errors - quota, API key issues
# 3. Import errors - dependency issues
```

---

## Comparison: Old vs New Behavior

### Old cv_parser.py:
- Manual markdown stripping (20+ lines of string manipulation)
- Generic exception handling
- No retry logic
- Returns dict with fallback to default structure
- No type validation

### New cv_parser.py (LangChain):
- **Automatic** markdown stripping via PydanticOutputParser
- **Automatic retry** on rate limits (max_retries=3)
- **Type-safe validation** - Pydantic enforces schema
- Better error messages showing exactly what's wrong
- Same return format (dict) for backward compatibility

### Expected Improvements:
- **-50% rate limit failures** (automatic retry)
- **Better error messages** (Pydantic validation details)
- **No more markdown parsing bugs** (handled by LangChain)

---

## Debugging Common Issues

### Issue 1: ImportError for langchain modules

**Symptoms:**
```
ModuleNotFoundError: No module named 'langchain_google_genai'
```

**Solution:**
```bash
# Rebuild container
docker-compose up --build backend

# Or manually install in container
docker exec -it hirehub-backend pip install langchain-core langchain-google-genai
```

### Issue 2: Pydantic Validation Error

**Symptoms:**
```
ValidationError: 1 validation error for CVData
  personalInfo -> firstName
    field required (type=value_error.missing)
```

**Cause:** Gemini returned data that doesn't match CVData schema

**Solution:**
1. Check backend logs for the actual Gemini response
2. Verify schema in `backend/app/schemas/cv_schemas.py` matches expected format
3. Check if fields are marked `Optional` when they should be

### Issue 3: Gemini API Errors

**Symptoms:**
```
Error parsing CV with Gemini: 429 Resource exhausted
```

**Solutions:**
- **429 (Rate limit):** Wait a few minutes, or check quota at https://makersuite.google.com
- **401 (Invalid key):** Check `GEMINI_API_KEY` in `.env` file
- **503 (Service unavailable):** Temporary Gemini outage, retry later

### Issue 4: Different Output Format

**Symptoms:** Frontend expects certain fields but they're missing

**Solution:**
The refactored cv_parser returns `.dict()` which should be identical to the old format. However, if there are differences:

1. Check the fallback structure in cv_parser.py (lines 120-145)
2. Ensure all field names match exactly (camelCase vs snake_case)
3. Look for `personalInfo` vs `personal_info` mismatches

---

## Rollback Plan (If Needed)

If the refactored version causes issues:

```bash
# Restore old cv_parser
cp /Users/carlosid/Desktop/HireHub__AI/backend/app/services/cv_parser_old_backup.py \
   /Users/carlosid/Desktop/HireHub__AI/backend/app/services/cv_parser.py

# Rebuild container
docker-compose up --build -d backend

# You can also temporarily remove LangChain dependencies from requirements.txt
# But this isn't necessary - they won't hurt if not used
```

---

## Success Criteria

Before proceeding to refactor the remaining 7 services, we need:

✅ **Backend starts successfully** with no import errors
✅ **CV upload completes** without crashes
✅ **Parsing produces valid output** that matches CVData schema
✅ **Score calculation works** (uses the parsed CV data)
✅ **No regression** - everything that worked before still works
✅ **Better error handling** - retry logic works on transient failures

---

## Next Steps After Successful Test

Once cv_parser.py is validated:

1. **Refactor jd_analyzer.py** - Similar pattern to cv_parser
2. **Refactor scorer.py** - More complex (RAG + vector scoring)
3. **Refactor question_gen.py** - Medium complexity
4. **Refactor cv_optimizer.py** - Complex (RAG + PDF generation)
5. **Refactor cover_letter_gen.py** - Medium complexity
6. **Refactor learning_recommendations.py** - Medium complexity
7. **Refactor interview_prep.py** - Medium complexity

Each service will follow the same pattern:
- Create Pydantic schema (already done ✅)
- Create prompt template
- Use `ChatGoogleGenerativeAI` with retries
- Use `PydanticOutputParser` for validation
- Test individually before moving to next

---

## Questions to Answer During Testing

1. **Performance:** Is the new version slower/faster than the old one?
2. **Reliability:** Does retry logic actually help with transient failures?
3. **Accuracy:** Does Pydantic validation catch malformed responses?
4. **Compatibility:** Does the output format work seamlessly with existing frontend?

---

## Contact Points

If issues arise:
- Check backend logs: `docker-compose logs -f backend`
- Check Qdrant: `curl http://localhost:6335/collections`
- Check frontend console: Browser DevTools → Console
- Check network requests: Browser DevTools → Network tab

---

## Summary

**What Changed:**
- cv_parser.py now uses LangChain for improved reliability and type safety
- Old version backed up as cv_parser_old_backup.py
- Ready for testing with Docker rebuild

**What's Next:**
- Test thoroughly with real CV upload
- Validate no regressions
- If successful, continue with remaining 7 services
- If issues found, debug and fix before proceeding

**Expected Timeline:**
- Testing: 30-60 minutes
- Fix issues (if any): 1-2 hours
- Refactor remaining services: 2-3 days (after validation)

---

Good luck with testing! 🚀
