from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import asyncio
import json
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from app.database import get_db
from app.models import CVAnalysis
from app.config import get_settings
from app.services.cv_parser import extract_text_from_pdf, extract_text_from_docx, parse_cv_with_gemini, store_cv_embeddings
from app.services.jd_analyzer import analyze_jd_with_gemini, store_jd_embeddings
from app.services.scorer import calculate_compatibility_score
from app.services.question_gen import generate_smart_questions
from app.services.cv_optimizer import optimize_cv, generate_cv_pdf
from app.services.cover_letter_gen import generate_cover_letter, generate_cover_letter_pdf
from app.services.learning_recommender import generate_learning_recommendations
from app.services.interview_prep import generate_interview_prep
from app.services.qdrant_service import init_collections, store_cv_embedding, store_jd_embedding
from app.services.embeddings import get_embedding_model, generate_cv_jd_embeddings_batch
from app.services.cache_service import is_redis_available

# Create necessary directories
os.makedirs("/app/data", exist_ok=True)
os.makedirs("/app/uploads", exist_ok=True)
os.makedirs("/app/outputs", exist_ok=True)

# Configure Gemini API
settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

app = FastAPI(title="HireHubAI Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OPTIMIZATION: Gzip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Thread pool for parallel execution
executor = ThreadPoolExecutor(max_workers=4)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing HireHubAI Backend...")

    # Initialize Qdrant collections
    print("   📦 Setting up Qdrant collections...")
    init_collections()

    # Preload embedding model
    print("   🧠 Preloading embedding model...")
    try:
        get_embedding_model()
        print("   ✅ Embedding model loaded")
    except Exception as e:
        print(f"   ⚠️  Embedding model preload warning: {e}")

    # Check Redis connection
    print("   💾 Checking Redis cache...")
    if is_redis_available():
        print("   ✅ Redis cache connected")
    else:
        print("   ⚠️  Redis cache unavailable (caching disabled)")

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

@app.post("/api/parse-cv")
async def parse_cv_endpoint(cv_text: str = Form(...)):
    """Parse CV and return structured JSON - STANDALONE ENDPOINT"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Complete CV parsing prompt
        prompt = f"""Extract structured information from this CV/Resume:

{cv_text}

Return ONLY a valid JSON object (no markdown, no backticks) with this exact structure:
{{
    "personal_info": {{
        "name": "string or null",
        "email": "string or null",
        "phone": "string or null",
        "location": "string or null",
        "linkedin": "string or null",
        "github": "string or null",
        "portfolio": "string or null"
    }},
    "professional_summary": "string",
    "skills": {{
        "technical_skills": ["array of strings"],
        "tools": ["array of strings"],
        "soft_skills": ["array of strings"]
    }},
    "experience": [
        {{
            "company": "string",
            "role": "string",
            "duration": "string",
            "location": "string or null",
            "achievements": ["array of strings"]
        }}
    ],
    "education": [
        {{
            "degree": "string",
            "institution": "string",
            "year": "string",
            "gpa": "string or null"
        }}
    ],
    "projects": [
        {{
            "name": "string",
            "description": "string",
            "technologies": ["array of strings"],
            "link": "string or null"
        }}
    ],
    "certifications": ["array of strings"],
    "languages": ["array of strings"],
    "years_of_experience": 0
}}

Extract ALL information present in the CV. Be thorough and accurate."""

        generation_config = {
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response (remove markdown if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        cv_parsed = json.loads(response_text)

        return {
            "status": "success",
            "cv_parsed": cv_parsed
        }

    except Exception as e:
        print(f"Error in parse_cv_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "cv_parsed": {
                "personal_info": {},
                "professional_summary": "",
                "skills": {"technical_skills": [], "tools": [], "soft_skills": []},
                "experience": [],
                "education": [],
                "projects": [],
                "certifications": [],
                "languages": [],
                "years_of_experience": 0
            }
        }

@app.post("/api/parse-jd")
async def parse_jd_endpoint(jd_text: str = Form(...)):
    """Parse JD and return structured JSON - STANDALONE ENDPOINT"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Complete JD parsing prompt
        prompt = f"""Analyze this job description and extract requirements:

{jd_text}

Return ONLY a valid JSON object (no markdown, no backticks) with:
{{
    "company_name": "string or null",
    "position_title": "string or null",
    "location": "string or null",
    "work_mode": "remote/hybrid/onsite or null",
    "salary_range": "string or null",
    "experience_years_required": 0,
    "experience_level": "junior/mid/senior",
    "hard_skills_required": [
        {{
            "skill": "string",
            "priority": "critical/important/nice"
        }}
    ],
    "soft_skills_required": ["array of strings"],
    "responsibilities": ["array of key duties"],
    "tech_stack": ["array of technologies"],
    "domain_expertise": {{
        "industry": "string or null",
        "specific_knowledge": ["array"]
    }},
    "implicit_requirements": ["things not stated but implied"],
    "company_culture_signals": ["array"],
    "ats_keywords": ["array of important terms"]
}}

Be thorough and extract all information."""

        generation_config = {
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response (remove markdown if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        jd_parsed = json.loads(response_text)

        return {
            "status": "success",
            "jd_parsed": jd_parsed
        }

    except Exception as e:
        print(f"Error in parse_jd_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "jd_parsed": {
                "company_name": None,
                "position_title": None,
                "location": None,
                "work_mode": None,
                "salary_range": None,
                "experience_years_required": 0,
                "experience_level": "mid",
                "hard_skills_required": [],
                "soft_skills_required": [],
                "responsibilities": [],
                "tech_stack": [],
                "domain_expertise": {"industry": None, "specific_knowledge": []},
                "implicit_requirements": [],
                "company_culture_signals": [],
                "ats_keywords": []
            }
        }

@app.post("/api/calculate-score")
async def calculate_score_endpoint(
    cv_parsed: dict = Form(...),
    jd_parsed: dict = Form(...)
):
    """Calculate compatibility score - STANDALONE ENDPOINT"""
    try:
        # Parse JSON strings if needed
        if isinstance(cv_parsed, str):
            cv_parsed = json.loads(cv_parsed)
        if isinstance(jd_parsed, str):
            jd_parsed = json.loads(jd_parsed)

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Compress CV data - only send relevant fields
        cv_summary = {
            "name": cv_parsed.get('personal_info', {}).get('name', 'Unknown'),
            "years_experience": cv_parsed.get('years_of_experience', 0),
            "skills": cv_parsed.get('skills', {}),
            "experience": [
                {
                    "role": exp.get('role', ''),
                    "company": exp.get('company', ''),
                    "duration": exp.get('duration', ''),
                    "key_achievements": exp.get('achievements', [])[:3]
                }
                for exp in (cv_parsed.get('experience', [])[:3])
            ],
            "education": cv_parsed.get('education', []),
            "certifications": cv_parsed.get('certifications', [])
        }

        # Compress JD data - only send requirements
        jd_summary = {
            "position": jd_parsed.get('position_title', ''),
            "company": jd_parsed.get('company_name', ''),
            "hard_skills": [s.get('skill', '') for s in jd_parsed.get('hard_skills_required', [])],
            "soft_skills": jd_parsed.get('soft_skills_required', []),
            "experience_required": jd_parsed.get('experience_years_required', 0),
            "responsibilities": jd_parsed.get('responsibilities', [])[:5],
            "nice_to_have": jd_parsed.get('tech_stack', [])
        }

        # Complete scoring prompt
        prompt = f"""Analyze the match between this CV and Job Description:

CANDIDATE:
- Name: {cv_summary['name']}
- Experience: {cv_summary['years_experience']} years
- Skills: {json.dumps(cv_summary['skills'])}
- Recent Roles: {json.dumps(cv_summary['experience'])}
- Education: {json.dumps(cv_summary['education'])}

JOB REQUIREMENTS:
- Position: {jd_summary['position']} at {jd_summary['company']}
- Required Skills: {', '.join(jd_summary['hard_skills'])}
- Soft Skills: {', '.join(jd_summary['soft_skills'])}
- Experience Required: {jd_summary['experience_required']} years
- Responsibilities: {json.dumps(jd_summary['responsibilities'])}

Calculate a detailed compatibility score. Return ONLY valid JSON (no markdown):
{{
    "overall_score": 0,
    "breakdown": {{
        "hard_skills": {{
            "score": 0,
            "weight": 35,
            "matched": ["array of matched skills"],
            "missing": ["array of missing skills"]
        }},
        "soft_skills": {{
            "score": 0,
            "weight": 15,
            "matched": ["array"],
            "missing": ["array"]
        }},
        "experience": {{
            "score": 0,
            "weight": 20,
            "candidate_years": 0,
            "required_years": 0,
            "assessment": "string"
        }},
        "domain": {{
            "score": 0,
            "weight": 15,
            "assessment": "string"
        }},
        "portfolio": {{
            "score": 0,
            "weight": 10,
            "assessment": "string"
        }},
        "logistics": {{
            "score": 0,
            "weight": 5,
            "assessment": "string"
        }}
    }},
    "top_gaps": [
        {{
            "gap": "string",
            "priority": "critical/high/medium",
            "impact": "string (e.g., '+15% score if added')"
        }}
    ],
    "strengths": ["array of candidate strengths"],
    "recommendations": ["array of actionable recommendations"]
}}

Overall score should be 0-100. Be realistic and detailed."""

        generation_config = {
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        score_data = json.loads(response_text)

        return {
            "status": "success",
            "score_data": score_data
        }

    except Exception as e:
        print(f"Error in calculate_score_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "score_data": {"overall_score": 0}
        }

@app.post("/api/generate-questions")
async def generate_questions_endpoint(
    cv_parsed: dict = Form(...),
    jd_parsed: dict = Form(...),
    gaps: list = Form(...)
):
    """Generate smart questions - STANDALONE ENDPOINT"""
    try:
        # Parse JSON strings if needed
        if isinstance(cv_parsed, str):
            cv_parsed = json.loads(cv_parsed)
        if isinstance(jd_parsed, str):
            jd_parsed = json.loads(jd_parsed)
        if isinstance(gaps, str):
            gaps = json.loads(gaps)

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Compress data - only send what's needed for question generation
        candidate_summary = {
            "name": cv_parsed.get('personal_info', {}).get('name', 'Candidate'),
            "years_exp": cv_parsed.get('years_of_experience', 0),
            "skills": list(set(
                cv_parsed.get('skills', {}).get('technical_skills', []) +
                cv_parsed.get('skills', {}).get('soft_skills', [])
            ))[:15]
        }

        job_requirements = {
            "position": jd_parsed.get('position_title', ''),
            "required_skills": [s.get('skill', '') for s in jd_parsed.get('hard_skills_required', [])][:10]
        }

        # Complete questions prompt
        prompt = f"""Based on these gaps between the candidate and job:

CANDIDATE: {candidate_summary['name']} ({candidate_summary['years_exp']} years experience)
Skills: {', '.join(candidate_summary['skills'])}

JOB: {job_requirements['position']}
Required: {', '.join(job_requirements['required_skills'])}

IDENTIFIED GAPS:
{json.dumps(gaps, indent=2)}

Generate 5-8 smart questions to uncover hidden experience that could close these gaps.

For EACH question, also provide 3-4 suggested answer options that users can select from. These should:
- Be realistic and varied (from beginner to expert level)
- Cover different levels of experience (e.g., "Yes, extensively", "Some experience", "Learning/exploring", "Not yet")
- Be written in first person, ready to use
- Let users customize them further
- Contextually include negative/"not yet" options when appropriate

Return ONLY valid JSON array (no markdown):
[
    {{
        "question": "string - the actual question",
        "category": "technical/domain/experience/soft_skills",
        "priority": "critical/high/medium/low",
        "potential_impact": "string (e.g., '+10% score if yes')",
        "why_asking": "string - explain what gap this addresses",
        "suggested_answers": [
            "string - first person answer option 1",
            "string - first person answer option 2",
            "string - first person answer option 3",
            "string - optional 4th answer"
        ]
    }}
]

Make questions specific, actionable, and easy to answer. Suggested answers should be ready to use but editable."""

        generation_config = {
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        questions = json.loads(response_text)

        return {
            "status": "success",
            "questions": questions
        }

    except Exception as e:
        print(f"Error in generate_questions_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "questions": []
        }

@app.post("/api/optimize-cv")
async def optimize_cv_endpoint(
    cv_parsed: dict = Form(...),
    jd_parsed: dict = Form(...),
    answers: dict = Form(...)
):
    """Optimize CV for job - STANDALONE ENDPOINT"""
    try:
        # Parse JSON strings if needed
        if isinstance(cv_parsed, str):
            cv_parsed = json.loads(cv_parsed)
        if isinstance(jd_parsed, str):
            jd_parsed = json.loads(jd_parsed)
        if isinstance(answers, str):
            answers = json.loads(answers)

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Complete CV optimization prompt
        prompt = f"""Optimize this CV for the job description, incorporating user's answers:

ORIGINAL CV:
{json.dumps(cv_parsed, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_parsed, indent=2)}

USER'S ADDITIONAL INFORMATION (from questions):
{json.dumps(answers, indent=2)}

INSTRUCTIONS:
1. Rewrite professional summary to emphasize alignment with job
2. Reorder and reframe experience bullets to highlight relevant work
3. Add skills uncovered from user answers
4. Use keywords from job description naturally
5. Quantify achievements where possible
6. Use action verbs (architected, led, optimized, delivered)

CRITICAL RULES:
- DO NOT fabricate experience
- Only use information from CV + user answers
- Reframe truthfully, don't invent
- Keep professional tone
- Maintain same JSON structure as input

Return optimized CV in same JSON structure as the original CV."""

        generation_config = {
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        optimized_cv = json.loads(response_text)

        return {
            "status": "success",
            "optimized_cv": optimized_cv
        }

    except Exception as e:
        print(f"Error in optimize_cv_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "optimized_cv": cv_parsed
        }

@app.post("/api/generate-cover-letter")
async def generate_cover_letter_endpoint(
    cv_parsed: dict = Form(...),
    jd_parsed: dict = Form(...),
    optimized_cv: dict = Form(...),
    answers: dict = Form(...)
):
    """Generate cover letter - STANDALONE ENDPOINT"""
    try:
        # Parse JSON strings if needed
        if isinstance(cv_parsed, str):
            cv_parsed = json.loads(cv_parsed)
        if isinstance(jd_parsed, str):
            jd_parsed = json.loads(jd_parsed)
        if isinstance(optimized_cv, str):
            optimized_cv = json.loads(optimized_cv)
        if isinstance(answers, str):
            answers = json.loads(answers)

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Complete cover letter prompt
        prompt = f"""Write a compelling, professional cover letter for this job application:

OPTIMIZED CV:
{json.dumps(optimized_cv, indent=2)}

JOB DESCRIPTION:
{json.dumps(jd_parsed, indent=2)}

USER'S ADDITIONAL CONTEXT (from questions):
{json.dumps(answers, indent=2)}

INSTRUCTIONS:
1. Opening: Strong hook that shows enthusiasm and alignment with company mission
2. Body Paragraph 1: Highlight 2-3 most relevant experiences/achievements
3. Body Paragraph 2: Show understanding of company/role + why you're excited
4. Body Paragraph 3: Address any gaps proactively (if applicable)
5. Closing: Clear call-to-action and availability

CRITICAL RULES:
- Professional but warm tone
- Specific examples from CV
- Show genuine interest in company/role
- Address hiring manager (use "Dear Hiring Manager" if unknown)
- Keep to 3-4 paragraphs
- No generic templates - be specific and personal
- Use keywords from job description naturally

Return JSON with this structure:
{{
    "opening_paragraph": "string",
    "body_paragraph_1": "string",
    "body_paragraph_2": "string",
    "body_paragraph_3": "string or null",
    "closing_paragraph": "string",
    "signature": {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "location": "string"
    }}
}}"""

        generation_config = {
            "temperature": 0.5,
            "response_mime_type": "application/json"
        }

        # Call Gemini API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        cover_letter = json.loads(response_text)

        return {
            "status": "success",
            "cover_letter": cover_letter
        }

    except Exception as e:
        print(f"Error in generate_cover_letter_endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "cover_letter": {
                "opening_paragraph": "I am writing to express my interest in this position.",
                "body_paragraph_1": "Based on my experience, I believe I would be a strong fit.",
                "body_paragraph_2": "I am excited about this opportunity.",
                "closing_paragraph": "Thank you for considering my application.",
                "signature": cv_parsed.get('personal_info', {})
            }
        }

@app.post("/api/transcribe")
async def transcribe_audio_endpoint(
    audio_file: UploadFile = File(...),
    language: str = Form("en")
):
    """Transcribe audio to text using OpenAI Whisper API - STANDALONE ENDPOINT

    Supports: English (en), French (fr), German (de), Spanish (es), and 50+ other languages
    Cost: ~$0.006 per minute of audio
    """
    import tempfile
    import os
    from openai import OpenAI

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None)

        # Save uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1] or ".mp3") as temp_audio:
            content = await audio_file.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # Transcribe audio using OpenAI Whisper API
        print(f"🎤 Transcribing audio in language: {language}")
        with open(temp_audio_path, "rb") as audio:
            # Use whisper-1 model with language hint
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language=language if language and language != "auto" else None,
                response_format="json"
            )

        # Clean up temp file
        os.unlink(temp_audio_path)

        return {
            "status": "success",
            "text": transcription.text.strip(),
            "language": language,
            "detected_language": None  # Whisper API doesn't return detected language
        }

    except Exception as e:
        print(f"Error in transcribe_audio_endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "text": ""
        }

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
        elif file.filename.endswith('.txt'):
            # Support .txt files for testing
            with open(file_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
        else:
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files supported")

        # OPTIMIZATION: Parse CV and JD in parallel (saves ~5-6 seconds)
        print("⚡ Running CV parsing and JD analysis in parallel...")
        loop = asyncio.get_event_loop()

        cv_parse_future = loop.run_in_executor(executor, parse_cv_with_gemini, cv_text)
        jd_parse_future = loop.run_in_executor(executor, analyze_jd_with_gemini, jd_text)

        # Wait for both to complete
        cv_parsed, jd_parsed = await asyncio.gather(cv_parse_future, jd_parse_future)

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

        # OPTIMIZATION: Generate all embeddings in batch (saves ~1.7 seconds)
        print("⚡ Generating embeddings in batch...")
        embeddings_batch = generate_cv_jd_embeddings_batch(cv_parsed, jd_parsed)

        # Store CV embedding in Qdrant
        cv_embedding_id = store_cv_embedding(
            cv_id=analysis.id,
            text=embeddings_batch['cv_full']['text'],
            embedding=embeddings_batch['cv_full']['embedding'],
            metadata={
                "section": "full",
                "name": cv_parsed.get('personal_info', {}).get('name', 'Unknown'),
                "years_of_experience": cv_parsed.get('years_of_experience', 0)
            }
        )

        # Store JD embedding in Qdrant
        jd_embedding_id = store_jd_embedding(
            jd_id=analysis.id,
            text=embeddings_batch['jd_full']['text'],
            embedding=embeddings_batch['jd_full']['embedding'],
            metadata={
                "requirement_type": "full",
                "position": jd_parsed.get('position_title', 'Unknown'),
                "company": jd_parsed.get('company_name', 'Unknown')
            }
        )

        # Update with embedding IDs
        analysis.cv_embedding_id = cv_embedding_id
        analysis.jd_embedding_id = jd_embedding_id
        db.commit()

        # ============================================================
        # TEMPORARILY DISABLED FOR PERFORMANCE TESTING
        # Testing hypothesis: scoring is the main bottleneck (not questions)
        # ============================================================
        # # Calculate compatibility score with RAG (ASYNC)
        # print("⚡ Running compatibility scoring (async)...")
        # score_data = await calculate_compatibility_score(cv_parsed, jd_parsed, analysis.id)

        # SCORING DISABLED - set minimal values
        print("⚠️  TESTING MODE: Scoring disabled, questions enabled")
        analysis.compatibility_score = 0
        analysis.score_breakdown = {}
        analysis.gaps = []
        analysis.strengths = []

        # Generate smart questions with RAG (ASYNC) - ENABLED
        # Pass empty gaps since we don't have scoring data
        print("⚡ Running question generation (async)...")
        questions = await generate_smart_questions(cv_parsed, jd_parsed, [], analysis.id)

        # Update analysis with questions
        analysis.questions = questions
        analysis.answers = {}

        db.commit()

        return {
            "id": analysis.id,
            "score": 0,  # Disabled for testing
            "breakdown": {},
            "gaps": [],
            "strengths": [],
            "questions": questions  # ENABLED
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
            "optimized_cv": analysis.optimized_cv
        }

    except Exception as e:
        print(f"Error in get_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-cover-letter/{analysis_id}")
async def generate_cover_letter_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Phase 7: Generate cover letter"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.optimized_cv:
            raise HTTPException(status_code=400, detail="CV not optimized yet. Please answer questions first.")

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

@app.get("/api/download-cover-letter/{analysis_id}")
async def download_cover_letter(
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

        generate_cover_letter_pdf(
            analysis.cover_letter,
            analysis.cv_parsed,
            analysis.jd_parsed,
            output_path
        )

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:
        print(f"Error in download_cover_letter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-recommendations/{analysis_id}")
async def get_learning_recommendations(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Phase 8: Get personalized learning path"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Generate if not already cached
        if not analysis.learning_recommendations:
            learning_path = generate_learning_recommendations(
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
            analysis.learning_recommendations = learning_path
            db.commit()
        else:
            learning_path = analysis.learning_recommendations

        return {
            "id": analysis_id,
            "learning_recommendations": learning_path
        }

    except Exception as e:
        print(f"Error in get_learning_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview-prep/{analysis_id}")
async def get_interview_prep(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Phase 9: Get interview preparation guide"""

    try:
        analysis = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not analysis.optimized_cv:
            raise HTTPException(status_code=400, detail="CV not optimized yet. Please answer questions first.")

        # Generate if not already cached
        if not analysis.interview_prep:
            interview_guide = generate_interview_prep(
                analysis.cv_parsed,
                analysis.jd_parsed,
                analysis.optimized_cv,
                analysis.answers or {},
                analysis.id
            )

            # Save to database
            analysis.interview_prep = interview_guide
            db.commit()
        else:
            interview_guide = analysis.interview_prep

        return {
            "id": analysis_id,
            "interview_prep": interview_guide
        }

    except Exception as e:
        print(f"Error in get_interview_prep: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/parse-cv")
async def test_cv_parsing():
    """Test CV parsing performance in isolation"""
    import time

    try:
        # Read test CV
        test_cv_path = "/app/../backend/test/resume.txt"
        with open(test_cv_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()

        # Time the parsing
        start = time.time()
        cv_parsed = parse_cv_with_gemini(cv_text)
        elapsed = time.time() - start

        return {
            "status": "success",
            "elapsed_ms": round(elapsed * 1000, 2),
            "elapsed_s": round(elapsed, 2),
            "cv_text_length": len(cv_text),
            "cv_parsed_keys": list(cv_parsed.keys()) if cv_parsed else []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/test/parse-jd")
async def test_jd_parsing():
    """Test JD parsing performance in isolation"""
    import time

    try:
        # Read test JD
        test_jd_path = "/app/../backend/test/job_description.txt"
        with open(test_jd_path, 'r', encoding='utf-8') as f:
            jd_text = f.read()

        # Time the parsing
        start = time.time()
        jd_parsed = analyze_jd_with_gemini(jd_text)
        elapsed = time.time() - start

        return {
            "status": "success",
            "elapsed_ms": round(elapsed * 1000, 2),
            "elapsed_s": round(elapsed, 2),
            "jd_text_length": len(jd_text),
            "jd_parsed_keys": list(jd_parsed.keys()) if jd_parsed else []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
