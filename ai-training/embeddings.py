"""Generate and manage embeddings for semantic search using free models"""

import json
import numpy as np
import os
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import pickle

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a free sentence transformer model"""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.qa_data = None
        
    def load_qa_data(self, qa_file: str) -> List[Dict]:
        """Load Q&A pairs from JSON file"""
        with open(qa_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_embeddings(self, qa_file: str, output_dir: str):
        """Generate embeddings for all Q&A pairs"""
        print("Loading Q&A data...")
        self.qa_data = self.load_qa_data(qa_file)
        
        print(f"Generating embeddings for {len(self.qa_data)} Q&A pairs...")
        
        # Extract questions and answers for embedding
        questions = [qa['question'] for qa in self.qa_data]
        answers = [qa['answer'] for qa in self.qa_data]
        
        # Generate embeddings
        print("Encoding questions...")
        question_embeddings = self.model.encode(questions, show_progress_bar=True)
        
        print("Encoding answers...")
        answer_embeddings = self.model.encode(answers, show_progress_bar=True)
        
        # Store embeddings
        self.embeddings = {
            'questions': question_embeddings,
            'answers': answer_embeddings,
            'qa_data': self.qa_data
        }
        
        # Save embeddings
        os.makedirs(output_dir, exist_ok=True)
        embeddings_file = os.path.join(output_dir, 'embeddings.pkl')
        
        with open(embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        print(f"Embeddings saved to {embeddings_file}")
        return embeddings_file   
 
    def load_embeddings(self, embeddings_file: str):
        """Load pre-generated embeddings"""
        with open(embeddings_file, 'rb') as f:
            self.embeddings = pickle.load(f)
        self.qa_data = self.embeddings['qa_data']
        print(f"Loaded embeddings for {len(self.qa_data)} Q&A pairs")
    
    def find_similar_questions(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Find most similar questions to the query"""
        if self.embeddings is None:
            raise ValueError("Embeddings not loaded. Call generate_embeddings or load_embeddings first.")
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate similarities with questions
        question_embeddings = self.embeddings['questions']
        similarities = np.dot(query_embedding, question_embeddings.T)[0]
        
        # Get top-k most similar
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            qa_pair = self.qa_data[idx]
            similarity = similarities[idx]
            results.append((qa_pair, similarity))
        
        return results
    
    def search_knowledge_base(self, query: str, threshold: float = 0.3) -> List[Dict]:
        """Search knowledge base for relevant information"""
        similar_questions = self.find_similar_questions(query, top_k=10)
        
        # Filter by threshold and return relevant answers
        relevant_answers = []
        for qa_pair, similarity in similar_questions:
            if similarity >= threshold:
                relevant_answers.append({
                    'question': qa_pair['question'],
                    'answer': qa_pair['answer'],
                    'category': qa_pair['category'],
                    'similarity': float(similarity),
                    'confidence': qa_pair['confidence']
                })
        
        return relevant_answers