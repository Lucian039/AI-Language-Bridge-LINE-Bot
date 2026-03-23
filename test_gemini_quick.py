#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test for Gemini translation"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Verify API Key
print("=" * 60)
print("[CHECK] Environment Variables")
print("=" * 60)

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not set")
    sys.exit(1)

print(f"[OK] API Key: {api_key[:20]}... (configured)")
print(f"[OK] Model: {model}")
print()

# Test Gemini translation
print("=" * 60)
print("[TEST] Gemini Translation")
print("=" * 60)

try:
    from src.translator.gemini_translator import GeminiTranslator
    
    translator = GeminiTranslator()
    
    # Test text
    test_text = "Hello, how are you today?"
    print(f"\n[INPUT] Text: {test_text}")
    print(f"[TARGET] Language: Traditional Chinese (zh-TW)")
    print("\n[PROCESSING] Translating...")
    
    result = translator.translate(test_text, target_language="zh-TW")
    
    print("\n" + "=" * 60)
    if result["success"]:
        print("[SUCCESS] Translation completed!")
        print(f"[RESULT] {result['translation']}")
        print(f"[SOURCE] {result.get('source_language', 'Unknown')}")
        print(f"[TARGET] {result.get('target_language', 'Unknown')}")
        print("\n[OK] Gemini translation is working!")
    else:
        print("[ERROR] Translation failed")
        print(f"[MESSAGE] {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 60)
