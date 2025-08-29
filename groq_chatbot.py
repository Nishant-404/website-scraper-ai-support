#!/usr/bin/env python3
"""
Advanced AI Customer Support Chatbot using Groq API
Provides intelligent responses based on scraped website data
"""

import json
import os
from typing import List, Dict, Any, Optional
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class GroqChatbot:
    def __init__(self, api_key: str, qa_file: str = None, company_name: str = "AI Assistant"):
        """Initialize the Groq-powered chatbot"""
        self.client = Groq(api_key=api_key)
        self.qa_file = qa_file
        self.qa_pairs = []
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.question_vectors = None
        
        # Load Q&A data
        self.load_qa_data()
        
        # Create vector embeddings for questions
        if self.qa_pairs:
            self.create_embeddings()
    
    def load_qa_data(self):
        """Load Q&A pairs from JSON file"""
        try:
            if os.path.exists(self.qa_file):
                with open(self.qa_file, 'r', encoding='utf-8') as f:
                    self.qa_pairs = json.load(f)
                print(f"Loaded {len(self.qa_pairs)} Q&A pairs")
            else:
                print(f"Q&A file not found: {self.qa_file}")
        except Exception as e:
            print(f"Error loading Q&A data: {e}")
    
    def create_embeddings(self):
        """Create TF-IDF embeddings for questions"""
        try:
            questions = [qa.get('question', '') for qa in self.qa_pairs]
            self.question_vectors = self.vectorizer.fit_transform(questions)
            print("Created question embeddings")
        except Exception as e:
            print(f"Error creating embeddings: {e}")
    
    def find_relevant_context(self, user_question: str, top_k: int = 5) -> List[Dict]:
        """Find most relevant Q&A pairs for context"""
        if self.question_vectors is None:
            return []
        
        try:
            # Vectorize user question
            user_vector = self.vectorizer.transform([user_question])
            
            # Calculate similarities
            similarities = cosine_similarity(user_vector, self.question_vectors).flatten()
            
            # Get top-k most similar questions
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            relevant_context = []
            for idx in top_indices:
                similarity_score = float(similarities[idx])
                if similarity_score > 0.1:  # Minimum similarity threshold
                    relevant_context.append({
                        'question': self.qa_pairs[idx].get('question', ''),
                        'answer': self.qa_pairs[idx].get('answer', ''),
                        'category': self.qa_pairs[idx].get('category', ''),
                        'similarity': similarity_score
                    })
            
            return relevant_context
        except Exception as e:
            print(f"Error finding relevant context: {e}")
            return []
    
    def create_system_prompt(self, relevant_context: List[Dict]) -> str:
        """Create system prompt with relevant context"""
        company_name = getattr(self, 'company_name', 'our company')
        base_prompt = f"""You are a customer support assistant for {company_name}.

Instructions:
1. Give concise, direct answers (max 150 words)
2. Be professional and helpful
3. Use the provided context
4. If no info available, say so briefly

"""
        
        if relevant_context:
            base_prompt += "CONTEXT:\n"
            for i, context in enumerate(relevant_context[:3], 1):  # Limit to top 3
                base_prompt += f"{i}. {context.get('answer', '')}\n"
        else:
            base_prompt += "No specific context found.\n"
        
        base_prompt += "\nProvide a concise, helpful response (max 150 words)."
        
        return base_prompt
    
    def get_response(self, user_question: str, model: str = "llama3-8b-8192") -> Dict[str, Any]:
        """Get AI response using Groq API"""
        try:
            # Find relevant context
            relevant_context = self.find_relevant_context(user_question)
            
            # Create system prompt
            system_prompt = self.create_system_prompt(relevant_context)
            
            # Get response from Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                model=model,
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=200,
                top_p=0.8
            )
            
            response_text = chat_completion.choices[0].message.content
            
            return {
                'response': response_text,
                'relevant_context': relevant_context,
                'model_used': model,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}",
                'relevant_context': [],
                'model_used': model,
                'success': False,
                'error': str(e)
            }
    
    def chat_loop(self):
        """Interactive chat loop"""
        company_name = getattr(self, 'company_name', 'AI Customer Support')
        print(f"🤖 {company_name}")
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    company_name = getattr(self, 'company_name', 'our support')
                    print(f"\n🤖 Thank you for using {company_name}! Have a great day!")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 Thinking...")
                
                # Get AI response
                result = self.get_response(user_input)
                
                print(f"\n🤖 Assistant: {result['response']}")
                
                # Show context info if available
                if result['relevant_context']:
                    print(f"\n📚 (Based on {len(result['relevant_context'])} relevant sources)")
                
            except KeyboardInterrupt:
                print("\n\n🤖 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Main function to run the chatbot"""
    # API key - in production, use environment variables
    api_key = "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"
    
    # Initialize chatbot
    print("🚀 Initializing Groq-powered chatbot...")
    chatbot = GroqChatbot(api_key)
    
    if not chatbot.qa_pairs:
        print("❌ No Q&A data loaded. Please run the scraper and data processor first.")
        return
    
    # Start chat
    chatbot.chat_loop()

if __name__ == "__main__":
    main()