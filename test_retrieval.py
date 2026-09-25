#!/usr/bin/env python
"""Test data retrieval from knowledge base"""

import sys
import os
from pathlib import Path

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing Knowledge Base and Retrieval")
print("=" * 60)

# Test 1: Load knowledge base
print("\n1. Loading knowledge base...")
try:
    from src.knowledge_base import load_knowledge_base
    docs = load_knowledge_base()
    print(f"   ✓ Loaded {len(docs)} documents")
    for i, doc in enumerate(docs[:3]):
        print(f"   - Doc {i+1}: {doc['id']} ({len(doc['content'])} chars)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Initialize chatbot
print("\n2. Initializing chatbot...")
try:
    from src.chatbot_rag import KyungdongRAGChatbot
    
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("   ✗ GROQ_API_KEY not found")
        sys.exit(1)
    
    print(f"   API Key: {api_key[:20]}...")
    
    chatbot = KyungdongRAGChatbot(groq_api_key=api_key)
    print("   ✓ Chatbot initialized")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Add documents to vector database
print("\n3. Adding documents to vector database...")
try:
    chatbot.add_documents(docs)
    print(f"   ✓ Added {len(docs)} documents")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test retrieval
print("\n4. Testing document retrieval...")
test_queries = [
    "What are the admission requirements?",
    "How much does tuition cost?",
    "What scholarships are available?",
]

for query in test_queries:
    try:
        print(f"\n   Query: '{query}'")
        retrieved = chatbot.retrieve_documents(query, top_k=2)
        print(f"   ✓ Retrieved {len(retrieved)} documents")
        for i, doc in enumerate(retrieved):
            print(f"     - Source: {doc.source}")
            print(f"       Score: {doc.relevance_score:.2%}")
            print(f"       Content: {doc.content[:100]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Test 5: Test full chat
print("\n5. Testing full chat response...")
try:
    query = "Tell me about admissions"
    print(f"   Query: '{query}'")
    response, docs = chatbot.chat(query)
    print(f"   ✓ Got response from chatbot")
    print(f"   Retrieved {len(docs)} documents")
    print(f"\n   Response preview:")
    print(f"   {response[:200]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Data retrieval test complete!")
print("=" * 60)
