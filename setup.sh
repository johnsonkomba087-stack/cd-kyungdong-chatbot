#!/bin/bash

# Create project directory structure
echo "🎓 Creating Kyungdong University RAG Chatbot Project..."
echo ""

# Create root directory
mkdir -p kyungdong-chatbot
cd kyungdong-chatbot

# Create subdirectories
mkdir -p src
mkdir -p .streamlit
mkdir -p chroma_db

echo "✅ Created project directories"
echo ""