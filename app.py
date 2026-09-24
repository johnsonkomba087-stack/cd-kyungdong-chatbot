"""
Streamlit web interface for Kyungdong University RAG Chatbot
"""

import os
import sys
import streamlit as st
from pathlib import Path

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

# Configure Streamlit page
st.set_page_config(
    page_title="KDU Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base


def _is_placeholder(value: str) -> bool:
    if not value:
        return True
    normalized = value.strip().lower()
    return normalized in {"your_groq_api_key_here", "your_api_key_here", "your_actual_api_key_here", "changeme"}


def load_groq_api_key() -> str:
    """Resolve the Groq API key from env, .env, or the local secret files."""
    candidate_values = [
        os.getenv("GROQ_API_KEY", ""),
        os.getenv("GROQ_KEY", ""),
        os.getenv("GROQ_APIKEY", ""),
    ]
    for value in candidate_values:
        if not _is_placeholder(value):
            return value.strip()

    project_root = Path(__file__).resolve().parent
    dotenv_paths = [project_root / ".env", project_root / "app.py" / ".env"]
    for dotenv_path in dotenv_paths:
        if dotenv_path.exists():
            try:
                for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line and line.strip().startswith("GROQ_API_KEY"):
                        value = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if not _is_placeholder(value):
                            os.environ["GROQ_API_KEY"] = value
                            return value
            except Exception:
                pass

    secret_candidates = [
        project_root / ".streamlit" / "secrets.toml",
        project_root / "toml .streamlit" / "secrets.toml",
        project_root / "app.py" / ".streamlit" / "secrets.toml",
    ]
    for secret_path in secret_candidates:
        if not secret_path.exists():
            continue
        try:
            with open(secret_path, "rb") as fh:
                data = tomllib.load(fh)
            value = str(data.get("GROQ_API_KEY", "")).strip()
            if not _is_placeholder(value):
                return value
        except Exception:
            try:
                text = secret_path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "GROQ_API_KEY" in line and "=" in line:
                        value = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if not _is_placeholder(value):
                            return value
            except Exception:
                pass

    return ""


@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot once"""
    groq_api_key = load_groq_api_key()

    if not groq_api_key:
        return None

    chatbot = KyungdongRAGChatbot(groq_api_key=groq_api_key)

    # Load and add documents to vector database
    if not st.session_state.get("documents_loaded", False):
        with st.spinner("📚 Loading university knowledge base..."):
            documents = load_knowledge_base()
            chatbot.add_documents(documents)
            st.session_state.documents_loaded = True
            
    return chatbot


def get_chatbot():
    """Get or initialize chatbot - ensures documents are always loaded"""
    if "chatbot" not in st.session_state or st.session_state.chatbot is None:
        chatbot = initialize_chatbot()
        if chatbot:
            st.session_state.chatbot = chatbot
            # Ensure documents are loaded
            if st.session_state.get("documents_loaded", False) == False:
                with st.spinner("📚 Loading knowledge base..."):
                    documents = load_knowledge_base()
                    chatbot.add_documents(documents)
                    st.session_state.documents_loaded = True
        return chatbot
    return st.session_state.chatbot


def display_sources(retrieved_docs) -> None:
    """Display retrieved sources with relevance scores"""
    if retrieved_docs:
        st.markdown("### 📚 Retrieved Sources")
        st.progress(min(len(retrieved_docs) / 3, 1.0), text=f"{len(retrieved_docs)} document(s) found")
        
        for i, doc in enumerate(retrieved_docs, 1):
            # Color code by relevance
            if doc.relevance_score >= 0.7:
                relevance_class = "relevance-high"
                score_label = "🔴 High"
            elif doc.relevance_score >= 0.5:
                relevance_class = "relevance-medium"
                score_label = "🟡 Medium"
            else:
                relevance_class = ""
                score_label = "🟢 Low"
            
            with st.expander(f"📄 Source {i}: {doc.source} - {score_label}", expanded=(i==1)):
                st.write(doc.content)
                st.markdown(
                    f"<small>Relevance Score: {doc.relevance_score:.1%}</small>",
                    unsafe_allow_html=True
                )
    else:
        st.info("ℹ️ No related documents found - generating response from general knowledge")


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
        - **LLM:** Groq (Gemma 2 9B - FREE & fast!)
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
    chatbot = get_chatbot()
    
    if not chatbot:
        st.warning("⚠️ **Setup Required: GROQ_API_KEY Missing**")
        
        with st.expander("📋 Click to see setup instructions", expanded=True):
            st.markdown("""
            ### How to set up your API key:
            
            1. **Get a free API key from Groq:**
               - Visit: https://console.groq.com
               - Sign up for a free account
               - Generate an API key
            
            2. **Add the API key to this project:**
               - Create/Edit file: `.streamlit/secrets.toml`
               - Add this line:
               ```
               GROQ_API_KEY = "your_actual_api_key_here"
               ```
            
            3. **Restart the app** (press R or restart Streamlit)
            
            ### Or set as environment variable:
            ```bash
            # Windows PowerShell:
            $env:GROQ_API_KEY = "your_api_key"
            
            # Windows Command Prompt:
            set GROQ_API_KEY=your_api_key
            
            # Linux/Mac:
            export GROQ_API_KEY="your_api_key"
            ```
            """)
        st.stop()
    
    st.session_state.chatbot = chatbot
    
    # Status indicator
    with st.sidebar:
        try:
            count = chatbot.ensure_collection_exists()
            if count > 0:
                st.success(f"✅ Knowledge Base: {count} documents loaded")
            else:
                st.warning("⚠️ Knowledge Base initializing...")
        except Exception as e:
            st.warning(f"⚠️ Collection error: {str(e)[:50]}")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    
    # Display conversation history
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"])
    
    # Handle suggested question
    user_input = None
    if "suggested_question" in st.session_state:
        user_input = st.session_state.suggested_question
        del st.session_state.suggested_question
    else:
        # Chat input
        user_input = st.chat_input(
            "Ask about admissions, programs, scholarships, campus life, or student services...",
            key="chat_input"
        )
    
    # Process user input
    if user_input:
        # Initialize messages list if needed
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Add user message to session
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Searching knowledge base..."):
                retrieved_docs = chatbot.retrieve_documents(user_input, top_k=3)
            
            # Show retrieval status
            if len(retrieved_docs) > 0:
                st.success(f"✓ Found {len(retrieved_docs)} relevant document(s)")
            else:
                st.warning(f"⚠️ No relevant documents found - generating general response")
            
            with st.spinner("💭 Generating response..."):
                response, docs_used = chatbot.chat(user_input)
            
            st.markdown(response)
            
            # Display sources
            if retrieved_docs:
                st.divider()
                display_sources(retrieved_docs)
            
            # Store message with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": retrieved_docs
            })


if __name__ == "__main__":
    main()