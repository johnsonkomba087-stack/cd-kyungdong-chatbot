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
Answer style requirements:
1) Start with a direct answer in one sentence.
2) Then provide short supporting details.
3) Do not invent facts, figures, deadlines, or policies not present in the provided context.
4) If uncertain, explicitly say "I don't know based on official data currently loaded."
Always maintain a professional and welcoming tone."""

        self.low_confidence_response = (
            "I don't know based on official data currently loaded. "
            "Please check the official Kyungdong Global pages in the source links, "
            "or contact info@kduniv.ac.kr for confirmation."
        )

        self.stopwords = {
            "what", "when", "where", "which", "who", "why", "how", "the", "and", "for", "with",
            "about", "into", "from", "your", "you", "are", "can", "does", "this", "that", "have",
            "has", "was", "were", "will", "would", "could", "should", "their", "there", "tell",
            "me", "please", "is", "to", "of", "in", "on", "at", "by", "it", "or"
        }

        self.domain_keywords = {
            "kdu", "kyungdong", "university", "campus", "admission", "admissions", "apply", "application",
            "deadline", "requirements", "documents", "undergraduate", "graduate", "master", "phd", "program",
            "programs", "major", "majors", "degree", "academics", "scholarship", "scholarships", "tuition",
            "fees", "cost", "housing", "dorm", "dormitory", "facilities", "student", "services", "career",
            "counselling", "counseling", "parttime", "visa", "international", "goseong", "gangwon"
        }

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
        score_threshold: float = 0.2
    ) -> List[RetrievedDocument]:
        """Retrieve relevant documents using lightweight lexical matching."""
        if not self.documents_cache:
            return []

        query_terms = self._tokenize(query)
        if not self._is_domain_query(query_terms):
            return []

        intent_category = self._infer_intent_category(query_terms)
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
            unique_overlap = sum(1 for token in query_counts if token in content_counts)

            phrase_bonus = 0.0
            lowered_content = content.lower()
            lowered_query = query.lower().strip()
            if lowered_query and lowered_query in lowered_content:
                phrase_bonus = 0.35

            category_bonus = 0.0
            category = document.get("category", "").replace("_", " ")
            if category and any(term in category for term in query_terms):
                category_bonus = 0.1

            intent_bonus = 0.0
            doc_category = document.get("category", "")
            if intent_category:
                if doc_category == intent_category:
                    intent_bonus = 0.25
                else:
                    intent_bonus = -0.08

            if unique_overlap == 0:
                continue
            if unique_overlap == 1 and normalized_overlap < 0.25 and intent_bonus <= 0:
                continue

            score = min(max(normalized_overlap + phrase_bonus + category_bonus + intent_bonus, 0.0), 1.0)
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

    def _assess_confidence(self, retrieved_docs: List[RetrievedDocument]) -> str:
        """Classify retrieval confidence to control answer strictness."""
        if not retrieved_docs:
            return "low"

        top_score = retrieved_docs[0].relevance_score
        avg_score = sum(doc.relevance_score for doc in retrieved_docs) / len(retrieved_docs)

        if top_score >= 0.65 and avg_score >= 0.45:
            return "high"
        if top_score >= 0.4:
            return "medium"
        return "low"

    def _tokenize(self, text: str) -> List[str]:
        terms = re.findall(r"[a-zA-Z0-9]{2,}", text.lower())
        return [term for term in terms if term not in self.stopwords]

    def _infer_intent_category(self, query_terms: List[str]) -> str:
        """Infer likely knowledge category from query tokens."""
        if not query_terms:
            return ""

        category_keywords = {
            "admissions": {"admission", "admissions", "apply", "application", "deadline", "requirements", "transfer", "documents"},
            "academics": {"program", "programs", "major", "majors", "academic", "degree", "curriculum", "undergraduate", "graduate", "phd", "master"},
            "fees": {"fee", "fees", "tuition", "cost", "costs", "payment", "scholarship", "scholarships", "financial", "aid"},
            "campus_life": {"campus", "housing", "dorm", "dormitory", "facility", "facilities", "clubs", "events", "studentlife"},
            "student_services": {"service", "services", "support", "career", "counselling", "counseling", "human", "rights", "parttime", "job"},
            "overview": {"about", "global", "why", "kdu", "university", "location", "address"},
        }

        scores = {category: 0 for category in category_keywords}
        for term in query_terms:
            for category, keywords in category_keywords.items():
                if term in keywords:
                    scores[category] += 1

        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else ""

    def _is_domain_query(self, query_terms: List[str]) -> bool:
        """Return True when query appears related to university/helpdesk domain."""
        if not query_terms:
            return False
        return any(term in self.domain_keywords for term in query_terms)

    def _summarize_docs_without_llm(self, retrieved_docs: List[RetrievedDocument]) -> str:
        """Create a direct response from retrieved docs when LLM is unavailable."""
        if not retrieved_docs:
            return self.low_confidence_response

        highlights = []
        for doc in retrieved_docs[:2]:
            first_sentence = re.split(r"(?<=[.!?])\s+", doc.content.strip())[0]
            highlights.append(f"- {first_sentence}")

        return (
            "Direct answer based on official website data:\n\n"
            + "\n".join(highlights)
            + "\n\nFor exact wording or latest updates, please verify the linked official sources."
        )

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

    def _build_style_instruction(self, style_options: dict | None) -> str:
        """Build user-facing style instruction for human-like interactions."""
        if not style_options:
            return ""

        tone = style_options.get("tone", "Friendly")
        detail_level = style_options.get("detail_level", "Balanced")
        response_language = style_options.get("response_language", "English")

        return (
            f"Response style: tone={tone}, detail={detail_level}, language={response_language}. "
            "Sound natural and conversational, but stay factual. "
            "When confident, answer directly in the first sentence. "
            "When uncertain, explicitly say you don't know based on official data."
        )

    def generate_follow_up_suggestions(
        self,
        query: str,
        retrieved_docs: List[RetrievedDocument],
        limit: int = 3
    ) -> List[str]:
        """Generate actionable follow-up question suggestions."""
        query_lower = query.lower()
        suggestions = []

        keyword_map = {
            "admission": [
                "What documents are required for this application?",
                "What are the key application deadlines?",
                "Who should I contact for admissions support?",
            ],
            "scholar": [
                "Which scholarships can international students apply for?",
                "How do scholarship and tuition payments work?",
                "Are there partial scholarships for first-year students?",
            ],
            "program": [
                "Which majors are taught fully in English?",
                "Can you compare undergraduate and graduate options?",
                "What career paths match these programs?",
            ],
            "housing": [
                "What are the dormitory options and costs?",
                "What facilities are available in student housing?",
                "How do I apply for campus accommodation?",
            ],
            "tuition": [
                "Can you break down annual tuition and living costs?",
                "What payment methods are available?",
                "Are there fee differences by program?",
            ],
            "service": [
                "What student support services are available for newcomers?",
                "How does career support work at KDU Global?",
                "Where can I get counseling or human rights support?",
            ],
        }

        for key, mapped in keyword_map.items():
            if key in query_lower:
                suggestions.extend(mapped)
                break

        if not suggestions and retrieved_docs:
            top_category = retrieved_docs[0].category
            category_defaults = {
                "admissions": [
                    "Can you explain the application process step by step?",
                    "What are the minimum language score requirements?",
                    "When should I apply for the next intake?",
                ],
                "academics": [
                    "Which courses are available in English?",
                    "Can you summarize program options by campus?",
                    "What is the difference between undergraduate and graduate tracks?",
                ],
                "fees": [
                    "Can you summarize tuition and scholarship information?",
                    "Are there additional fees besides tuition?",
                    "What financial support is available?",
                ],
                "campus_life": [
                    "What is student life like on campus?",
                    "Can you describe housing and facilities?",
                    "What events and clubs are available?",
                ],
                "student_services": [
                    "What support services are available for international students?",
                    "How can students get career guidance?",
                    "Where can students access counseling support?",
                ],
            }
            suggestions.extend(category_defaults.get(top_category, []))

        if not suggestions:
            suggestions = [
                "Tell me about admissions requirements for international students.",
                "What programs are available at KDU Global Campus?",
                "What scholarships and tuition options should I know about?",
            ]

        unique = []
        for suggestion in suggestions:
            if suggestion not in unique:
                unique.append(suggestion)
            if len(unique) >= limit:
                break

        return unique

    def generate_response(
        self,
        query: str,
        retrieved_docs: List[RetrievedDocument],
        style_options: dict | None = None
    ) -> Tuple[str, List[RetrievedDocument]]:
        """Generate response using Groq with retrieved context."""
        confidence = self._assess_confidence(retrieved_docs)

        if confidence == "low":
            assistant_response = self.low_confidence_response
            if retrieved_docs:
                assistant_response += " I found related snippets, but they are not reliable enough to answer confidently."

            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response, retrieved_docs

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

        confidence_instruction = (
            "Confidence: HIGH. Provide a direct answer first, then concise details based only on context."
            if confidence == "high"
            else "Confidence: MEDIUM. Be cautious, mention uncertainty where needed, and do not over-claim."
        )

        style_instruction = self._build_style_instruction(style_options)

        messages.append({
            "role": "user",
            "content": f"{context}{confidence_instruction}\n{style_instruction}\nUser question: {query}"
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
                    assistant_response = self._summarize_docs_without_llm(retrieved_docs)
                else:
                    assistant_response = self.low_confidence_response

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