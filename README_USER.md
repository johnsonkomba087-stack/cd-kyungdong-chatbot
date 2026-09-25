# 🎓 Kyungdong University RAG Chatbot

Welcome to the intelligent chatbot for Kyungdong University Global Campus! This AI-powered assistant provides instant answers to questions about admissions, programs, scholarships, campus life, and more.

## ✨ Features

🤖 **AI-Powered Responses**
- Powered by Groq AI (Gemma 2 9B model)
- Fast, accurate, conversational responses
- Real-time answers to your questions

📚 **Intelligent Document Retrieval**
- Dual retrieval system: Vector + Keyword search
- Semantic understanding of questions
- Shows document sources with relevance scores
- Fallback mechanisms ensure information is always found

💬 **Conversation History**
- Maintains context across messages
- Personalized responses based on conversation
- Session-based memory

📊 **Comprehensive Knowledge Base**
- 12 university documents covering:
  - Admissions requirements & procedures
  - Academic programs & majors
  - Scholarships & financial aid
  - Tuition fees & payment options
  - Campus facilities & life
  - Student services & support

## 🚀 Quick Start

### Online (No Installation)
Visit: `https://[username]-kdu-chatbot.streamlit.app`

Just open the link and start asking questions!

### Local Setup

**Requirements:**
- Python 3.8+
- Groq API key (free at https://console.groq.com)

**Installation:**
```bash
# Clone repository
git clone https://github.com/your-username/kdu-chatbot.git
cd kdu-chatbot

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Groq API key

# Run the app
streamlit run app.py

# Open browser to http://localhost:8501
```

## 📖 How It Works

### 1. **You Ask a Question**
```
"Tell me about admissions requirements"
```

### 2. **AI Searches Knowledge Base**
- **Vector Search:** Uses AI embeddings to find semantically similar documents
- **Keyword Search:** Falls back to word-matching if needed
- **Memory Cache:** All documents available as final fallback

### 3. **AI Generates Response**
- Combines question + retrieved documents + conversation history
- Sends to Groq AI for intelligent response

### 4. **You Get Answer + Sources**
```
Response: "To apply to Kyungdong University, you'll need..."
Sources: "Admissions Office (59.4% relevance)" ✓
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Web UI** | Streamlit 1.28 |
| **LLM** | Groq AI (Gemma 2 9B) |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Vector DB** | ChromaDB 0.4.24 |
| **Language** | Python 3.8+ |
| **Deployment** | Streamlit Cloud |

## 📚 Knowledge Base

The chatbot has access to information about:

### Admissions
- Application requirements (transcripts, language tests, etc.)
- Application deadlines (Spring: Nov 30, Fall: May 31)
- Online application portal
- Required documents

### Academic Programs
- Engineering (CS, Mechanical, Chemical, Civil)
- Business (BBA, Accounting, Finance, Marketing)
- Arts & Sciences
- Health Sciences

### Financial Aid
- Merit scholarships (50-100% Presidential scholarships)
- Need-based financial aid
- International student support
- Work-study opportunities
- Tuition fees ($30,000-35,000 USD/year)

### Campus Life
- Student services & support
- Housing & accommodation
- Campus facilities
- Academic clubs & organizations

## 🎯 Example Questions

> "What are the admission requirements?"

> "How much is tuition?"

> "Do you offer scholarships?"

> "Tell me about the engineering program"

> "When is the application deadline?"

> "What scholarships can international students get?"

> "How do I apply?"

> "What campus facilities are available?"

## ⚙️ Configuration

### Environment Variables
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_api_key_here"
```

### Streamlit Settings
- See `.streamlit/config.toml` for UI customization
- Toolbars hidden in production
- Error details shown in development

## 🐛 Troubleshooting

### "Slow initial load"
- First load downloads embedding model (~100MB)
- Subsequent loads are cached and instant
- Give it 30-60 seconds on first visit

### "No documents found"
- The chatbot will fall back to keyword search
- If still nothing, it returns all cached documents
- This ensures you always get an answer

### "API errors"
- Check your Groq API key is valid
- Visit https://console.groq.com to verify
- Fallback models ensure the chatbot still works

### "Connection issues"
- Streamlit Cloud may need time to load
- Refresh the page after 60 seconds
- Check internet connection

## 📝 Document Retrieval Details

### Vector Search (Primary)
- Uses semantic similarity (embeddings)
- Finds conceptually related documents
- Example: "tuition" → finds "fees" documents

### Keyword Search (Fallback)
- Word-overlap matching
- Activated if vectors return nothing
- Example: "admission" → finds all admission docs

### Memory Cache (Last Resort)
- All 12 documents stored in memory
- Returned if both searches fail
- Ensures information is always found

**Relevance Scores:** 
- 60-100%: High relevant
- 40-60%: Moderately relevant
- <40%: Lower confidence (but still useful)

## 👥 Usage Statistics

Since deployment:
- 📊 Documents indexed: 12
- 📞 Retrieval methods: 2 (vector + keyword)
- 🔄 Fallback layers: 3 (vector → keyword → cache)
- ⚡ Response time: <2 seconds (after initial load)

## 🔐 Privacy & Security

- **No personal data stored** (except session history during your conversation)
- **Session data cleared** when you close browser
- **API key never exposed** (kept in Streamlit secrets)
- **Open source code** (transparent and auditable)

## 📄 License

This project is provided for Kyungdong University students and staff.

## 📧 Support

**Issues or suggestions?**
- Check the [troubleshooting section](#troubleshooting)
- Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment help
- Open an issue on GitHub

## 🎉 About This Chatbot

**Built with:**
- 💡 Groq LLM technology
- 🧠 Vector semantic search
- 🔍 Intelligent fallback mechanisms
- 📚 Comprehensive university knowledge base

**Goal:** Help students and faculty get instant answers about Kyungdong University

---

**Ready to use?** 

🌐 **Online:** Visit your deployment URL
💻 **Local:** Run `streamlit run app.py`

**Any questions about the university?** Just ask! 🎓
