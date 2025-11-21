#!/usr/bin/env python3
"""
Performance Test for HireHub AI Backend
Tests both first request (no cache) and cached request performance
"""

import requests
import time
import json
from pathlib import Path

API_URL = "http://localhost:8000/api/upload-cv"

def test_upload_performance():
    """Test upload-cv endpoint performance"""

    # Read test files
    resume_path = Path("backend/test/resume.txt")
    jd_path = Path("backend/test/job_description.txt")

    with open(resume_path, 'r') as f:
        resume_text = f.read()

    with open(jd_path, 'r') as f:
        jd_text = f.read()

    print("=" * 80)
    print("🚀 HIREHUB AI - PERFORMANCE TEST WITH OPTIMIZATIONS")
    print("=" * 80)
    print()

    # Test 1: First request (no cache)
    print("📊 TEST 1: FIRST REQUEST (No Cache)")
    print("-" * 80)

    files = {'file': ('resume.txt', resume_text, 'text/plain')}
    data = {'jd_text': jd_text}

    start_time = time.time()
    response = requests.post(API_URL, files=files, data=data, timeout=180)
    elapsed_1 = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: SUCCESS")
        print(f"⏱️  Total Time: {elapsed_1:.2f}s")
        print(f"📈 Compatibility Score: {result['score']}%")
        print(f"🎯 Gaps Found: {len(result.get('gaps', []))}")
        print(f"❓ Questions Generated: {len(result.get('questions', []))}")
        print()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return

    # Wait a moment to ensure cache is written
    time.sleep(2)

    # Test 2: Second request (with cache)
    print("📊 TEST 2: SECOND REQUEST (With Cache)")
    print("-" * 80)

    files = {'file': ('resume.txt', resume_text, 'text/plain')}
    data = {'jd_text': jd_text}

    start_time = time.time()
    response = requests.post(API_URL, files=files, data=data, timeout=180)
    elapsed_2 = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: SUCCESS")
        print(f"⏱️  Total Time: {elapsed_2:.2f}s")
        print(f"📈 Compatibility Score: {result['score']}%")
        print(f"🎯 Gaps Found: {len(result.get('gaps', []))}")
        print(f"❓ Questions Generated: {len(result.get('questions', []))}")
        print()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return

    # Performance Summary
    print("=" * 80)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 80)
    print()
    print(f"FIRST REQUEST (No Cache):     {elapsed_1:>8.2f}s")
    print(f"SECOND REQUEST (With Cache):  {elapsed_2:>8.2f}s")
    print()

    improvement = ((elapsed_1 - elapsed_2) / elapsed_1) * 100
    speedup = elapsed_1 / elapsed_2

    print(f"⚡ Cache Improvement:          {improvement:>7.1f}%")
    print(f"🚀 Speedup Factor:             {speedup:>7.1f}x")
    print()

    # Compare with targets
    print("=" * 80)
    print("🎯 TARGET COMPARISON")
    print("=" * 80)
    print()
    print(f"Target for First Request:     <10s")
    print(f"Actual First Request:         {elapsed_1:.2f}s", "✅ PASS" if elapsed_1 < 10 else "❌ FAIL")
    print()
    print(f"Target for Cached Request:    <5s")
    print(f"Actual Cached Request:        {elapsed_2:.2f}s", "✅ PASS" if elapsed_2 < 5 else "❌ FAIL")
    print()

    # Optimization breakdown
    print("=" * 80)
    print("📈 OPTIMIZATION BREAKDOWN")
    print("=" * 80)
    print()
    print("✅ Async-compatible caching decorator")
    print("✅ Parallel scoring + question generation")
    print("✅ Cached scorer.py and question_gen.py")
    print("✅ Cached cv_optimizer.py")
    print("✅ Cached cover_letter_gen.py")
    print("✅ Cached learning_recommender.py")
    print("✅ Cached interview_prep.py")
    print()

if __name__ == "__main__":
    try:
        test_upload_performance()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
