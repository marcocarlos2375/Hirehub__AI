#!/usr/bin/env python3
"""
Test the /api/upload-cv endpoint and display full output including gaps and questions
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

# Read test files
with open('/app/test/resume.txt', 'r', encoding='utf-8') as f:
    cv_text = f.read()

with open('/app/test/job_description.txt', 'r', encoding='utf-8') as f:
    jd_text = f.read()

print("=" * 80)
print("  HireHub API Test - Full Output Display")
print("=" * 80)
print()
print(f"📄 Resume: {len(cv_text)} characters")
print(f"📋 Job Description: {len(jd_text)} characters")
print()

# Prepare request
files = {
    'file': ('resume.txt', cv_text, 'text/plain')
}
data = {
    'jd_text': jd_text
}

print("🚀 Sending request to /api/upload-cv...")
print(f"⏰ Start time: {time.strftime('%H:%M:%S')}")
print()

start_time = time.time()

try:
    response = requests.post(
        f"{API_BASE}/api/upload-cv",
        files=files,
        data=data,
        timeout=120
    )

    duration = time.time() - start_time

    print(f"⏱️  Request completed in: {duration:.2f}s")
    print(f"📊 HTTP Status: {response.status_code}")
    print()

    if response.status_code == 200:
        result = response.json()

        print("=" * 80)
        print("✅ SUCCESS - Analysis Complete")
        print("=" * 80)
        print()

        # Basic Info
        print(f"📝 Analysis ID: {result.get('id', 'N/A')}")
        print(f"📈 Compatibility Score: {result.get('score', 'N/A')}%")
        print()

        # Score Breakdown
        if 'breakdown' in result and result['breakdown']:
            print("=" * 80)
            print("📊 SCORE BREAKDOWN")
            print("=" * 80)
            for key, value in result['breakdown'].items():
                print(f"   {key}: {value}%")
            print()

        # Strengths
        if 'strengths' in result and result['strengths']:
            print("=" * 80)
            print(f"💪 STRENGTHS ({len(result['strengths'])} found)")
            print("=" * 80)
            for i, strength in enumerate(result['strengths'], 1):
                print(f"{i}. {strength}")
            print()

        # Gaps
        if 'gaps' in result and result['gaps']:
            print("=" * 80)
            print(f"🔍 GAPS IDENTIFIED ({len(result['gaps'])} found)")
            print("=" * 80)
            for i, gap in enumerate(result['gaps'], 1):
                print(f"{i}. {gap}")
            print()

        # Questions
        if 'questions' in result and result['questions']:
            print("=" * 80)
            print(f"❓ QUESTIONS GENERATED ({len(result['questions'])} questions)")
            print("=" * 80)
            for i, question in enumerate(result['questions'], 1):
                if isinstance(question, dict):
                    q_text = question.get('question', question.get('text', str(question)))
                else:
                    q_text = str(question)
                print(f"\n{i}. {q_text}")
            print()

        # Full JSON (for debugging)
        print("=" * 80)
        print("📄 COMPLETE JSON RESPONSE")
        print("=" * 80)
        print(json.dumps(result, indent=2))

    else:
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    duration = time.time() - start_time
    print(f"❌ TIMEOUT after {duration:.2f}s")
    print("The request took too long. This might indicate:")
    print("- Backend is still processing")
    print("- Network issues")
    print("- Timeout setting is too short")

except Exception as e:
    duration = time.time() - start_time
    print(f"❌ ERROR after {duration:.2f}s")
    print(f"Error: {e}")
