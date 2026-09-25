"""
Kyungdong University website-backed chatbot.
"""

import re
from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple

from groq import Groq


@dataclass
class RetrievedDocument:
    """Retrieved document with metadata."""

    content: str
    source: str
    relevance_score: float
    url: str = ""
    category: str = "general"


class KyungdongRAGChatbot:
    def __init__(
        self,
        groq_api_key: str,
        chroma_path: str = "./chroma_db",
        model_name: str = "all-MiniLM-L6-v2",
        llm_model: str = "gemma2-9b-it"
    ):
        """Initialize chatbot with a lightweight retrieval layer."""
        try:
            self.groq_client = Groq(api_key=groq_api_key)
        except Exception as exc:
            print(f"Warning: Groq client initialization failed: {exc}")
            self.groq_client = None
        self.llm_model = llm_model
        self.fallback_llm_model = "gemma-7b-it"
        self.documents_cache: List[dict] = []
        self.conversation_history = []

        self.system_prompt = """You are a helpful admissions and campus life chatbot for Kyungdong University Global Campus in Goseong, Gangwon State.

Provide accurate, friendly, and detailed information about:
- Admissions requirements and procedures
- Academic programs and majors
- Scholarships and financial aid
- Tuition fees and payment options
- Campus life and facilities
- Student services and support
- Housing and accommodation

Base your answers on the retrieved official university website content when it is available.
If you do not have enough official information, say that clearly and suggest contacting the university directly.
Always maintain a professional and welcoming tone."""

    def ensure_collection_exists(self):
        """Compatibility method for the UI; returns current document count."""
        return len(self.documents_cache)

    def reset_collection(self):
        """Clear the in-memory knowledge store."""
        self.documents_cache = []

    def add_documents(self, documents: List[dict]) -> None:
        """Store processed website documents in memory."""
        self.reset_collection()
        self.documents_cache = documents.copy()
        print(f"Loaded {len(self.documents_cache)} documents into in-memory knowledge store")

    def retrieve_documents(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.15
    ) -> List[RetrievedDocument]:
        """Retrieve relevant documents using lightweight lexical matching."""
        if not self.documents_cache:
            return []

        query_terms = self._tokenize(query)
        query_counts = Counter(query_terms)
        scored_documents = []

        for document in self.documents_cache:
            content = document.get("content", "")
            content_terms = self._tokenize(content)
            if not content_terms:
                continue

            content_counts = Counter(content_terms)
            overlap = sum(min(query_counts[token], content_counts[token]) for token in query_counts)
            normalized_overlap = overlap / max(len(query_terms), 1)

            phrase_bonus = 0.0
            lowered_content = content.lower()
            lowered_query = query.lower().strip()
            if lowered_query and lowered_query in lowered_content:
                phrase_bonus = 0.35

            category_bonus = 0.0
            category = document.get("category", "").replace("_", " ")
            if category and any(term in category for term in query_terms):
                category_bonus = 0.1

            score = min(normalized_overlap + phrase_bonus + category_bonus, 1.0)
            if score >= score_threshold:
                scored_documents.append((score, document))

        scored_documents.sort(key=lambda item: item[0], reverse=True)

        results = []
        for score, document in scored_documents[:top_k]:
            results.append(
                RetrievedDocument(
                    content=document.get("content", ""),
                    source=document.get("source", "Unknown"),
                    relevance_score=score,
                    url=document.get("url", ""),
                    category=document.get("category", "general"),
                )
            )

        return results

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9]{2,}", text.lower())

    def _generate_with_model(self, messages, model_name):
        """Call Groq with a specific model, with fallback on errors."""
        if self.groq_client is None:
            raise RuntimeError("Groq client is unavailable")
        try:
            print(f"Calling Groq with model: {model_name}")
            return self.groq_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
            )
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            raise

    def generate_response(
        self,
        query: str,
        retrieved_docs: List[RetrievedDocument]
    ) -> Tuple[str, List[RetrievedDocument]]:
        """Generate response using Groq with retrieved context."""
        if retrieved_docs:
            context = "Based on the following information from the official Kyungdong University Global website:\n\n"
            for doc in retrieved_docs:
                context += f"- {doc.content}\n"
            context += "\n"
        else:
            context = "No specific official website information was found in the current knowledge base. "

        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.conversation_history[-6:]:
            messages.append(msg)
        messages.append({
            "role": "user",
            "content": f"{context}User question: {query}"
        })

        try:
            response = self._generate_with_model(messages, self.llm_model)
            assistant_response = response.choices[0].message.content
        except Exception as first_error:
            print(f"[Groq] Primary model failed: {first_error}")
            try:
                response = self._generate_with_model(messages, self.fallback_llm_model)
                assistant_response = response.choices[0].message.content
            except Exception as second_error:
                print(f"[Groq] Both models failed: {first_error} | {second_error}")
                if retrieved_docs:
                    assistant_response = "I found the following information on the official university website:\n\n"
                    for doc in retrieved_docs:
                        assistant_response += f"• {doc.content}\n\n"
                    assistant_response += "Please verify important details on the linked official source pages."
                else:
                    assistant_response = "I apologize, but I'm currently unable to connect to the AI service and I could not find matching official website content for that question."

        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        return assistant_response, retrieved_docs

    def chat(self, user_query: str) -> Tuple[str, List[RetrievedDocument]]:
        """Main chat method: retrieve then generate."""
        retrieved_docs = self.retrieve_documents(user_query)
        response, docs = self.generate_response(user_query, retrieved_docs)
        return response, docs

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []