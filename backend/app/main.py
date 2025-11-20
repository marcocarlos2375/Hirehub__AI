from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from app.database import get_db
from app.models import CVAnalysis
from app.services.cv_parser import extract_text_from_pdf, extract_text_from_docx, parse_cv_with_gemini, store_cv_embeddings
from app.services.jd_analyzer import analyze_jd_with_gemini, store_jd_embeddings
from app.services.scorer import calculate_compatibility_score
from app.services.question_gen import generate_smart_questions
from app.services.cv_optimizer import optimize_cv, generate_cv_pdf
from app.services.cover_letter_gen import generate_cover_letter, generate_cover_letter_pdf
from app.services.learning_recommendations import generate_learning_path
from app.services.interview_prep import generate_interview_prep
from app.services.qdrant_service import init_collections

# Create necessary directories
os.makedirs("/app/data", exist_ok=True)
os.makedirs("/app/uploads", exist_ok=True)
os.makedirs("/app/outputs", exist_ok=True)

app = FastAPI(title="HireHubAI Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Qdrant collections on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing Qdrant collections...")
    init_collections()
    print("✅ HireHubAI Backend Ready!")

@app.get("/")
def root():
    return {
        "message": "HireHubAI API is running",
        "version": "1.0.0",
        "services": ["Gemini 2.0 Flash-Lite", "Qdrant Vector DB"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Step 1: Upload CV and JD, get analysis with RAG"""

    try:
        # Save uploaded file
        file_path = f"/app/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from CV
        if file.filename.endswith('.pdf'):
            cv_text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            cv_text = extract_text_from_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files supported")

        # Delete the uploaded file after extraction (we only need the text)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete uploaded file: {e}")

        # Parse CV with Gemini
        cv_parsed = parse_cv_with_gemini(cv_text)

        # Analyze JD with Gemini
        jd_parsed = analyze_jd_with_gemini(jd_text)

        # Create database entry first
        analysis = CVAnalysis(
            cv_filename=file.filename,
            cv_text=cv_text,
            cv_parsed=cv_parsed,
            jd_text=jd_text,
            jd_parsed=jd_parsed
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Store embeddings in Qdrant
        cv_embedding_id = store_cv_embeddings(analysis.id, cv_parsed)
        jd_embedding_id = store_jd_embeddings(analysis.id, jd_parsed)

        # Update with embedding IDs
        analysis.cv_embedding_id = cv_embedding_id
        analysis.jd_embedding_id = jd_embedding_id
        db.commit()

        # Calculate compatibility score with RAG
        score_data = calculate_compatibility_score(cv_parsed, jd_parsed, analysis.id)

        # Generate smart questions with RAG
        top_gaps = score_data.get('top_gaps', [])
        questions = generate_smart_questions(cv_parsed, jd_parsed, top_gaps, analysis.id)

        # Update analysis with results
        analysis.compatibility_score = score_data.get('overall_score')
        analysis.score_breakdown = score_data.get('breakdown')
        analysis.gaps = top_gaps
        analysis.strengths = score_data.get('strengths', [])
        analysis.questions = questions
        analysis.answers = {}

        db.commit()

        return {
            "id": analysis.id,
            "score": score_data.get('overall_score'),
            "breakdown": score_data.get('breakdown'),
            "gaps": top_gaps,
            "strengths": score_data.get('strengths'),
            "questions": questions
        }

    except Exception as e:
        print(f"Error in upload_cv: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-answers/{analysis_id}")
async def submit_answers(
    analysis_id: str,
    answers: dict,
    db: Session = Depends(get_db)
):
    """Step 2: Submit answers and optimize CV with RAG"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Save answers
        analysis.answers = answers

        # Generate optimized CV with RAG
        optimized = optimize_cv(
            analysis.cv_parsed,
            analysis.jd_parsed,
            answers,
            analysis.id
        )
        analysis.optimized_cv = optimized

        db.commit()

        return {
            "id": analysis_id,
            "message": "Answers saved and CV optimized",
            "optimized_cv": optimized
        }

    except Exception as e:
        print(f"Error in submit_answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-cv/{analysis_id}")
async def download_cv(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Step 3: Download optimized CV as PDF"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.optimized_cv:
            raise HTTPException(status_code=400, detail="CV not optimized yet")

        # Generate PDF
        output_filename = f"optimized_cv_{analysis_id}.pdf"
        output_path = f"/app/outputs/{output_filename}"

        generate_cv_pdf(analysis.optimized_cv, output_path)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:
        print(f"Error in download_cv: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get full analysis data"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return {
            "id": analysis.id,
            "cv_parsed": analysis.cv_parsed,
            "jd_parsed": analysis.jd_parsed,
            "score": analysis.compatibility_score,
            "breakdown": analysis.score_breakdown,
            "gaps": analysis.gaps,
            "strengths": analysis.strengths,
            "questions": analysis.questions,
            "answers": analysis.answers,
            "optimized_cv": analysis.optimized_cv,
            "cover_letter": analysis.cover_letter,
            "learning_path": analysis.learning_path,
            "interview_prep": analysis.interview_prep
        }

    except Exception as e:
        print(f"Error in get_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-cover-letter/{analysis_id}")
async def generate_cover_letter_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Generate personalized cover letter"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.optimized_cv:
            raise HTTPException(status_code=400, detail="CV not optimized yet. Please complete the optimization step first.")

        # Generate cover letter
        cover_letter = generate_cover_letter(
            analysis.cv_parsed,
            analysis.jd_parsed,
            analysis.answers or {},
            analysis.optimized_cv,
            analysis.id
        )

        # Save to database
        analysis.cover_letter = cover_letter
        db.commit()

        return {
            "id": analysis_id,
            "message": "Cover letter generated successfully",
            "cover_letter": cover_letter
        }

    except Exception as e:
        print(f"Error in generate_cover_letter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cover-letter/{analysis_id}")
async def get_cover_letter(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get cover letter for an analysis"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not generated yet")

        return {
            "id": analysis_id,
            "cover_letter": analysis.cover_letter
        }

    except Exception as e:
        print(f"Error in get_cover_letter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-cover-letter/{analysis_id}")
async def download_cover_letter_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Download cover letter as PDF"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.cover_letter:
            raise HTTPException(status_code=400, detail="Cover letter not generated yet")

        # Generate PDF
        output_filename = f"cover_letter_{analysis_id}.pdf"
        output_path = f"/app/outputs/{output_filename}"

        generate_cover_letter_pdf(analysis.cover_letter, output_path)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:
        print(f"Error in download_cover_letter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-learning-path/{analysis_id}")
async def generate_learning_path_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Generate personalized learning roadmap"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Generate learning path
        learning_path_data = generate_learning_path(
            analysis.cv_parsed,
            analysis.jd_parsed,
            analysis.gaps or [],
            {
                "overall_score": analysis.compatibility_score,
                "breakdown": analysis.score_breakdown
            },
            analysis.id
        )

        # Save to database
        analysis.learning_path = learning_path_data
        db.commit()

        return {
            "id": analysis_id,
            "message": "Learning path generated successfully",
            "learning_path": learning_path_data
        }

    except Exception as e:
        print(f"Error in generate_learning_path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-path/{analysis_id}")
async def get_learning_path(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get learning path for an analysis"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.learning_path:
            raise HTTPException(status_code=404, detail="Learning path not generated yet")

        return {
            "id": analysis_id,
            "learning_path": analysis.learning_path
        }

    except Exception as e:
        print(f"Error in get_learning_path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-interview-prep/{analysis_id}")
async def generate_interview_prep_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Generate interview preparation materials"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Generate interview prep
        interview_prep_data = generate_interview_prep(
            analysis.cv_parsed,
            analysis.jd_parsed,
            analysis.answers or {},
            analysis.gaps or [],
            analysis.id
        )

        # Save to database
        analysis.interview_prep = interview_prep_data
        db.commit()

        return {
            "id": analysis_id,
            "message": "Interview prep generated successfully",
            "interview_prep": interview_prep_data
        }

    except Exception as e:
        print(f"Error in generate_interview_prep: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview-prep/{analysis_id}")
async def get_interview_prep(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get interview prep for an analysis"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.interview_prep:
            raise HTTPException(status_code=404, detail="Interview prep not generated yet")

        return {
            "id": analysis_id,
            "interview_prep": analysis.interview_prep
        }

    except Exception as e:
        print(f"Error in get_interview_prep: {e}")
        raise HTTPException(status_code=500, detail=str(e))
