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
        self.system_prompt = """You are the official-style AI information assistant for Kyungdong University Global Campus.

Your goals:
- Give accurate, useful, and well-reasoned answers about the university.
- Prioritize facts from the provided knowledge base over assumptions.
- Think critically before answering and avoid filling gaps with invented details.

Scope of support:
- Admissions requirements and procedures
- Academic programs and majors
- Scholarships and financial aid
- Tuition fees and payment options
- Campus life and facilities
- Student services and support
- Housing and accommodation

Reasoning and answer rules:
1. Base your answer on the provided context whenever relevant.
2. If the context is incomplete, say what is known, what is uncertain, and avoid claiming unsupported facts.
3. If no reliable information is available, clearly say so and recommend contacting the university directly.
4. When information could be misunderstood, explain it in a simple and precise way.
5. If the user asks a broad question, synthesize the most relevant points into a concise but complete answer.
6. If the user asks for steps, eligibility, deadlines, fees, or requirements, present them clearly in bullet points when helpful.
7. Never present guesses, outdated assumptions, or generic filler as confirmed university policy.

Tone:
- Professional, welcoming, and clear
- Helpful and confident only when the information is supported
- Honest about uncertainty

Your main priority is to provide trustworthy information that helps the user make a good decision."""
        
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