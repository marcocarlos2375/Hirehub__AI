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
    cover_letter = Column(JSON, nullable=True)
    learning_path = Column(JSON, nullable=True)
    interview_prep = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)
