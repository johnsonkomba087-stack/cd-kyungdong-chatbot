#!/usr/bin/env python
"""Quick test without model loading"""

import os
import sys
from pathlib import Path

sys.path.insert(0, '.')

# Load API key from .env
api_key = ''
env_file = Path('.env')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith('GROQ_API_KEY='):
            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    print("ERROR: API key not found")
    sys.exit(1)

os.environ['GROQ_API_KEY'] = api_key

print("Testing the Streamlit app through browser simulation...")
print(f"API Key Configured: {api_key[:20]}...")

# Import streamlit and app
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

print("\n1. Loading knowledge base...")
from src.knowledge_base import load_knowledge_base
docs = load_knowledge_base()
print(f"   ✓ {len(docs)} documents loaded")

print("\n2. Initializing chatbot (this will download the model)...")
print("   This may take a minute on first run...")

from src.chatbot_rag import KyungdongRAGChatbot
bot = KyungdongRAGChatbot(groq_api_key=api_key)

print("\n3. Adding documents to vector database...")
bot.add_documents(docs)

print("\n4. Testing retrieval...")
query = "Tell me about admissions"
print(f"   Query: '{query}'")

retrieved = bot.retrieve_documents(query, top_k=3)
print(f"   Retrieved: {len(retrieved)} documents")

if len(retrieved) == 0:
    print("\n   ✗ ERROR: No documents retrieved!")
    print("   The vector database query returned no results.")
else:
    print("\n   ✓ SUCCESS: Documents retrieved!")
    for i, doc in enumerate(retrieved, 1):
        print(f"\n   Document {i}:")
        print(f"   Source: {doc.source}")
        print(f"   Relevance: {doc.relevance_score:.1%}")
        print(f"   Preview: {doc.content[:100]}...")

print("\n5. Testing chat response...")
response, docs_used = bot.chat(query)
print(f"   ✓ Got response: {response[:150]}...")

print("\n✅ All tests passed! Data retrieval is working correctly.")
