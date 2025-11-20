# Quick Start - Testing LangChain Integration

## 🚀 Quick Commands

```bash
# 1. Navigate to project
cd /Users/carlosid/Desktop/HireHub__AI

# 2. Rebuild backend with new dependencies
docker-compose down
docker-compose up --build -d

# 3. Watch logs for startup
docker-compose logs -f backend
# Wait for: "✅ HireHubAI Backend Ready!"
# Press Ctrl+C to exit logs

# 4. Test backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# 5. Start frontend (in new terminal)
cd frontend
npm run dev
# Opens on http://localhost:3000

# 6. Test with CV upload
# - Go to http://localhost:3000
# - Upload a CV (PDF/DOCX)
# - Paste a job description
# - Click "Analyze & Optimize"
# - Wait 15-30 seconds
# - Check if score displays correctly
```

---

## ✅ Success Checklist

- [ ] Docker backend starts without errors
- [ ] No "ModuleNotFoundError" for langchain
- [ ] curl health check returns {"status":"healthy"}
- [ ] Frontend starts on port 3000
- [ ] CV upload completes without 500 error
- [ ] Compatibility score displays (0-100%)
- [ ] Score breakdown shows
- [ ] Questions are generated

---

## ⚠️ If Something Breaks

### Error: "ModuleNotFoundError: No module named 'langchain_google_genai'"

**Fix:**
```bash
docker-compose up --build backend  # Force rebuild
```

### Error: "Pydantic ValidationError"

**Fix:** Check logs for details
```bash
docker-compose logs backend | tail -50
```

Schema might need adjustment in `backend/app/schemas/cv_schemas.py`

### Error: "Gemini API error: 429"

**Fix:** Rate limit hit
- Wait 2-3 minutes
- Check quota at https://makersuite.google.com
- Verify GEMINI_API_KEY in `.env`

### Want to Rollback?

```bash
# Restore old cv_parser
cp backend/app/services/cv_parser_old_backup.py \
   backend/app/services/cv_parser.py

# Rebuild
docker-compose up --build -d backend
```

---

## 📊 What Changed?

**Old cv_parser.py:**
- Manual JSON parsing
- No retry logic
- Fragile markdown stripping

**New cv_parser.py:**
- Automatic validation (Pydantic)
- 3 automatic retries
- Type-safe output

**Same output format** - backward compatible!

---

## 📝 Next Steps After Testing

✅ **If test passes:** I'll refactor the remaining 7 services

❌ **If test fails:** I'll debug and fix issues before continuing

---

## 📞 Report Back

Tell me:
1. ✅ or ❌ - Did backend start successfully?
2. ✅ or ❌ - Did CV upload work?
3. ✅ or ❌ - Did score display correctly?
4. Any error messages you saw?

Then we'll proceed accordingly! 🚀
