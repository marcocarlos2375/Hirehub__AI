import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.embeddings import generate_embedding


def calculate_vector_similarity_score(cv_data: dict, jd_data: dict) -> dict:
    """
    Calculate objective compatibility score using semantic vector similarity.
    Deterministic - same inputs always produce same score.
    """

    # Extract CV elements
    cv_skills = extract_cv_skills(cv_data)
    cv_experience = extract_cv_experience(cv_data)
    cv_education = extract_cv_education(cv_data)

    # Extract JD requirements
    jd_hard_skills = extract_jd_hard_skills(jd_data)
    jd_soft_skills = extract_jd_soft_skills(jd_data)
    jd_responsibilities = extract_jd_responsibilities(jd_data)
    jd_experience_req = jd_data.get('experience_required', {})

    # Calculate individual scores
    hard_skills_score, hard_matched, hard_missing = calculate_skills_match(cv_skills, jd_hard_skills)
    soft_skills_score, soft_matched, soft_missing = calculate_skills_match(cv_skills, jd_soft_skills)
    experience_score, exp_assessment = calculate_experience_match(cv_experience, jd_experience_req)
    domain_score = calculate_domain_match(cv_experience, jd_data.get('industry', ''))
    responsibilities_score = calculate_responsibilities_match(cv_experience, jd_responsibilities)

    # Weighted overall score (0-100)
    overall_score = round(
        hard_skills_score * 0.35 +
        soft_skills_score * 0.15 +
        experience_score * 0.20 +
        domain_score * 0.15 +
        responsibilities_score * 0.10 +
        50 * 0.05  # Logistics baseline (assume neutral)
    )

    # Build breakdown
    breakdown = {
        "hard_skills": {
            "score": round(hard_skills_score),
            "weight": 35,
            "matched": hard_matched,
            "missing": hard_missing
        },
        "soft_skills": {
            "score": round(soft_skills_score),
            "weight": 15,
            "matched": soft_matched,
            "missing": soft_missing
        },
        "experience": {
            "score": round(experience_score),
            "weight": 20,
            "candidate_years": calculate_total_years(cv_experience),
            "required_years": jd_experience_req.get('min_years', 0),
            "assessment": exp_assessment
        },
        "domain": {
            "score": round(domain_score),
            "weight": 15,
            "assessment": f"Domain match score based on industry alignment"
        },
        "portfolio": {
            "score": round(responsibilities_score),
            "weight": 10,
            "assessment": f"Responsibilities alignment score"
        },
        "logistics": {
            "score": 50,
            "weight": 5,
            "assessment": "Neutral - cannot assess from CV alone"
        }
    }

    return {
        "overall_score": overall_score,
        "breakdown": breakdown
    }


def extract_cv_skills(cv_data: dict) -> list:
    """Extract all skills from CV with their text representation"""
    skills = cv_data.get('skills', [])
    return [f"{s.get('skill', s.get('name', 'Unknown'))} ({s.get('level', 'unknown')} level)" for s in skills]


def extract_cv_experience(cv_data: dict) -> list:
    """Extract experience descriptions from employment history"""
    history = cv_data.get('employmentHistory', [])
    experiences = []
    for job in history:
        position = job.get('position', '')
        company = job.get('company', '')
        description = job.get('summary', '')
        experiences.append(f"{position} at {company}: {description}")
    return experiences


def extract_cv_education(cv_data: dict) -> list:
    """Extract education information"""
    education = cv_data.get('education', [])
    return [f"{e.get('degree', '')} in {e.get('field', '')}" for e in education]


def extract_jd_hard_skills(jd_data: dict) -> list:
    """Extract required hard skills from JD"""
    return [s['skill'] for s in jd_data.get('hard_skills_required', [])]


def extract_jd_soft_skills(jd_data: dict) -> list:
    """Extract required soft skills from JD"""
    return [s['skill'] for s in jd_data.get('soft_skills_required', [])]


def extract_jd_responsibilities(jd_data: dict) -> list:
    """Extract job responsibilities"""
    return jd_data.get('responsibilities', [])


def calculate_skills_match(cv_skills: list, jd_required_skills: list) -> tuple:
    """
    Calculate skill match using semantic similarity.
    Returns: (score, matched_skills, missing_skills)
    """
    if not jd_required_skills:
        return 100.0, [], []

    if not cv_skills:
        return 0.0, [], jd_required_skills

    # Generate embeddings
    cv_embeddings = [generate_embedding(skill) for skill in cv_skills]
    jd_embeddings = [generate_embedding(skill) for skill in jd_required_skills]

    cv_matrix = np.array(cv_embeddings)
    jd_matrix = np.array(jd_embeddings)

    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(jd_matrix, cv_matrix)

    matched_skills = []
    missing_skills = []

    # For each required skill, find best match in CV
    for idx, jd_skill in enumerate(jd_required_skills):
        max_similarity = similarity_matrix[idx].max()
        best_match_idx = similarity_matrix[idx].argmax()

        # Threshold: 0.7 = good match, 0.5-0.7 = partial, <0.5 = missing
        if max_similarity >= 0.7:
            matched_skills.append(f"{jd_skill} ({int(max_similarity * 100)}% match)")
        elif max_similarity >= 0.5:
            matched_skills.append(f"{jd_skill} ({int(max_similarity * 100)}% partial)")
        else:
            missing_skills.append(jd_skill)

    # Calculate score: percentage of well-matched skills
    full_matches = sum(1 for s in matched_skills if "% match)" in s)
    partial_matches = len(matched_skills) - full_matches

    score = ((full_matches * 1.0 + partial_matches * 0.5) / len(jd_required_skills)) * 100

    return score, matched_skills, missing_skills


def calculate_experience_match(cv_experience: list, jd_experience_req: dict) -> tuple:
    """
    Calculate experience match based on years and relevance.
    Returns: (score, assessment_text)
    """
    min_years = jd_experience_req.get('min_years', 0)
    preferred_years = jd_experience_req.get('preferred_years', min_years)

    # Calculate total years from CV
    total_years = calculate_total_years(cv_experience)

    if total_years >= preferred_years:
        score = 100
        assessment = f"Candidate has {total_years} years, exceeds preferred {preferred_years} years"
    elif total_years >= min_years:
        # Proportional score between min and preferred
        ratio = (total_years - min_years) / (preferred_years - min_years) if preferred_years > min_years else 1
        score = 70 + (ratio * 30)  # 70-100 range
        assessment = f"Candidate has {total_years} years, meets minimum {min_years} years"
    elif total_years > 0:
        # Below minimum but has some experience
        ratio = total_years / min_years if min_years > 0 else 0
        score = ratio * 70  # 0-70 range
        assessment = f"Candidate has {total_years} years, below minimum {min_years} years"
    else:
        score = 0
        assessment = f"No relevant experience found, requires {min_years} years"

    return score, assessment


def calculate_total_years(cv_experience: list) -> int:
    """Estimate total years of experience (simplified)"""
    # This is a rough estimate - can be improved
    return len(cv_experience)


def calculate_domain_match(cv_experience: list, jd_industry: str) -> float:
    """
    Calculate domain/industry match using semantic similarity.
    """
    if not jd_industry or not cv_experience:
        return 50.0  # Neutral score

    # Generate embeddings
    industry_embedding = generate_embedding(jd_industry)
    experience_embeddings = [generate_embedding(exp) for exp in cv_experience]

    # Find best match
    similarities = [
        cosine_similarity([industry_embedding], [exp_emb])[0][0]
        for exp_emb in experience_embeddings
    ]

    max_similarity = max(similarities) if similarities else 0

    # Convert to 0-100 score
    score = max_similarity * 100

    return score


def calculate_responsibilities_match(cv_experience: list, jd_responsibilities: list) -> float:
    """
    Calculate how well CV experience matches JD responsibilities.
    """
    if not jd_responsibilities or not cv_experience:
        return 50.0

    # Generate embeddings
    cv_embeddings = [generate_embedding(exp) for exp in cv_experience]
    resp_embeddings = [generate_embedding(resp) for resp in jd_responsibilities]

    cv_matrix = np.array(cv_embeddings)
    resp_matrix = np.array(resp_embeddings)

    # Calculate similarity
    similarity_matrix = cosine_similarity(resp_matrix, cv_matrix)

    # Average of best matches for each responsibility
    avg_similarity = similarity_matrix.max(axis=1).mean()

    score = avg_similarity * 100

    return score
