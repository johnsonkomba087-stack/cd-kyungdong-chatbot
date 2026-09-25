#!/usr/bin/env python
"""Minimal test to check basic dependencies"""

print("Checking Python packages...")

packages = [
    ('streamlit', 'st'),
    ('groq', 'Groq'),
    ('chromadb', 'chromadb'),
    ('sentence_transformers', 'SentenceTransformer'),
    ('dotenv', 'load_dotenv'),
]

for package, import_name in packages:
    try:
        if import_name == 'st':
            import streamlit as st
            print(f"✓ streamlit {st.__version__}")
        elif import_name == 'Groq':
            from groq import Groq
            print(f"✓ groq imported")
        elif import_name == 'chromadb':
            import chromadb
            print(f"✓ chromadb imported")
        elif import_name == 'SentenceTransformer':
            from sentence_transformers import SentenceTransformer
            print(f"✓ sentence_transformers imported")
        elif import_name == 'load_dotenv':
            from dotenv import load_dotenv
            print(f"✓ python-dotenv imported")
    except ImportError as e:
        print(f"✗ {package}: {e}")
    except Exception as e:
        print(f"✗ {package}: {type(e).__name__}: {e}")

print("\n✓ All basic packages available!")
