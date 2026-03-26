#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List available Gemini models"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
print(f"[TEST] Checking models with API Key: {api_key[:20]}...")

try:
    import google.genai as genai
    
    client = genai.Client(api_key=api_key)
    
    # List available models
    print("\n[CHECK] Available Models:")
    print("=" * 60)
    
    models = client.models.list()
    
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Methods: {model.supported_generation_methods}")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
