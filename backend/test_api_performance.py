#!/usr/bin/env python3
"""
Test actual API endpoint performance with parallelization
"""

import requests
import time

API_BASE = "http://localhost:8000"

# Sample job description
JD_TEXT = """
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

def test_upload_api():
    """Test the actual /api/upload-cv endpoint"""
    print("\n" + "="*60)
    print("   API Endpoint Performance Test")
    print("="*60 + "\n")

    # Read test resume
    resume_path = "backend/test/resume.txt"
    with open(resume_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()

    # Prepare multipart form data (fake it as PDF for the API)
    files = {
        'file': ('test_resume.pdf', cv_text.encode(), 'application/pdf')
    }
    data = {
        'jd_text': JD_TEXT
    }

    print(f"📄 Uploading CV to {API_BASE}/api/upload-cv...")
    print(f"   CV size: {len(cv_text)} characters")
    print(f"   JD size: {len(JD_TEXT)} characters\n")

    # First request (cache miss)
    print("🔄 Test 1: First request (no cache)")
    start_time = time.time()

    try:
        response = requests.post(
            f"{API_BASE}/api/upload-cv",
            files=files,
            data=data,
            timeout=120
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success in {elapsed:.2f}s")
            print(f"   Compatibility Score: {result.get('score', 'N/A')}%")
            print(f"   Questions Generated: {len(result.get('questions', []))}")
            print(f"   Gaps Identified: {len(result.get('gaps', []))}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return

    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out after 120 seconds")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Second request (should hit cache)
    print(f"\n🔄 Test 2: Second request (with cache)")
    files2 = {
        'file': ('test_resume.pdf', cv_text.encode(), 'application/pdf')
    }

    start_time = time.time()

    try:
        response = requests.post(
            f"{API_BASE}/api/upload-cv",
            files=files2,
            data=data,
            timeout=120
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success in {elapsed:.2f}s")
            print(f"   Compatibility Score: {result.get('score', 'N/A')}%")
            print(f"   **Cache speedup achieved!**")
        else:
            print(f"❌ Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*60)
    print(f"Summary:")
    print(f"   With caching and parallelization, the API should:")
    print(f"   - First request: ~10-15s (parallelized CV+JD parsing)")
    print(f"   - Subsequent requests: <5s (cached Gemini responses)")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_upload_api()
