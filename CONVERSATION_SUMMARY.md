# HireHub AI - Conversation Summary

## Date: November 20, 2025

## What We Implemented

### 1. Multiple-Choice Answer Suggestions
**Problem**: Single suggested answer wasn't flexible enough
**Solution**: Created radio button UI with 3-4 answer options per question

**Files Modified**:
- `backend/app/services/question_gen.py` - Changed to `suggested_answers` array
- `frontend/pages/questions/[id].vue` - Radio button UI with custom answer option

### 2. Vector-Based Scoring System
**Problem**: AI scoring inconsistent (45% → 68% with same inputs)
**Solution**: Replaced AI scoring with semantic vector similarity (deterministic)

**Files Created**:
- `backend/app/services/vector_scorer.py` - Cosine similarity scoring

**Files Modified**:
- `backend/app/services/scorer.py` - Now uses vectors for scores, AI only for insights
- `backend/requirements.txt` - Added `scikit-learn==1.3.2`

### 3. Docker Development Setup
**Files Modified**:
- `docker-compose.yml` - Added source code volume mount: `- ./backend/app:/app/app`

## How to Resume After Restart

```bash
# 1. Restart Docker (should fix storage error)
docker-compose down
docker-compose up --build -d

# 2. Start frontend
cd frontend && npm run dev
```

## Key Features Added

1. **Multiple-Choice Answers**: Users can select from 3-4 pre-written options or write custom answer
2. **Deterministic Scoring**: Same CV + JD = same score every time (using cosine similarity)
3. **Live Code Reload**: Source code changes sync to container without rebuild

## Technical Details

### Vector Scoring Logic
- Uses sentence-transformers embeddings
- Calculates cosine similarity between CV and JD elements
- Weighted formula: hard_skills (35%) + experience (20%) + domain (15%) + soft_skills (15%) + responsibilities (10%) + logistics (5%)
- Threshold: 70%+ = match, 50-70% = partial, <50% = missing

### Answer Suggestions Format
```json
{
  "suggested_answers": [
    "Strong experience option",
    "Moderate experience option", 
    "Learning/basic level option",
    "Alternative perspective option"
  ]
}
```

## Status
- ✅ All code changes saved locally
- ⏳ Docker container rebuild pending (storage error - needs restart)
- ✅ Frontend running successfully
