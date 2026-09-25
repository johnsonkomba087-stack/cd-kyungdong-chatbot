#!/usr/bin/env python
"""Comprehensive retrieval test with output to file"""

import os
import sys
from pathlib import Path

out_file = Path("test_results.txt")

def log(msg):
    """Log to both console and file"""
    print(msg)
    with open(out_file, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

# Clear previous results
out_file.unlink(missing_ok=True)

log("=" * 80)
log("COMPREHENSIVE DATA RETRIEVAL TEST")
log("=" * 80)

sys.path.insert(0, '.')

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Load API key
api_key = ''
env_file = Path('.env')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith('GROQ_API_KEY='):
            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    log("✗ ERROR: API key not found in .env file")
    sys.exit(1)

os.environ['GROQ_API_KEY'] = api_key
log(f"\n✓ API key loaded: {api_key[:25]}...")

# Test 1: Load knowledge base
log("\n[TEST 1] Loading knowledge base...")
try:
    from src.knowledge_base import load_knowledge_base
    docs = load_knowledge_base()
    log(f"✓ Loaded {len(docs)} documents")
except Exception as e:
    log(f"✗ FAILED: {e}")
    import traceback
    log(traceback.format_exc())
    sys.exit(1)

# Test 2: Initialize chatbot
log("\n[TEST 2] Initializing chatbot with embedding model...")
try:
    from src.chatbot_rag import KyungdongRAGChatbot
    bot = KyungdongRAGChatbot(groq_api_key=api_key)
    log("✓ Chatbot initialized successfully")
except Exception as e:
    log(f"✗ FAILED: {e}")
    import traceback
    log(traceback.format_exc())
    sys.exit(1)

# Test 3: Add documents
log("\n[TEST 3] Adding documents to vector database...")
try:
    bot.add_documents(docs)
    collection_count = bot.collection.count()
    log(f"✓ Documents added. Collection count: {collection_count}")
except Exception as e:
    log(f"✗ FAILED: {e}")
    import traceback
    log(traceback.format_exc())
    sys.exit(1)

# Test 4: Retrieval
log("\n[TEST 4] Testing document retrieval...")
test_queries = [
    "admission requirements international students",
    "tuition fees cost",
    "scholarships financial aid",
]

all_retrieved = False
for query in test_queries:
    try:
        log(f"\n  Query: '{query}'")
        retrieved = bot.retrieve_documents(query, top_k=2, score_threshold=0.0)
        log(f"  Retrieved: {len(retrieved)} documents")
        
        if len(retrieved) > 0:
            all_retrieved = True
            for i, doc in enumerate(retrieved, 1):
                log(f"    [{i}] {doc.source} (score: {doc.relevance_score:.1%})")
                log(f"        {doc.content[:80]}...")
        else:
            log(f"  ⚠ WARNING: No documents retrieved for this query!")
    except Exception as e:
        log(f"  ✗ ERROR during retrieval: {e}")
        import traceback
        log(traceback.format_exc())

if not all_retrieved:
    log("\n✗ CRITICAL: Could not retrieve ANY documents from ANY query!")
    log("The vector database is not working properly.")
else:
    log("\n✓ SUCCESS: Retrieved documents from all test queries!")

# Test 5: Chat
log("\n[TEST 5] Testing chat with Groq API...")
try:
    query = "Tell me about admissions"
    log(f"  Query: '{query}'")
    response, docs_used = bot.chat(query)
    log(f"  ✓ Got response from Groq")
    log(f"  Documents used: {len(docs_used)}")
    log(f"  Response preview: {response[:150]}...")
except Exception as e:
    log(f"  ✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 80)
log("TEST COMPLETE - See results above")
log("=" * 80)
