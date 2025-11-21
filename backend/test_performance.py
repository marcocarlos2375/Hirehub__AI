#!/usr/bin/env python3
"""
Performance Benchmark Script for HireHub CV Parsing
Tests actual timing with backend/test/resume.txt
"""

import time
import sys
import os
from typing import Dict, List
from contextlib import contextmanager

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cv_parser import parse_cv_with_gemini
from app.services.jd_analyzer import analyze_jd_with_gemini
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import (
    get_qdrant_client,
    store_cv_embedding,
    store_jd_embedding,
    search_similar_cvs,
    search_similar_jds
)
from app.services.scorer import calculate_compatibility_score
from app.services.question_gen import generate_smart_questions
from app.config import get_settings

# Sample job description for testing
SAMPLE_JD = """
Senior Full Stack Developer - Cloud Platform Team

We're seeking an experienced Full Stack Developer to join our Cloud Platform team.
You'll be responsible for building scalable SaaS applications using modern technologies.

Required Skills:
- 5+ years of experience with JavaScript/TypeScript
- Strong experience with React and Next.js
- Proficiency in Node.js and backend frameworks (Express, NestJS)
- Experience with PostgreSQL and MongoDB databases
- Knowledge of AWS cloud services and infrastructure
- Docker and Kubernetes experience
- Experience with CI/CD pipelines and DevOps practices

Responsibilities:
- Design and implement scalable microservices architecture
- Lead technical decisions for frontend and backend development
- Mentor junior developers and conduct code reviews
- Implement automated testing and deployment pipelines
- Collaborate with product team on feature requirements

Nice to Have:
- Experience with GraphQL
- Python/Flask knowledge
- AWS certifications
- Open source contributions
"""

class Timer:
    """Simple timer context manager"""
    def __init__(self, name: str, results: Dict[str, float]):
        self.name = name
        self.results = results
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        print(f"⏱️  Starting: {self.name}...", flush=True)
        return self

    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        self.results[self.name] = elapsed
        print(f"✅ Completed: {self.name} in {elapsed:.2f}s\n", flush=True)


def format_results(results: Dict[str, float]) -> str:
    """Format timing results into a readable report"""
    total_time = sum(results.values())

    # Group by category
    gemini_operations = [
        "Gemini API - CV Parse",
        "Gemini API - JD Parse",
        "Gemini API - Scoring",
        "Gemini API - Questions"
    ]

    embedding_operations = [
        "Embedding - CV",
        "Embedding - JD",
        "Embedding - Score Query",
        "Embedding - Question Query"
    ]

    qdrant_operations = [
        "Qdrant - Store CV",
        "Qdrant - Store JD",
        "Qdrant - Search CVs",
        "Qdrant - Search JDs"
    ]

    gemini_total = sum(results.get(op, 0) for op in gemini_operations)
    embedding_total = sum(results.get(op, 0) for op in embedding_operations)
    qdrant_total = sum(results.get(op, 0) for op in qdrant_operations)

    report = "\n" + "="*60 + "\n"
    report += "         PERFORMANCE BENCHMARK RESULTS\n"
    report += "="*60 + "\n\n"

    report += "📄 TEXT EXTRACTION:\n"
    if "Text Extraction" in results:
        pct = (results["Text Extraction"] / total_time) * 100
        report += f"   {results['Text Extraction']:>6.2f}s ({pct:>5.1f}%)\n\n"

    report += "🤖 GEMINI API CALLS:\n"
    for op in gemini_operations:
        if op in results:
            pct = (results[op] / total_time) * 100
            report += f"   {op:<30} {results[op]:>6.2f}s ({pct:>5.1f}%)\n"
    pct = (gemini_total / total_time) * 100
    report += f"   {'─'*30} {'─'*6}   {'─'*7}\n"
    report += f"   {'Subtotal':<30} {gemini_total:>6.2f}s ({pct:>5.1f}%)\n\n"

    report += "🧠 EMBEDDING GENERATION:\n"
    for op in embedding_operations:
        if op in results:
            pct = (results[op] / total_time) * 100
            report += f"   {op:<30} {results[op]:>6.2f}s ({pct:>5.1f}%)\n"
    pct = (embedding_total / total_time) * 100
    report += f"   {'─'*30} {'─'*6}   {'─'*7}\n"
    report += f"   {'Subtotal':<30} {embedding_total:>6.2f}s ({pct:>5.1f}%)\n\n"

    report += "💾 QDRANT OPERATIONS:\n"
    for op in qdrant_operations:
        if op in results:
            pct = (results[op] / total_time) * 100
            report += f"   {op:<30} {results[op]:>6.2f}s ({pct:>5.1f}%)\n"
    pct = (qdrant_total / total_time) * 100
    report += f"   {'─'*30} {'─'*6}   {'─'*7}\n"
    report += f"   {'Subtotal':<30} {qdrant_total:>6.2f}s ({pct:>5.1f}%)\n\n"

    report += "="*60 + "\n"
    report += f"⏱️  TOTAL TIME:                     {total_time:>6.2f}s\n"
    report += "="*60 + "\n\n"

    report += "📊 SUMMARY:\n"
    report += f"   Gemini API:      {gemini_total:>6.2f}s ({(gemini_total/total_time)*100:>5.1f}%)\n"
    report += f"   Embeddings:      {embedding_total:>6.2f}s ({(embedding_total/total_time)*100:>5.1f}%)\n"
    report += f"   Qdrant:          {qdrant_total:>6.2f}s ({(qdrant_total/total_time)*100:>5.1f}%)\n"
    report += f"   Other:           {total_time - gemini_total - embedding_total - qdrant_total:>6.2f}s\n"

    return report


def main():
    print("\n" + "="*60)
    print("   HireHub CV Parsing Performance Benchmark")
    print("="*60 + "\n")

    # Storage for timing results
    results: Dict[str, float] = {}

    # Read test resume
    resume_path = os.path.join(os.path.dirname(__file__), 'test', 'resume.txt')
    print(f"📄 Test Resume: {resume_path}\n")

    try:
        with Timer("Text Extraction", results):
            with open(resume_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
            print(f"   Extracted {len(cv_text)} characters")

        # Step 1: Parse CV with Gemini
        with Timer("Gemini API - CV Parse", results):
            cv_parsed = parse_cv_with_gemini(cv_text)
            print(f"   Parsed CV into structured JSON")

        # Step 2: Parse JD with Gemini
        with Timer("Gemini API - JD Parse", results):
            jd_parsed = analyze_jd_with_gemini(SAMPLE_JD)
            print(f"   Analyzed job description")

        # Step 3: Generate CV embedding
        with Timer("Embedding - CV", results):
            # Simulate what store_cv_embeddings does
            cv_summary = cv_parsed.get("professional_summary", "")
            cv_skills = ", ".join(cv_parsed.get("technical_skills", {}).get("programming_languages", []))
            cv_text_for_embedding = f"{cv_summary} {cv_skills}"
            cv_embedding = generate_embedding(cv_text_for_embedding)
            print(f"   Generated {len(cv_embedding)}-dimensional embedding")

        # Step 4: Generate JD embedding
        with Timer("Embedding - JD", results):
            jd_summary = jd_parsed.get("job_title", "") + " " + jd_parsed.get("company_description", "")
            jd_embedding = generate_embedding(jd_summary)
            print(f"   Generated {len(jd_embedding)}-dimensional embedding")

        # Step 5: Store CV embedding in Qdrant
        fake_cv_id = "benchmark-test-cv"
        with Timer("Qdrant - Store CV", results):
            cv_point_id = store_cv_embedding(
                cv_id=fake_cv_id,
                text=cv_text_for_embedding[:500],
                embedding=cv_embedding,
                metadata={"section": "full", "benchmark": True}
            )
            print(f"   Stored CV embedding: {cv_point_id}")

        # Step 6: Store JD embedding in Qdrant
        fake_jd_id = "benchmark-test-jd"
        with Timer("Qdrant - Store JD", results):
            jd_point_id = store_jd_embedding(
                jd_id=fake_jd_id,
                text=jd_summary[:500],
                embedding=jd_embedding,
                metadata={"requirement_type": "general", "benchmark": True}
            )
            print(f"   Stored JD embedding: {jd_point_id}")

        # Step 7: Generate embedding for RAG query (scoring)
        with Timer("Embedding - Score Query", results):
            query_embedding_score = generate_embedding("compatibility analysis")
            print(f"   Generated query embedding for scoring")

        # Step 8: Search similar CVs (RAG for scoring)
        with Timer("Qdrant - Search CVs", results):
            similar_cvs = search_similar_cvs(query_embedding_score, limit=3)
            print(f"   Found {len(similar_cvs)} similar CVs")

        # Step 9: Search similar JDs (RAG for scoring)
        with Timer("Qdrant - Search JDs", results):
            similar_jds = search_similar_jds(query_embedding_score, limit=3)
            print(f"   Found {len(similar_jds)} similar JDs")

        # Step 10: Calculate compatibility score with Gemini
        with Timer("Gemini API - Scoring", results):
            score_data = calculate_compatibility_score(cv_parsed, jd_parsed, fake_cv_id)
            print(f"   Calculated compatibility score: {score_data.get('compatibility_score', 'N/A')}%")

        # Step 11: Generate embedding for question generation
        with Timer("Embedding - Question Query", results):
            query_embedding_questions = generate_embedding("experience gaps")
            print(f"   Generated query embedding for questions")

        # Step 12: Generate smart questions with Gemini
        with Timer("Gemini API - Questions", results):
            gaps = score_data.get("gaps", [])[:3]  # Top 3 gaps
            questions = generate_smart_questions(cv_parsed, jd_parsed, gaps, fake_cv_id)
            print(f"   Generated {len(questions)} smart questions")

        # Print formatted results
        print(format_results(results))

        # Cleanup: Remove test points from Qdrant
        print("🧹 Cleaning up test data from Qdrant...")
        try:
            client = get_qdrant_client()
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Delete by metadata filter
            client.delete(
                collection_name="cv_embeddings",
                points_selector=Filter(
                    must=[FieldCondition(key="cv_id", match=MatchValue(value=fake_cv_id))]
                )
            )
            client.delete(
                collection_name="jd_embeddings",
                points_selector=Filter(
                    must=[FieldCondition(key="jd_id", match=MatchValue(value=fake_jd_id))]
                )
            )
            print("✅ Cleanup complete\n")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}\n")

    except FileNotFoundError:
        print(f"❌ Error: Resume file not found at {resume_path}")
        print("   Please ensure the test resume exists at backend/test/resume.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
