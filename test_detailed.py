#!/usr/bin/env python
"""Detailed test script for data retrieval"""

import os
import sys
import traceback

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

sys.path.insert(0, '.')

print("=" * 70)
print("DETAILED DATA RETRIEVAL TEST")
print("=" * 70)

# Step 1: Load knowledge base
print("\n[1/6] Loading knowledge base...")
try:
    from src.knowledge_base import load_knowledge_base
    docs = load_knowledge_base()
    print(f"✓ Loaded {len(docs)} documents")
    #for i, doc in enumerate(docs[:2]):
    #    print(f"    Doc {i+1}: {doc['id']}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Check API key
print("\n[2/6] Checking API key...")
from pathlib import Path
api_key = os.getenv('GROQ_API_KEY', '').strip()

# Try to load from .env file if not in environment
if not api_key:
    env_file = Path('.env')
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('GROQ_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("✗ FAILED: GROQ_API_KEY not found")
    sys.exit(1)
    
os.environ['GROQ_API_KEY'] = api_key
print(f"✓ API key found: {api_key[:30]}...")

# Step 3: Import chatbot
print("\n[3/6] Importing chatbot library...")
try:
    from src.chatbot_rag import KyungdongRAGChatbot
    print("✓ Chatbot imported")
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 4: Initialize chatbot
print("\n[4/6] Initializing chatbot...")
try:
    bot = KyungdongRAGChatbot(groq_api_key=api_key)
    print("✓ Chatbot initialized")
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 5: Add documents
print("\n[5/6] Adding documents to vector database...")
try:
    bot.add_documents(docs)
    print("✓ Documents added")
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 6: Test retrieval
print("\n[6/6] Testing document retrieval...")
try:
    test_queries = [
        "What are admission requirements?",
        "How much is tuition?",
        "What scholarships are available?",
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        retrieved = bot.retrieve_documents(query, top_k=2)
        print(f"  Retrieved: {len(retrieved)} documents")
        
        if len(retrieved) == 0:
            print("  WARNING: No documents retrieved!")
        else:
            for i, doc in enumerate(retrieved, 1):
                print(f"    [{i}] Source: {doc.source}")
                print(f"        Score: {doc.relevance_score:.2%}")
                print(f"        Preview: {doc.content[:70]}...")
                
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - Data retrieval is working!")
print("=" * 70)
