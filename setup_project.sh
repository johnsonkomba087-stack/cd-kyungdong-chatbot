#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎓 Kyungdong University RAG Chatbot - Complete Setup      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Check Python
echo -e "${BLUE}[1/7]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Found Python ${PYTHON_VERSION}${NC}\n"

# Create project structure
echo -e "${BLUE}[2/7]${NC} Creating project structure..."
PROJECT_DIR="kyungdong-chatbot"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory '$PROJECT_DIR' already exists${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        echo -e "${RED}❌ Setup cancelled${NC}"
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR/src"
mkdir -p "$PROJECT_DIR/.streamlit"
mkdir -p "$PROJECT_DIR/chroma_db"
cd "$PROJECT_DIR"

echo -e "${GREEN}✅ Created directory structure${NC}\n"

# Create all files
echo -e "${BLUE}[3/7]${NC} Creating application files..."

# requirements.txt
cat > requirements.txt << 'EOF'
streamlit==1.28.1
groq==0.9.0
sentence-transformers==2.2.2
chromadb==0.4.24
python-dotenv==1.0.0
EOF
echo -e "${GREEN}  ✅ requirements.txt${NC}"

# .env
cat > .env << 'EOF'
GROQ_API_KEY=
EOF
echo -e "${GREEN}  ✅ .env${NC}"

# .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
venv/
ENV/
env/
.venv
.vscode/
.idea/
.DS_Store
.env
.env.local
.streamlit/secrets.toml
.streamlit/cache/
chroma_db/
*.log
.cache/
.pytest_cache/
.coverage
Thumbs.db
EOF
echo -e "${GREEN}  ✅ .gitignore${NC}"

# src/__init__.py
cat > src/__init__.py << 'EOF'
"""Kyungdong University RAG Chatbot Package"""
EOF
echo -e "${GREEN}  ✅ src/__init__.py${NC}"

# src/knowledge_base.py
cat > src/knowledge_base.py << 'EOF'
"""
Sample knowledge base for Kyungdong University Global Campus
"""

from typing import List

UNIVERSITY_DOCUMENTS = [
    {
        "id": "admission_001",
        "content": "Kyungdong University Global Campus offers diverse undergraduate programs in Engineering, Business, Arts & Sciences, and Health Sciences. International students can apply through our online portal. Application requirements include: completed application form, official transcripts, English proficiency test (TOEFL/IELTS), and statement of purpose.",
        "source": "Admissions Office",
        "category": "admissions"
    },
    {
        "id": "admission_002",
        "content": "Application deadlines vary by program. Spring semester applications are due by November 30, and fall semester applications by May 31. Early application is recommended as some programs have rolling admissions.",
        "source": "Admissions Office",
        "category": "admissions"
    },
    {
        "id": "programs_001",
        "content": "Our Engineering programs include Computer Science, Mechanical Engineering, Chemical Engineering, and Civil Engineering. All programs are accredited and offer both theory and practical lab experience.",
        "source": "College of Engineering",
        "category": "programs"
    },
    {
        "id": "programs_002",
        "content": "Business programs include Bachelor of Business Administration (BBA), accounting, finance, marketing, and international business. Students can participate in internship programs with leading corporations.",
        "source": "College of Business",
        "category": "programs"
    },
    {
        "id": "scholarship_001",
        "content": "Merit-based scholarships are available for high-achieving students. Presidential Scholarships cover 50-100% of tuition. Academic Excellence Scholarships cover 30-50%. All incoming students are automatically considered for merit scholarships.",
        "source": "Financial Aid Office",
        "category": "scholarships"
    },
    {
        "id": "scholarship_002",
        "content": "Need-based financial aid is available to demonstrated need students. International students can apply for tuition assistance, living expense support, and work-study opportunities on campus.",
        "source": "Financial Aid Office",
        "category": "scholarships"
    },
    {
        "id": "fees_001",
        "content": "Undergraduate tuition for 2024-2025 academic year: International students pay approximately $30,000-35,000 USD per year depending on the program. Engineering programs may have slightly higher rates.",
        "source": "Office of the Registrar",
        "category": "fees"
    },
    {
        "id": "fees_002",
        "content": "Additional costs include: dormitory fees ($4,000-6,000/year), meal plan ($3,000-4,000/year), books and supplies ($1,500/year), personal expenses ($2,000/year). Total estimated cost ranges from $40,000-50,000 USD annually.",
        "source": "Office of the Registrar",
        "category": "fees"
    },
    {
        "id": "campus_001",
        "content": "The Global Campus features state-of-the-art facilities including computer labs, science centers, sports complex with gymnasium and swimming pool, library with 500,000+ volumes, and modern student lounges.",
        "source": "Campus Life Office",
        "category": "campus_life"
    },
    {
        "id": "campus_002",
        "content": "Student housing is provided for all international students in modern dormitories with amenities including 24-hour internet, laundry facilities, common kitchens, and organized social events.",
        "source": "Housing Office",
        "category": "campus_life"
    },
    {
        "id": "services_001",
        "content": "International Student Services provides visa support, orientation programs, cultural integration activities, language support, and emergency assistance. Dedicated advisors help with adjustment to campus life.",
        "source": "International Student Services",
        "category": "student_services"
    },
    {
        "id": "services_002",
        "content": "Academic support services include tutoring centers, writing labs, study groups, career counseling, and mental health services. All services are free for enrolled students.",
        "source": "Student Support Services",
        "category": "student_services"
    },
]


def load_knowledge_base() -> List[dict]:
    """Load university knowledge base"""
    return UNIVERSITY_DOCUMENTS
EOF
echo -e "${GREEN}  ✅ src/knowledge_base.py${NC}"

# src/chatbot_rag.py
cat > src/chatbot_rag.py << 'EOF'
"""
Kyungdong University RAG Chatbot
Intelligent Q&A system using Groq LLM and free embeddings
"""

import os
from typing import List, Tuple
from dataclasses import dataclass

import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq


@dataclass
class RetrievedDocument:
    """Retrieved document with metadata"""
    content: str
    source: str
    relevance_score: float


class KyungdongRAGChatbot:
    def __init__(
        self,
        groq_api_key: str,
        chroma_path: str = "./chroma_db",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """Initialize RAG chatbot"""
        self.groq_client = Groq(api_key=groq_api_key)
        self.embedding_model = SentenceTransformer(model_name)

        # Initialize Chroma vector database
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="kyungdong_documents",
            metadata={"hnsw:space": "cosine"}
        )

        # System prompt for university context
        self.system_prompt = """You are a helpful admissions and campus life chatbot for Kyungdong University Global Campus.

Provide accurate, friendly, and detailed information about:
- Admissions requirements and procedures
- Academic programs and majors
- Scholarships and financial aid
- Tuition fees and payment options
- Campus life and facilities
- Student services and support
- Housing and accommodation

If you don't have information about something, politely say so and suggest contacting the university directly.
Always maintain a professional and welcoming tone."""

        self.conversation_history = []

    def add_documents(self, documents: List[dict]) -> None:
        """Add documents to vector database"""
        for doc in documents:
            doc_id = doc.get("id", str(hash(doc["content"])))
            embedding = self.embedding_model.encode(doc["content"]).tolist()

            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[doc["content"]],
                metadatas=[{
                    "source": doc.get("source", "unknown"),
                    "category": doc.get("category", "general")
                }]
            )

    def retrieve_documents(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.3
    ) -> List[RetrievedDocument]:
        """Retrieve relevant documents using vector similarity"""
        query_embedding = self.embedding_model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results["documents"] and results["documents"][0]:
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                # Convert distance to similarity score (cosine)
                similarity = 1 - distance

                if similarity >= score_threshold:
                    retrieved.append(RetrievedDocument(
                        content=doc,
                        source=metadata.get("source", "Unknown"),
                        relevance_score=similarity
                    ))

        return retrieved

    def generate_response(
        self,
        query: str,
        retrieved_docs: List[RetrievedDocument]
    ) -> Tuple[str, List[RetrievedDocument]]:
        """Generate response using Groq with retrieved context"""

        # Build context from retrieved documents
        context = ""
        if retrieved_docs:
            context = "Based on the following information:\n\n"
            for doc in retrieved_docs:
                context += f"- {doc.content}\n"
            context += "\n"
        else:
            context = "Note: No specific information found in the database. "

        # Build messages for multi-turn conversation
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history (keep last 3 exchanges for context)
        for msg in self.conversation_history[-6:]:
            messages.append(msg)

        # Add current query with context
        messages.append({
            "role": "user",
            "content": f"{context}\nUser question: {query}"
        })

        # Call Groq API
        response = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9
        )

        assistant_response = response.choices[0].message.content

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        return assistant_response, retrieved_docs

    def chat(self, user_query: str) -> Tuple[str, List[RetrievedDocument]]:
        """Main chat method: retrieve -> generate"""

        # Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(user_query)

        # Generate response with context
        response, docs = self.generate_response(user_query, retrieved_docs)

        return response, docs

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
EOF
echo -e "${GREEN}  ✅ src/chatbot_rag.py${NC}"

# .streamlit/config.toml
cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#1f4788"
backgroundColor = "#f5f5f5"
secondaryBackgroundColor = "#e3f2fd"
textColor = "#1f1f1f"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"
EOF
echo -e "${GREEN}  ✅ .streamlit/config.toml${NC}"

# .streamlit/secrets.toml
cat > .streamlit/secrets.toml << 'EOF'
GROQ_API_KEY = ""
EOF
echo -e "${GREEN}  ✅ .streamlit/secrets.toml${NC}"

# app.py (Main Streamlit App)
cat > app.py << 'EOF'
"""
Streamlit web interface for Kyungdong University RAG Chatbot
"""

import os
import sys
import streamlit as st
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base

# Page config
st.set_page_config(
    page_title="Kyungdong University Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #1f4788;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .relevance-high {
        color: #2e7d32;
        font-weight: bold;
    }
    .relevance-medium {
        color: #f57c00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot once"""
    groq_api_key = os.getenv("GROQ_API_KEY", "")

    if not groq_api_key:
        try:
            groq_api_key = st.secrets["GROQ_API_KEY"]
        except (FileNotFoundError, KeyError):
            return None

    if not groq_api_key:
        return None

    chatbot = KyungdongRAGChatbot(groq_api_key=groq_api_key)

    if not st.session_state.get("documents_loaded", False):
        with st.spinner("📚 Loading university knowledge base..."):
            documents = load_knowledge_base()
            chatbot.add_documents(documents)
            st.session_state.documents_loaded = True

    return chatbot


def display_sources(retrieved_docs) -> None:
    """Display retrieved sources with relevance scores"""
    if retrieved_docs:
        st.markdown("### 📚 Retrieved Sources")
        for i, doc in enumerate(retrieved_docs, 1):
            if doc.relevance_score >= 0.7:
                relevance_class = "relevance-high"
                score_label = "High"
            elif doc.relevance_score >= 0.5:
                relevance_class = "relevance-medium"
                score_label = "Medium"
            else:
                relevance_class = ""
                score_label = "Low"

            with st.expander(f"📄 Source {i}: {doc.source}", expanded=True):
                st.write(doc.content)
                st.markdown(
                    f"<span class='{relevance_class}'>"
                    f"Relevance Score: {doc.relevance_score:.2%} ({score_label})"
                    f"</span>",
                    unsafe_allow_html=True
                )


def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Kyungdong University Global Campus</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #555; margin-top: -10px;">Intelligent Chatbot Assistant</h3>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("### ℹ️ About This Chatbot")
        st.markdown("""
        This is an AI-powered chatbot powered by:
        - **LLM:** Groq (mixtral-8x7b)
        - **Embeddings:** Sentence Transformers (free)
        - **Database:** Chroma (vector database)
        - **Interface:** Streamlit

        Ask questions about:
        - 🎓 Admissions & Programs
        - 💰 Scholarships & Fees
        - 🏫 Campus Life
        - 👨‍🎓 Student Services
        """)

        st.markdown("---")

        st.markdown("### 🎯 Quick Topics")
        topics = {
            "📝 Admissions": "Tell me about the admissions process for international students",
            "💼 Programs": "What programs does Kyungdong offer?",
            "🎓 Scholarships": "What scholarships are available for international students?",
            "💵 Tuition": "How much does tuition cost per year?",
            "🏠 Campus": "Describe the campus facilities and housing",
            "🆘 Support": "What student services are available?",
        }

        for label, question in topics.items():
            if st.button(label, use_container_width=True, key=label):
                st.session_state.suggested_question = question

        st.markdown("---")

        if st.button("🔄 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.get("chatbot"):
                st.session_state.chatbot.clear_history()
            st.success("✅ Chat history cleared!")

    # Check for API key
    chatbot = initialize_chatbot()

    if not chatbot:
        st.error("""
        ❌ **GROQ_API_KEY not found!**

        Please set your Groq API key:

        **Option 1: Environment Variable**
        ```bash
        export GROQ_API_KEY="your_api_key_here"
        streamlit run app.py
        ```

        **Option 2: Update `.streamlit/secrets.toml`**
        ```toml
        GROQ_API_KEY = "your_api_key_here"
        ```

        **Get a free API key:** https://console.groq.com
        """)
        st.stop()

    st.session_state.chatbot = chatbot

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"])

    user_input = None
    if "suggested_question" in st.session_state:
        user_input = st.session_state.suggested_question
        del st.session_state.suggested_question
    else:
        user_input = st.chat_input(
            "Ask about admissions, programs, scholarships, campus life, or student services...",
            key="chat_input"
        )

    if user_input:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                response, retrieved_docs = chatbot.chat(user_input)

            st.markdown(response)

            if retrieved_docs:
                display_sources(retrieved_docs)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": retrieved_docs
            })


if __name__ == "__main__":
    main()
EOF
echo -e "${GREEN}  ✅ app.py${NC}"

echo ""

# Create virtual environment
echo -e "${BLUE}[4/7]${NC} Creating Python virtual environment..."
python3 -m venv venv
echo -e "${GREEN}✅ Virtual environment created${NC}\n"

# Activate virtual environment and install dependencies
echo -e "${BLUE}[5/7]${NC} Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed successfully${NC}\n"

# Create startup script
echo -e "${BLUE}[6/7]${NC} Creating startup scripts..."

# run.sh for macOS/Linux
cat > run.sh << 'SCRIPT'
#!/bin/bash
source venv/bin/activate
streamlit run app.py
SCRIPT
chmod +x run.sh
echo -e "${GREEN}  ✅ run.sh${NC}"

# run.bat for Windows
cat > run.bat << 'SCRIPT'
@echo off
call venv\Scripts\activate.bat
streamlit run app.py
SCRIPT
echo -e "${GREEN}  ✅ run.bat${NC}"

echo ""

# Create README
echo -e "${BLUE}[7/7]${NC} Creating documentation..."

cat > README.md << 'EOF'
# 🎓 Kyungdong University RAG Chatbot

An intelligent chatbot for Kyungdong University Global Campus using Retrieval-Augmented Generation (RAG).

## ✨ Features

- **Multi-turn Conversations** - Context-aware responses
- **RAG Pipeline** - Retrieves relevant documents before responding
- **Source Attribution** - Shows which documents were used
- **Free Resources** - Groq LLM, Sentence Transformers, Chroma vector DB
- **Beautiful UI** - Streamlit interface with quick buttons
- **Production Ready** - Deployable on cloud platforms

## 🚀 Quick Start

### macOS/Linux: