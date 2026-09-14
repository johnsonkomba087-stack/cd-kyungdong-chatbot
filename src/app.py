"""
Streamlit web interface for Kyungdong University RAG Chatbot
Deployable on Streamlit Cloud, Hugging Face Spaces, or any cloud platform
"""

import os
import sys
from typing import List
import streamlit as st
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot_rag import KyungdongRAGChatbot
from knowledge_base import load_knowledge_base

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
    }
    .relevance-medium {
        color: #f57c00;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot once"""
    groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not found. Please set it in secrets or environment.")
        st.stop()

    chatbot = KyungdongRAGChatbot(groq_api_key=groq_api_key)

    # Load and add documents to vector database
    if not st.session_state.get("documents_loaded", False):
        with st.spinner("Loading university knowledge base..."):
            documents = load_knowledge_base()
            chatbot.add_documents(documents)
            st.session_state.documents_loaded = True

    return chatbot

def display_sources(retrieved_docs) -> None:
    """Display retrieved sources with relevance scores"""
    if retrieved_docs:
        st.markdown("### 📚 Sources")
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

            with st.expander(f"📄 Source {i}: {doc.source}", expanded=False):
                st.markdown(f"**Source:** {doc.source}")
                st.markdown(f"**Content:** {doc.content}")
                st.markdown(
                    f"<span class='{relevance_class}'>"
                    f"**Relevance Score:** {doc.relevance_score:.2%} ({score_label})"
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
            "📝 Admissions": "Tell me about the admissions process",
            "💼 Programs": "What programs does Kyungdong offer?",
            "🎓 Scholarships": "What scholarships are available?",
            "💵 Tuition": "How much does tuition cost?",
            "🏠 Campus": "Describe the campus facilities",
            "🆘 Support": "What student services are available?",
        }

        for label, question in topics.items():
            if st.button(label, use_container_width=True):
                st.session_state.suggested_question = question

        st.markdown("---")

        if st.button("🔄 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chatbot.clear_history()
            st.success("Chat history cleared!")

    # Initialize chatbot
    chatbot = initialize_chatbot()
    st.session_state.chatbot = chatbot

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"])

    # Handle suggested question
    if "suggested_question" in st.session_state:
        user_input = st.session_state.suggested_question
        del st.session_state.suggested_question
    else:
        # Chat input
        user_input = st.chat_input("Ask about admissions, programs, scholarships, campus life, or student services...")

    # Process user input
    if user_input:
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
            with st.spinner("Thinking..."):
                response, retrieved_docs = chatbot.chat(user_input)

            st.markdown(response)

            # Display sources
            display_sources(retrieved_docs)

            # Store message with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": retrieved_docs
            })

if __name__ == "__main__":
    main()