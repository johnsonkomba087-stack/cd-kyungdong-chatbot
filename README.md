# 🎓 Kyungdong University RAG Chatbot

An intelligent chatbot for Kyungdong University Global Campus using Retrieval-Augmented Generation (RAG).

## 🌟 Features

- **Multi-turn Conversations** - Context-aware responses across multiple exchanges
- **RAG Pipeline** - Retrieves relevant documents before generating responses
- **Live Official Data** - Pulls content from the official KDU Global website and can refresh on demand
- **Source Attribution** - Shows which documents were used with relevance scores
- **Lightweight Stack** - Groq for chat plus direct website retrieval without a heavy vector database
- **Beautiful UI** - Streamlit interface with quick topic buttons
- **Production Ready** - Deployable on cloud platforms

## Official Data Mode

The chatbot no longer depends on manually maintained text files for its main knowledge base. It fetches admissions, academics, campus life, and student service content from the official KDU Global website, caches the processed text locally for faster startup, and lets you refresh the website data from the Streamlit sidebar.

## Online Deployment

This project is ready for cloud deployment.

- Streamlit Community Cloud: use `app.py` as the main file and add `GROQ_API_KEY` in the app Secrets panel.
- Render: use the included `render.yaml` and set `GROQ_API_KEY` in the Render environment settings.
- Local secret template: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` for development.

## 📋 Prerequisites

- Python 3.9+
- Groq API Key (free from https://console.groq.com)

## 🚀 Quick Start

### 1. Clone/Download Project

### 2. Create Virtual Environment