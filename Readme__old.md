I want you to build a complete AI-powered CV optimization platform called "HireHubAI Basic" using Python FastAPI backend (Dockerized with Qdrant) and Nuxt.js 3 frontend. This is a SIMPLE MVP with no authentication, no email, and no payments.

═══════════════════════════════════════════════════════════
🎯 PROJECT OVERVIEW
═══════════════════════════════════════════════════════════

The system does this:
1. User uploads CV (PDF/DOCX) + pastes job description
2. AI parses CV and analyzes JD using Google Gemini 2.0 Flash-Lite
3. System stores embeddings in Qdrant for semantic search
4. System calculates compatibility score (0-100%) using RAG
5. System generates 5-8 smart questions to uncover hidden experience
6. User answers questions
7. System generates optimized CV tailored to the job using RAG context
8. User downloads optimized CV as PDF

═══════════════════════════════════════════════════════════
🛠️ TECH STACK
═══════════════════════════════════════════════════════════

Backend (Dockerized):
- FastAPI (Python 3.11+)
- SQLite (file-based database, mounted volume)
- Google Gemini 2.0 Flash-Lite API
- Qdrant Vector Database (in Docker Compose)
- PyMuPDF (for PDF parsing)
- python-docx (for DOCX parsing)
- ReportLab (for PDF generation)
- sentence-transformers (for embeddings)
- qdrant-client (Python SDK)

Frontend:
- Nuxt 3 (Vue.js framework)
- TypeScript
- Tailwind CSS
- Geist Font (Google Fonts or local)
- ofetch/useFetch for API calls
- Pinia (state management)

Infrastructure:
- Docker + Docker Compose
- Backend service (FastAPI)
- Qdrant service (vector database)
- Shared network between services

═══════════════════════════════════════════════════════════
📁 PROJECT STRUCTURE
═══════════════════════════════════════════════════════════

Create this exact structure:

hirehub-basic/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app with all routes
│   │   ├── models.py            # SQLAlchemy models (SQLite)
│   │   ├── database.py          # Database connection
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── cv_parser.py        # PDF/DOCX → text → structured JSON
│   │   │   ├── jd_analyzer.py      # Extract requirements from JD
│   │   │   ├── embeddings.py       # Generate embeddings
│   │   │   ├── qdrant_service.py   # Qdrant CRUD operations
│   │   │   ├── scorer.py           # Calculate compatibility with RAG
│   │   │   ├── question_gen.py     # Generate smart questions with RAG
│   │   │   └── cv_optimizer.py     # Optimize CV + generate PDF
│   │   └── config.py            # Configuration
│   ├── data/                    # SQLite database file (volume mount)
│   ├── uploads/                 # Uploaded CVs (volume mount)
│   ├── outputs/                 # Generated PDFs (volume mount)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app.vue
│   ├── pages/
│   │   ├── index.vue            # Home page (upload CV + JD)
│   │   ├── analysis/
│   │   │   └── [id].vue         # Analysis results page
│   │   └── questions/
│   │       └── [id].vue         # Questions page
│   ├── components/
│   │   ├── CVUpload.vue
│   │   ├── JDInput.vue
│   │   ├── ScoreDisplay.vue
│   │   ├── ScoreBreakdown.vue
│   │   ├── GapsList.vue
│   │   ├── StrengthsList.vue
│   │   └── QuestionCard.vue
│   ├── composables/
│   │   └── useApi.ts            # API client composable
│   ├── layouts/
│   │   └── default.vue
│   ├── public/
│   │   └── fonts/               # Geist font files (if local)
│   ├── assets/
│   │   └── css/
│   │       └── main.css         # Tailwind imports
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── docker-compose.yml           # Orchestrates backend + Qdrant
├── .env.example
└── README.md

═══════════════════════════════════════════════════════════
🐳 DOCKER SETUP - COMPLETE CONFIGURATION
═══════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
FILE: docker-compose.yml
────────────────────────────────────────────────────────────

version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: hirehub-backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - DATABASE_URL=sqlite:////app/data/hirehub.db
    volumes:
      - ./backend/data:/app/data          # SQLite database
      - ./backend/uploads:/app/uploads    # Uploaded files
      - ./backend/outputs:/app/outputs    # Generated PDFs
    depends_on:
      - qdrant
    networks:
      - hirehub-network
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: hirehub-qdrant
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC API (optional)
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    networks:
      - hirehub-network
    restart: unless-stopped

networks:
  hirehub-network:
    driver: bridge

volumes:
  qdrant_storage:
    driver: local

────────────────────────────────────────────────────────────
FILE: backend/Dockerfile
────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create necessary directories
RUN mkdir -p /app/data /app/uploads /app/outputs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

────────────────────────────────────────────────────────────
FILE: .env.example
────────────────────────────────────────────────────────────

GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_HOST=qdrant
QDRANT_PORT=6333
DATABASE_URL=sqlite:////app/data/hirehub.db

═══════════════════════════════════════════════════════════
📝 BACKEND CODE - COMPLETE IMPLEMENTATION
═══════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
FILE: backend/requirements.txt
────────────────────────────────────────────────────────────

fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
google-generativeai==0.3.2
pymupdf==1.23.26
python-docx==1.1.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
python-dotenv==1.0.0
reportlab==4.0.9
qdrant-client==1.7.3
sentence-transformers==2.3.1
numpy==1.26.3

────────────────────────────────────────────────────────────
FILE: backend/app/config.py
────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    DATABASE_URL: str = "sqlite:////app/data/hirehub.db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

────────────────────────────────────────────────────────────
FILE: backend/app/database.py
────────────────────────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

────────────────────────────────────────────────────────────
FILE: backend/app/models.py
────────────────────────────────────────────────────────────

from sqlalchemy import Column, String, Float, JSON, DateTime, Text
from datetime import datetime
import uuid
from app.database import Base, engine

class CVAnalysis(Base):
    __tablename__ = "cv_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cv_filename = Column(String)
    cv_text = Column(Text)
    cv_parsed = Column(JSON)
    cv_embedding_id = Column(String, nullable=True)  # Qdrant point ID
    jd_text = Column(Text)
    jd_parsed = Column(JSON)
    jd_embedding_id = Column(String, nullable=True)  # Qdrant point ID
    compatibility_score = Column(Float)
    score_breakdown = Column(JSON)
    gaps = Column(JSON)
    strengths = Column(JSON)
    questions = Column(JSON)
    answers = Column(JSON)
    optimized_cv = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

────────────────────────────────────────────────────────────
FILE: backend/app/services/__init__.py
────────────────────────────────────────────────────────────

# Empty file to make this a package

────────────────────────────────────────────────────────────
FILE: backend/app/services/embeddings.py
────────────────────────────────────────────────────────────

from sentence_transformers import SentenceTransformer
from app.config import get_settings
import numpy as np
from typing import List, Union

settings = get_settings()

# Load embedding model (cached globally)
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text"""
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return embeddings.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))

────────────────────────────────────────────────────────────
FILE: backend/app/services/qdrant_service.py
────────────────────────────────────────────────────────────

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings
import uuid
from typing import List, Dict, Optional

settings = get_settings()

# Initialize Qdrant client (cached globally)
_client = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
    return _client

# Collection names
CV_COLLECTION = "cv_embeddings"
JD_COLLECTION = "jd_embeddings"
SKILLS_COLLECTION = "skills_embeddings"

def init_collections():
    """Initialize Qdrant collections if they don't exist"""
    client = get_qdrant_client()
    
    collections = [CV_COLLECTION, JD_COLLECTION, SKILLS_COLLECTION]
    
    for collection_name in collections:
        try:
            client.get_collection(collection_name)
            print(f"✓ Collection '{collection_name}' already exists")
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"✓ Created collection '{collection_name}'")

def store_cv_embedding(
    cv_id: str,
    text: str,
    embedding: List[float],
    metadata: Dict
) -> str:
    """Store CV embedding in Qdrant"""
    client = get_qdrant_client()
    
    point_id = str(uuid.uuid4())
    
    client.upsert(
        collection_name=CV_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "cv_id": cv_id,
                    "text": text,
                    "section": metadata.get("section", "full"),
                    **metadata
                }
            )
        ]
    )
    
    return point_id

def store_jd_embedding(
    jd_id: str,
    text: str,
    embedding: List[float],
    metadata: Dict
) -> str:
    """Store JD embedding in Qdrant"""
    client = get_qdrant_client()
    
    point_id = str(uuid.uuid4())
    
    client.upsert(
        collection_name=JD_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "jd_id": jd_id,
                    "text": text,
                    "requirement_type": metadata.get("requirement_type", "general"),
                    **metadata
                }
            )
        ]
    )
    
    return point_id

def search_similar_cvs(
    query_embedding: List[float],
    limit: int = 5,
    filters: Optional[Dict] = None
) -> List[Dict]:
    """Search for similar CVs"""
    client = get_qdrant_client()
    
    search_result = client.search(
        collection_name=CV_COLLECTION,
        query_vector=query_embedding,
        limit=limit
    )
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in search_result
    ]

def search_similar_jds(
    query_embedding: List[float],
    limit: int = 5
) -> List[Dict]:
    """Search for similar job descriptions"""
    client = get_qdrant_client()
    
    search_result = client.search(
        collection_name=JD_COLLECTION,
        query_vector=query_embedding,
        limit=limit
    )
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in search_result
    ]

def get_rag_context_for_cv(cv_id: str, query_text: str, query_embedding: List[float]) -> str:
    """Get relevant context from similar CVs for RAG"""
    similar = search_similar_cvs(query_embedding, limit=3)
    
    context_parts = []
    for item in similar:
        if item["score"] > 0.7:  # Relevance threshold
            context_parts.append(f"Similar CV experience: {item['payload'].get('text', '')[:200]}")
    
    return "\n\n".join(context_parts) if context_parts else ""

def get_rag_context_for_jd(jd_id: str, query_embedding: List[float]) -> str:
    """Get relevant context from similar JDs for RAG"""
    similar = search_similar_jds(query_embedding, limit=3)
    
    context_parts = []
    for item in similar:
        if item["score"] > 0.7:
            context_parts.append(f"Similar JD requirement: {item['payload'].get('text', '')[:200]}")
    
    return "\n\n".join(context_parts) if context_parts else ""

────────────────────────────────────────────────────────────
FILE: backend/app/services/cv_parser.py
────────────────────────────────────────────────────────────

import fitz  # PyMuPDF
from docx import Document
import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding, generate_embeddings_batch
from app.services.qdrant_service import store_cv_embedding

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX"""
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def parse_cv_with_gemini(cv_text: str) -> dict:
    """Use Gemini to structure CV data"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
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

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        return parsed_data
        
    except Exception as e:
        print(f"Error parsing CV with Gemini: {e}")
        return {
            "error": str(e),
            "personal_info": {},
            "professional_summary": cv_text[:500],
            "skills": {"technical_skills": [], "tools": [], "soft_skills": []},
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "years_of_experience": 0
        }

def store_cv_embeddings(cv_id: str, cv_parsed: dict) -> str:
    """Generate and store embeddings for different CV sections in Qdrant"""
    
    # Combine all text for full CV embedding
    full_text = f"""
    Summary: {cv_parsed.get('professional_summary', '')}
    Skills: {', '.join(cv_parsed.get('skills', {}).get('technical_skills', []))}
    Experience: {' '.join([f"{exp.get('role', '')} at {exp.get('company', '')}" for exp in cv_parsed.get('experience', [])])}
    """
    
    # Generate embedding for full CV
    full_embedding = generate_embedding(full_text)
    
    # Store in Qdrant
    point_id = store_cv_embedding(
        cv_id=cv_id,
        text=full_text,
        embedding=full_embedding,
        metadata={
            "section": "full",
            "name": cv_parsed.get('personal_info', {}).get('name', 'Unknown'),
            "years_of_experience": cv_parsed.get('years_of_experience', 0)
        }
    )
    
    return point_id

────────────────────────────────────────────────────────────
FILE: backend/app/services/jd_analyzer.py
────────────────────────────────────────────────────────────

import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import store_jd_embedding

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_jd_with_gemini(jd_text: str) -> dict:
    """Extract requirements from job description"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
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

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        return parsed_data
        
    except Exception as e:
        print(f"Error analyzing JD with Gemini: {e}")
        return {"error": str(e)}

def store_jd_embeddings(jd_id: str, jd_parsed: dict) -> str:
    """Generate and store embeddings for JD in Qdrant"""
    
    # Combine requirements into text
    full_text = f"""
    Position: {jd_parsed.get('position_title', '')}
    Requirements: {', '.join([skill['skill'] for skill in jd_parsed.get('hard_skills_required', [])])}
    Responsibilities: {' '.join(jd_parsed.get('responsibilities', []))}
    """
    
    # Generate embedding
    embedding = generate_embedding(full_text)
    
    # Store in Qdrant
    point_id = store_jd_embedding(
        jd_id=jd_id,
        text=full_text,
        embedding=embedding,
        metadata={
            "requirement_type": "full",
            "position": jd_parsed.get('position_title', 'Unknown'),
            "company": jd_parsed.get('company_name', 'Unknown')
        }
    )
    
    return point_id

────────────────────────────────────────────────────────────
FILE: backend/app/services/scorer.py
────────────────────────────────────────────────────────────

import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def calculate_compatibility_score(cv_data: dict, jd_data: dict, cv_id: str = None) -> dict:
    """Calculate detailed compatibility score using AI with RAG context"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Generate query embedding for RAG
    query_text = f"Skills needed: {', '.join([s['skill'] for s in jd_data.get('hard_skills_required', [])])}"
    query_embedding = generate_embedding(query_text)
    
    # Get RAG context from similar CVs/JDs
    rag_context = ""
    if cv_id:
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)
    
    prompt = f"""Analyze the match between this CV and Job Description:

CV DATA:
{json.dumps(cv_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

{f"ADDITIONAL CONTEXT FROM SIMILAR CASES:\n{rag_context}" if rag_context else ""}

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

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        score_data = json.loads(response_text)
        return score_data
        
    except Exception as e:
        print(f"Error calculating score with Gemini: {e}")
        return {"error": str(e), "overall_score": 0}

────────────────────────────────────────────────────────────
FILE: backend/app/services/question_gen.py
────────────────────────────────────────────────────────────

import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_smart_questions(cv_data: dict, jd_data: dict, gaps: list, cv_id: str = None) -> list:
    """Generate smart questions to uncover hidden experience using RAG"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Get RAG context
    rag_context = ""
    if cv_id:
        query_text = f"Questions about: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)
    
    prompt = f"""Based on these gaps between the CV and job requirements:

CV SUMMARY:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

TOP GAPS:
{json.dumps(gaps, indent=2)}

{f"SIMILAR QUESTIONS FROM PAST CASES:\n{rag_context}" if rag_context else ""}

Generate 5-8 smart questions to uncover hidden experience that could close these gaps.

Return ONLY valid JSON array (no markdown):
[
    {{
        "question": "string - the actual question",
        "category": "technical/domain/experience/soft_skills",
        "priority": "critical/high/medium/low",
        "potential_impact": "string (e.g., '+10% score if yes')",
        "why_asking": "string - explain what gap this addresses"
    }}
]

Make questions specific, actionable, and easy to answer with yes/no + details."""

    generation_config = {
        "temperature": 0.4,
        "response_mime_type": "application/json"
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        questions = json.loads(response_text)
        return questions
        
    except Exception as e:
        print(f"Error generating questions with Gemini: {e}")
        return []

────────────────────────────────────────────────────────────
FILE: backend/app/services/cv_optimizer.py
────────────────────────────────────────────────────────────

import os
import google.generativeai as genai
import json
from app.config import get_settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def optimize_cv(cv_data: dict, jd_data: dict, answers: dict, cv_id: str = None) -> dict:
    """Generate optimized CV using AI with RAG context"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Get RAG context from similar successful CVs
    rag_context = ""
    if cv_id:
        query_text = f"Optimize CV for {jd_data.get('position_title', 'position')}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)
    
    prompt = f"""Optimize this CV for the job description, incorporating user's answers:

ORIGINAL CV:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

USER'S ADDITIONAL INFORMATION (from questions):
{json.dumps(answers, indent=2)}

{f"BEST PRACTICES FROM SIMILAR SUCCESSFUL CVS:\n{rag_context}" if rag_context else ""}

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

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        optimized = json.loads(response_text)
        return optimized
        
    except Exception as e:
        print(f"Error optimizing CV with Gemini: {e}")
        return cv_data

def generate_cv_pdf(cv_data: dict, output_path: str) -> str:
    """Generate PDF from CV data using ReportLab"""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2563eb',
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Name
    name = cv_data.get('personal_info', {}).get('name', 'Your Name')
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Contact info
    contact_parts = []
    pi = cv_data.get('personal_info', {})
    if pi.get('email'):
        contact_parts.append(pi['email'])
    if pi.get('phone'):
        contact_parts.append(pi['phone'])
    if pi.get('location'):
        contact_parts.append(pi['location'])
    
    if contact_parts:
        contact_text = ' | '.join(contact_parts)
        story.append(Paragraph(contact_text, styles['Normal']))
    
    # Links
    link_parts = []
    if pi.get('linkedin'):
        link_parts.append(f"LinkedIn: {pi['linkedin']}")
    if pi.get('github'):
        link_parts.append(f"GitHub: {pi['github']}")
    if pi.get('portfolio'):
        link_parts.append(f"Portfolio: {pi['portfolio']}")
    
    if link_parts:
        link_text = ' | '.join(link_parts)
        story.append(Paragraph(link_text, styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Professional Summary
    if cv_data.get('professional_summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(cv_data['professional_summary'], styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
    
    # Skills
    if cv_data.get('skills'):
        story.append(Paragraph("SKILLS", heading_style))
        skills = cv_data['skills']
        
        if skills.get('technical_skills'):
            tech_skills = ', '.join(skills['technical_skills'])
            story.append(Paragraph(f"<b>Technical:</b> {tech_skills}", styles['Normal']))
        
        if skills.get('tools'):
            tools = ', '.join(skills['tools'])
            story.append(Paragraph(f"<b>Tools:</b> {tools}", styles['Normal']))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Experience
    if cv_data.get('experience'):
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
        
        for exp in cv_data['experience']:
            # Company and role
            title = f"<b>{exp.get('role', 'Role')}</b> — {exp.get('company', 'Company')}"
            story.append(Paragraph(title, styles['Normal']))
            
            # Duration and location
            duration_location = []
            if exp.get('duration'):
                duration_location.append(exp['duration'])
            if exp.get('location'):
                duration_location.append(exp['location'])
            
            if duration_location:
                story.append(Paragraph(' | '.join(duration_location), styles['Normal']))
            
            story.append(Spacer(1, 0.05*inch))
            
            # Achievements
            if exp.get('achievements'):
                for achievement in exp['achievements']:
                    story.append(Paragraph(f"• {achievement}", styles['Normal']))
            
            story.append(Spacer(1, 0.1*inch))
    
    # Education
    if cv_data.get('education'):
        story.append(Paragraph("EDUCATION", heading_style))
        
        for edu in cv_data['education']:
            degree_text = f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')}"
            if edu.get('year'):
                degree_text += f" ({edu['year']})"
            if edu.get('gpa'):
                degree_text += f" | GPA: {edu['gpa']}"
            
            story.append(Paragraph(degree_text, styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
    
    # Projects
    if cv_data.get('projects'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("PROJECTS", heading_style))
        
        for proj in cv_data['projects']:
            proj_title = f"<b>{proj.get('name', 'Project')}</b>"
            if proj.get('technologies'):
                tech = ', '.join(proj['technologies'])
                proj_title += f" ({tech})"
            
            story.append(Paragraph(proj_title, styles['Normal']))
            
            if proj.get('description'):
                story.append(Paragraph(proj['description'], styles['Normal']))
            
            if proj.get('link'):
                story.append(Paragraph(f"Link: {proj['link']}", styles['Normal']))
            
            story.append(Spacer(1, 0.08*inch))
    
    # Build PDF
    doc.build(story)
    return output_path

────────────────────────────────────────────────────────────
FILE: backend/app/main.py
────────────────────────────────────────────────────────────

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
from app.services.qdrant_service import init_collections

# Create necessary directories
os.makedirs("/app/data", exist_ok=True)
os.makedirs("/app/uploads", exist_ok=True)
os.makedirs("/app/outputs", exist_ok=True)

app = FastAPI(title="HireHubAI Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
            "optimized_cv": analysis.optimized_cv
        }
        
    except Exception as e:
        print(f"Error in get_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

═══════════════════════════════════════════════════════════
🎨 FRONTEND CODE - NUXT.JS 3 WITH GEIST FONT
═══════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
FILE: frontend/package.json
────────────────────────────────────────────────────────────

{
  "name": "hirehub-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "generate": "nuxt generate",
    "preview": "nuxt preview"
  },
  "dependencies": {
    "nuxt": "^3.10.0",
    "@nuxtjs/tailwindcss": "^6.11.4",
    "@pinia/nuxt": "^0.5.1",
    "pinia": "^2.1.7"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "typescript": "^5.3.3"
  }
}

────────────────────────────────────────────────────────────
FILE: frontend/nuxt.config.ts
────────────────────────────────────────────────────────────

export default defineNuxtConfig({
  devtools: { enabled: true },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  
  app: {
    head: {
      title: 'HireHubAI - Optimize Your CV with AI',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-powered CV optimization platform' }
      ],
      link: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Geist:wght@100;200;300;400;500;600;700;800;900&display=swap'
        }
      ]
    }
  },
  
  css: ['~/assets/css/main.css'],
  
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'
    }
  }
})

────────────────────────────────────────────────────────────
FILE: frontend/tailwind.config.ts
────────────────────────────────────────────────────────────

import type { Config } from 'tailwindcss'

export default <Config>{
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue'
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
}

────────────────────────────────────────────────────────────
FILE: frontend/assets/css/main.css
────────────────────────────────────────────────────────────

@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Geist', system-ui, sans-serif;
}

────────────────────────────────────────────────────────────
FILE: frontend/app.vue
────────────────────────────────────────────────────────────

<template>
  <div class="min-h-screen bg-gray-50">
    <NuxtPage />
  </div>
</template>

────────────────────────────────────────────────────────────
FILE: frontend/composables/useApi.ts
────────────────────────────────────────────────────────────

export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const uploadCV = async (file: File, jdText: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('jd_text', jdText)

    const response = await $fetch(`${apiBase}/api/upload-cv`, {
      method: 'POST',
      body: formData
    })

    return response
  }

  const getAnalysis = async (id: string) => {
    return await $fetch(`${apiBase}/api/analysis/${id}`)
  }

  const submitAnswers = async (id: string, answers: Record<number, string>) => {
    return await $fetch(`${apiBase}/api/submit-answers/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(answers)
    })
  }

  const getDownloadURL = (id: string) => {
    return `${apiBase}/api/download-cv/${id}`
  }

  return {
    uploadCV,
    getAnalysis,
    submitAnswers,
    getDownloadURL
  }
}

────────────────────────────────────────────────────────────
FILE: frontend/pages/index.vue
────────────────────────────────────────────────────────────

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-6xl font-bold text-gray-900 mb-4 tracking-tight">
          HireHub<span class="text-blue-600">AI</span>
        </h1>
        <p class="text-xl text-gray-600 font-light">
          Optimize your CV for any job in minutes with AI
        </p>
      </div>

      <!-- Main Form Card -->
      <div class="bg-white rounded-3xl shadow-xl p-8 backdrop-blur-sm">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- CV Upload -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              📄 Upload Your CV/Resume
            </label>
            <input
              type="file"
              accept=".pdf,.docx"
              @change="handleFileChange"
              class="block w-full text-sm text-gray-600
                file:mr-4 file:py-3 file:px-6
                file:rounded-xl file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                file:transition-colors
                cursor-pointer"
            />
            <p class="mt-2 text-sm text-gray-500">
              PDF or DOCX format only
            </p>
          </div>

          <!-- JD Input -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              📋 Paste Job Description
            </label>
            <textarea
              v-model="jdText"
              rows="14"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl
                focus:ring-2 focus:ring-blue-500 focus:border-transparent
                resize-none transition-all"
              placeholder="Paste the complete job description here..."
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg
              hover:from-blue-700 hover:to-indigo-700
              disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed
              transition-all duration-200 transform hover:scale-[1.02]"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Analyzing with AI...
            </span>
            <span v-else>🚀 Analyze & Optimize</span>
          </button>
        </form>
      </div>

      <!-- Features -->
      <div class="mt-10 text-center">
        <div class="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>No signup required</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Powered by Gemini 2.0</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Vector DB intelligence</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Results in seconds</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const { uploadCV } = useApi()

const file = ref<File | null>(null)
const jdText = ref('')
const loading = ref(false)
const error = ref('')

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

const handleSubmit = async () => {
  if (!file.value || !jdText.value) {
    error.value = 'Please upload a CV and paste a job description'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await uploadCV(file.value, jdText.value)
    await navigateTo(`/analysis/${result.id}`)
  } catch (err: any) {
    error.value = err.message || 'Something went wrong. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

────────────────────────────────────────────────────────────
FILE: frontend/pages/analysis/[id].vue
────────────────────────────────────────────────────────────

<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading analysis...</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else-if="data">
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo('/')"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Home
          </button>
          <h1 class="text-4xl font-bold text-gray-900">Analysis Results</h1>
        </div>

        <!-- Score Card -->
        <div class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <div class="text-center">
            <div :class="getScoreColorClass(data.score)" class="text-7xl font-bold">
              {{ Math.round(data.score) }}%
            </div>
            <p class="text-2xl text-gray-600 mt-2 font-medium">
              {{ getScoreLabel(data.score) }}
            </p>
            <div class="w-full bg-gray-200 rounded-full h-4 mt-6">
              <div
                class="bg-gradient-to-r from-blue-600 to-indigo-600 h-4 rounded-full transition-all duration-500"
                :style="{ width: `${data.score}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Score Breakdown -->
        <div v-if="data.breakdown" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">Score Breakdown</h2>
          <div class="space-y-4">
            <div
              v-for="([key, value], index) in Object.entries(data.breakdown)"
              :key="index"
              class="flex items-center justify-between"
            >
              <div class="flex-1">
                <div class="flex justify-between mb-1">
                  <span class="font-semibold capitalize">
                    {{ key.replace('_', ' ') }}
                  </span>
                  <span class="text-gray-600">
                    {{ Math.round((value as any).score) }}% (weight: {{ (value as any).weight }}%)
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    :style="{ width: `${(value as any).score}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Strengths -->
        <div v-if="data.strengths?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">💪 Your Strengths</h2>
          <ul class="space-y-3">
            <li v-for="(strength, idx) in data.strengths" :key="idx" class="flex items-start">
              <span class="text-green-500 mr-3 text-xl">✓</span>
              <span class="text-gray-700">{{ strength }}</span>
            </li>
          </ul>
        </div>

        <!-- Gaps -->
        <div v-if="data.gaps?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">🎯 Areas to Improve</h2>
          <div class="space-y-4">
            <div
              v-for="(gap, idx) in data.gaps"
              :key="idx"
              class="border-l-4 border-yellow-500 pl-4 py-2"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-gray-900">{{ gap.gap }}</span>
                <span :class="getPriorityClass(gap.priority)" class="text-sm px-3 py-1 rounded-full">
                  {{ gap.priority.toUpperCase() }}
                </span>
              </div>
              <p class="text-sm text-gray-600">Impact: {{ gap.impact }}</p>
            </div>
          </div>
        </div>

        <!-- Questions CTA -->
        <div class="bg-white rounded-3xl shadow-lg p-8">
          <h2 class="text-2xl font-bold mb-6">
            💬 Smart Questions ({{ data.questions?.length || 0 }})
          </h2>
          <p class="text-gray-600 mb-6">
            Answer these questions to improve your CV optimization. Your answers will help us 
            uncover hidden experience and boost your score.
          </p>
          <button
            @click="navigateTo(`/questions/${route.params.id}`)"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg hover:from-blue-700 hover:to-indigo-700
              transition-all transform hover:scale-[1.02]"
          >
            Answer Questions & Optimize CV →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getAnalysis } = useApi()

const loading = ref(true)
const data = ref<any>(null)

onMounted(async () => {
  try {
    data.value = await getAnalysis(route.params.id as string)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const getScoreColorClass = (score: number) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreLabel = (score: number) => {
  if (score >= 80) return 'Excellent Match'
  if (score >= 60) return 'Good Match'
  return 'Needs Improvement'
}

const getPriorityClass = (priority: string) => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  return 'bg-yellow-100 text-yellow-700'
}
</script>

────────────────────────────────────────────────────────────
FILE: frontend/pages/questions/[id].vue
────────────────────────────────────────────────────────────

<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/analysis/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Analysis
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">Smart Questions</h1>
          <p class="text-gray-600">
            Answer these questions to help us optimize your CV. Be honest and detailed.
          </p>
        </div>

        <!-- Questions -->
        <div class="space-y-6">
          <div
            v-for="(q, idx) in questions"
            :key="idx"
            class="bg-white rounded-2xl shadow-lg p-6"
          >
            <!-- Priority Badge -->
            <div class="flex items-start justify-between mb-3">
              <span :class="getPriorityBadgeClass(q.priority)" class="text-xs px-3 py-1 rounded-full font-semibold">
                {{ q.priority.toUpperCase() }} PRIORITY
              </span>
              <span class="text-sm text-blue-600 font-medium">
                {{ q.potential_impact }}
              </span>
            </div>

            <!-- Question -->
            <h3 class="text-lg font-semibold text-gray-900 mb-2">
              {{ idx + 1 }}. {{ q.question }}
            </h3>

            <!-- Why Asking -->
            <p class="text-sm text-gray-600 mb-4 italic">
              💡 {{ q.why_asking }}
            </p>

            <!-- Answer Textarea -->
            <textarea
              v-model="answers[idx]"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl
                focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Type your answer here..."
            />
          </div>
        </div>

        <!-- Submit Button -->
        <div class="mt-8 bg-white rounded-2xl shadow-lg p-6">
          <button
            @click="handleSubmit"
            :disabled="submitting || Object.keys(answers).length === 0"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg
              hover:from-blue-700 hover:to-indigo-700
              disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed
              transition-all transform hover:scale-[1.02]"
          >
            <span v-if="submitting">⏳ Generating Optimized CV...</span>
            <span v-else>✨ Generate Optimized CV</span>
          </button>
          <p class="text-sm text-gray-600 text-center mt-3">
            You can skip questions, but answering them improves optimization quality
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { getAnalysis, submitAnswers, getDownloadURL } = useApi()

const loading = ref(true)
const submitting = ref(false)
const questions = ref<any[]>([])
const answers = ref<Record<number, string>>({})

onMounted(async () => {
  try {
    const data = await getAnalysis(route.params.id as string)
    questions.value = data.questions
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  submitting.value = true
  
  try {
    await submitAnswers(route.params.id as string, answers.value)
    
    // Download PDF
    window.open(getDownloadURL(route.params.id as string), '_blank')
    
    // Redirect back to analysis
    await navigateTo(`/analysis/${route.params.id}`)
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const getPriorityBadgeClass = (priority: string) => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  if (priority === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}
</script>

═══════════════════════════════════════════════════════════
📚 README.md
═══════════════════════════════════════════════════════════

FILE: README.md

# HireHubAI - AI-Powered CV Optimization Platform

Built with **Nuxt 3**, **FastAPI**, **Google Gemini 2.0 Flash-Lite**, and **Qdrant Vector Database**.

## Features

- 🤖 AI-powered CV parsing with Gemini 2.0
- 📊 Compatibility scoring (0-100%)
- 🧠 RAG-enhanced analysis with Qdrant
- 💬 Smart question generation
- ✨ CV optimization
- 📄 PDF export
- 🎨 Beautiful UI with Geist font

## Tech Stack

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

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Gemini API Key (get from https://makersuite.google.com/app/apikey)

## Setup & Run

### 1. Clone and configure
```bash
# Create .env file in root
cp .env.example .env

# Add your Gemini API key
GEMINI_API_KEY=your_key_here
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

## Usage

1. Open **http://localhost:3000**
2. Upload your CV (PDF/DOCX)
3. Paste job description
4. Get compatibility score
5. Answer smart questions
6. Download optimized CV

## Docker Commands
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

## Potential Considerations & Future Improvements

### Current Limitations

⚠️ **No error recovery UI** - Frontend could benefit from better error state handling and user feedback when API calls fail

⚠️ **Single-threaded scoring** - Processing large CVs or multiple requests could be slow. Consider implementing async processing or job queues

⚠️ **No rate limiting** - Gemini API calls are uncontrolled. Could hit API quotas quickly under load. Consider implementing:
- Request throttling
- Queue system for API calls
- Caching for repeated analyses

⚠️ **No data cleanup** - Uploaded files and generated PDFs accumulate forever. Recommendations:
- Implement automatic cleanup for files older than X days
- Add manual cleanup endpoint
- Consider file size limits

⚠️ **Hardcoded CORS** - Only allows `localhost:3000`. For production:
- Use environment variables for allowed origins
- Add production domain to allowed origins

⚠️ **No RAG seeding** - Empty Qdrant collections initially (cold start problem). First users won't benefit from RAG context. Consider:
- Pre-seeding with sample CV/JD pairs
- Fallback behavior when no similar documents exist

⚠️ **No file validation** - Could accept malicious files. Add:
- File size limits (e.g., max 5MB)
- Content type verification
- Virus scanning for production use

⚠️ **No session management** - Users can't retrieve past analyses. Consider:
- Browser localStorage for analysis IDs
- Optional email-based retrieval link

⚠️ **SQLite limitations** - Not suitable for high concurrency. For production, consider:
- PostgreSQL or MySQL
- Separate read/write instances

⚠️ **No monitoring/logging** - Difficult to debug issues in production. Add:
- Structured logging (e.g., JSON logs)
- Error tracking (e.g., Sentry)
- Performance monitoring

### Recommended Next Steps

1. **Add comprehensive error handling** on frontend with retry logic
2. **Implement rate limiting** using libraries like `slowapi`
3. **Add file cleanup cron job** or scheduled task
4. **Create admin dashboard** for monitoring usage and system health
5. **Implement A/B testing** for different prompts/optimization strategies
6. **Add analytics** to track conversion rates and user behavior
7. **Implement feedback loop** where users rate optimized CVs to improve RAG quality
8. **Add multi-language support** for international users
9. **Create API documentation** using FastAPI's built-in Swagger/OpenAPI
10. **Add unit and integration tests** for critical components

### Security Considerations

🔒 **API Key Management** - Gemini API key is in `.env`. For production:
- Use secrets management (e.g., AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly
- Monitor API usage

🔒 **Input Sanitization** - PDF/DOCX parsing could expose vulnerabilities. Consider:
- Sandboxed file processing
- Content validation before AI processing

🔒 **Data Privacy** - CVs contain sensitive personal information:
- Add privacy policy
- Implement data retention policies
- Consider GDPR compliance for EU users
- Add option to delete user data

### Performance Optimizations

⚡ **Caching Strategy**
- Cache Gemini responses for identical inputs
- Cache embeddings for common skills/requirements
- Implement Redis for distributed caching

⚡ **Batch Processing**
- Process multiple embeddings in single batch
- Queue long-running tasks (e.g., Celery + Redis)

⚡ **Database Optimization**
- Add indexes on frequently queried fields
- Implement connection pooling
- Consider read replicas for scaling

## Project Structure