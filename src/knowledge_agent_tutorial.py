#!/usr/bin/env python3
"""
Knowledge Agent Tutorial: A Complete Implementation
==================================================

This tutorial demonstrates how to build a knowledge agent from scratch,
showing all the key components and how they work together.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import hashlib
from pathlib import Path

# Simple vector similarity using basic math (for educational purposes)
import math
from collections import defaultdict

@dataclass
class Document:
    """Represents a document in our knowledge base"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class SimpleEmbedder:
    """A simple text embedder for demonstration purposes"""
    
    def __init__(self):
        # In a real system, you'd use models like OpenAI embeddings, sentence-transformers, etc.
        self.vocab = {}
        self.vocab_size = 1000  # Simplified vocabulary
    
    def simple_hash_embedding(self, text: str, dim: int = 100) -> List[float]:
        """Create a simple hash-based embedding (for demo only)"""
        # Normalize text
        text = text.lower().strip()
        words = text.split()
        
        # Create a simple embedding based on word hashes
        embedding = [0.0] * dim
        for word in words:
            hash_val = hash(word) % dim
            embedding[hash_val] += 1.0
        
        # Normalize the embedding
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
        
        return embedding
    
    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding vector"""
        return self.simple_hash_embedding(text)

class KnowledgeBase:
    """The core knowledge storage and retrieval system"""
    
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.embedder = SimpleEmbedder()
        self.documents: Dict[str, Document] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                embedding TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Load existing documents
        self._load_documents()
    
    def _load_documents(self):
        """Load documents from database into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents')
        rows = cursor.fetchall()
        
        for row in rows:
            doc_id, content, metadata_str, embedding_str, created_at = row
            metadata = json.loads(metadata_str) if metadata_str else {}
            embedding = json.loads(embedding_str) if embedding_str else None
            
            doc = Document(
                id=doc_id,
                content=content,
                metadata=metadata,
                embedding=embedding,
                created_at=datetime.fromisoformat(created_at)
            )
            self.documents[doc_id] = doc
        
        conn.close()
        print(f"Loaded {len(self.documents)} documents from database")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a new document to the knowledge base"""
        if metadata is None:
            metadata = {}
        
        # Generate unique ID
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create embedding
        embedding = self.embedder.embed_text(content)
        
        # Create document
        doc = Document(
            id=doc_id,
            content=content,
            metadata=metadata,
            embedding=embedding
        )
        
        # Store in memory
        self.documents[doc_id] = doc
        
        # Persist to database
        self._save_document(doc)
        
        print(f"Added document: {doc_id[:8]}... ({len(content)} chars)")
        return doc_id
    
    def _save_document(self, doc: Document):
        """Save document to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (id, content, metadata, embedding, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            doc.id,
            doc.content,
            json.dumps(doc.metadata),
            json.dumps(doc.embedding),
            doc.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def search(self, query: str, top_k: int = 5) -> List[tuple]:
        """Search for relevant documents"""
        query_embedding = self.embedder.embed_text(query)
        
        # Calculate similarities
        similarities = []
        for doc_id, doc in self.documents.items():
            if doc.embedding:
                similarity = self.cosine_similarity(query_embedding, doc.embedding)
                similarities.append((similarity, doc))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[:top_k]

class ReasoningEngine:
    """Handles reasoning and response generation"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and generate a response"""
        print(f"\n🔍 Processing query: '{query}'")
        
        # Step 1: Search for relevant documents
        search_results = self.kb.search(query, top_k=3)
        
        # Step 2: Extract relevant information
        relevant_docs = []
        for similarity, doc in search_results:
            if similarity > 0.1:  # Threshold for relevance
                relevant_docs.append({
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'similarity': similarity
                })
        
        # Step 3: Generate response
        response = self._generate_response(query, relevant_docs)
        
        return {
            'query': query,
            'response': response,
            'sources': relevant_docs,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_response(self, query: str, relevant_docs: List[Dict]) -> str:
        """Generate a response based on query and relevant documents"""
        if not relevant_docs:
            return "I don't have enough information to answer that question. Please add more documents to the knowledge base."
        
        # Simple response generation (in a real system, this would use an LLM)
        response_parts = [
            f"Based on the information in my knowledge base, here's what I found about '{query}':\n"
        ]
        
        for i, doc in enumerate(relevant_docs, 1):
            similarity_percent = doc['similarity'] * 100
            response_parts.append(
                f"{i}. (Relevance: {similarity_percent:.1f}%) {doc['content'][:200]}..."
            )
            if doc['metadata'].get('source'):
                response_parts.append(f"   Source: {doc['metadata']['source']}")
        
        return "\n\n".join(response_parts)

class KnowledgeAgent:
    """The main knowledge agent that ties everything together"""
    
    def __init__(self, name: str = "KnowledgeBot"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.reasoning_engine = ReasoningEngine(self.knowledge_base)
        self.conversation_history = []
        
        print(f"🤖 {self.name} initialized and ready!")
    
    def learn_from_text(self, text: str, source: str = "user_input") -> str:
        """Add new information to the knowledge base"""
        metadata = {
            'source': source,
            'type': 'text',
            'added_by': 'user'
        }
        doc_id = self.knowledge_base.add_document(text, metadata)
        return f"✅ Learned new information (ID: {doc_id[:8]}...)"
    
    def learn_from_file(self, file_path: str) -> str:
        """Learn from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'source': file_path,
                'type': 'file',
                'added_by': 'user'
            }
            doc_id = self.knowledge_base.add_document(content, metadata)
            return f"✅ Learned from file: {file_path} (ID: {doc_id[:8]}...)"
        
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    def ask(self, question: str) -> str:
        """Ask the agent a question"""
        result = self.reasoning_engine.process_query(question)
        
        # Store in conversation history
        self.conversation_history.append({
            'question': question,
            'response': result['response'],
            'timestamp': result['timestamp']
        })
        
        return result['response']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            'total_documents': len(self.knowledge_base.documents),
            'conversations': len(self.conversation_history),
            'database_path': self.knowledge_base.db_path
        }

# Demo function to show the agent in action
def demo_knowledge_agent():
    """Demonstrate the knowledge agent capabilities"""
    print("=" * 60)
    print("🚀 KNOWLEDGE AGENT DEMO")
    print("=" * 60)
    
    # Create agent
    agent = KnowledgeAgent("DemoBot")
    
    # Add some sample knowledge
    print("\n📚 Adding sample knowledge...")
    
    sample_facts = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
        "Vector databases store data as high-dimensional vectors, enabling semantic search capabilities.",
        "Knowledge graphs represent information as networks of interconnected entities and relationships.",
        "Natural language processing (NLP) helps computers understand and generate human language."
    ]
    
    for fact in sample_facts:
        agent.learn_from_text(fact, "demo_data")
    
    # Ask some questions
    print("\n❓ Asking questions...")
    
    questions = [
        "What is Python?",
        "Tell me about machine learning",
        "How do vector databases work?",
        "What is artificial intelligence?"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        answer = agent.ask(question)
        print(f"A: {answer}")
    
    # Show stats
    print(f"\n📊 Agent Statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    demo_knowledge_agent()
