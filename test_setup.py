#!/usr/bin/env python
"""Test script to validate the app setup"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
try:
    from src.chatbot_rag import KyungdongRAGChatbot
    print("✓ Successfully imported KyungdongRAGChatbot")
except Exception as e:
    print(f"✗ Failed to import KyungdongRAGChatbot: {e}")
    sys.exit(1)

try:
    from src.knowledge_base import load_knowledge_base
    print("✓ Successfully imported load_knowledge_base")
except Exception as e:
    print(f"✗ Failed to import load_knowledge_base: {e}")
    sys.exit(1)

print("\nTesting knowledge base...")
try:
    docs = load_knowledge_base()
    print(f"✓ Loaded {len(docs)} documents")
except Exception as e:
    print(f"✗ Failed to load knowledge base: {e}")
    sys.exit(1)

print("\nTesting API key loading...")
groq_key = os.getenv("GROQ_API_KEY", "").strip()
if groq_key:
    print(f"✓ GROQ_API_KEY found (length: {len(groq_key)})")
else:
    print("✗ GROQ_API_KEY not found in environment")

print("\n✅ All basic tests passed!")
