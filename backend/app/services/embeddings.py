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

def generate_cv_jd_embeddings_batch(cv_parsed: dict, jd_parsed: dict) -> dict:
    """
    Generate all required embeddings for CV and JD analysis in a single batch
    Returns dict with all embeddings ready for storage

    This is ~4x faster than individual embedding calls
    """
    # Prepare all texts for batch processing
    texts_to_embed = []
    text_labels = []

    # 1. CV full text
    cv_full_text = f"""
    Summary: {cv_parsed.get('professional_summary', '')}
    Skills: {', '.join(cv_parsed.get('skills', {}).get('technical_skills', []))}
    Experience: {' '.join([f"{exp.get('role', '')} at {exp.get('company', '')}" for exp in cv_parsed.get('experience', [])])}
    """
    texts_to_embed.append(cv_full_text.strip())
    text_labels.append('cv_full')

    # 2. JD full text
    jd_full_text = f"""
    Position: {jd_parsed.get('position_title', '')}
    Requirements: {', '.join([skill['skill'] for skill in jd_parsed.get('hard_skills_required', [])])}
    Responsibilities: {' '.join(jd_parsed.get('responsibilities', []))}
    """
    texts_to_embed.append(jd_full_text.strip())
    text_labels.append('jd_full')

    # 3. Score query embedding
    score_query = f"Skills needed: {', '.join([s['skill'] for s in jd_parsed.get('hard_skills_required', [])])}"
    texts_to_embed.append(score_query)
    text_labels.append('score_query')

    # 4. Question query embedding (will be generated later, but we can prepare a placeholder)
    # This is done later in the flow after gaps are identified

    # Generate all embeddings in one batch
    print(f"⚡ Generating {len(texts_to_embed)} embeddings in batch...")
    embeddings = generate_embeddings_batch(texts_to_embed)

    # Return organized embeddings
    return {
        'cv_full': {'text': texts_to_embed[0], 'embedding': embeddings[0]},
        'jd_full': {'text': texts_to_embed[1], 'embedding': embeddings[1]},
        'score_query': {'text': texts_to_embed[2], 'embedding': embeddings[2]},
    }
