"""
Streamlit web interface for Kyungdong University RAG Chatbot
Deployable on Streamlit Cloud, Hugging Face Spaces, or any cloud platform
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
    .chat-message-user {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .chat-message-assistant {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .source-badge {
        background-color: #4CAF50;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        margin: 2px;
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
        # Try to get from Streamlit secrets
        try:
            groq_api_key = st.secrets["GROQ_API_KEY"]
        except (FileNotFoundError, KeyError):
            return None
    
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


def display_sources(retrieved_docs) -> None:
    """Display retrieved sources with relevance scores"""
    if retrieved_docs:
        st.markdown("### 📚 Retrieved Sources")
        for i, doc in enumerate(retrieved_docs, 1):
            # Color code by relevance
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
        This is an AI-powered chatbot for Kyungdong University, built with:
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
        
        **Option 2: Create `.streamlit/secrets.toml`**
        ```toml
        GROQ_API_KEY = "your_api_key_here"
        ```
        
        **Get a free API key:** https://console.groq.com
        """)
        st.stop()
    
    st.session_state.chatbot = chatbot
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.messages = []
    
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
            with st.spinner("🤔 Thinking..."):
                response, retrieved_docs = chatbot.chat(user_input)
            
            st.markdown(response)
            
            # Display sources
            if retrieved_docs:
                display_sources(retrieved_docs)
            
            # Store message with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": retrieved_docs
            })


if __name__ == "__main__":
    main()