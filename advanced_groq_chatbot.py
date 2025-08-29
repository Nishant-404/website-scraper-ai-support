#!/usr/bin/env python3
"""
Production-ready AI Customer Support Chatbot using Groq API
Features: Environment variables, error handling, logging, and advanced context matching
"""

import json
import os
from typing import List, Dict, Any, Optional
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import logging
from product_query_filter import ProductQueryFilter
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)

class AdvancedGroqChatbot:
    def __init__(self, qa_file: str = None, user_id: int = None):
        """Initialize the advanced Groq-powered chatbot"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.query_filter = ProductQueryFilter()
        self.user_id = user_id
        self.qa_file = qa_file
        self.qa_pairs = []
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=1000,
            ngram_range=(1, 2),  # Include bigrams for better matching
            min_df=1,
            max_df=0.95
        )
        self.question_vectors = None
        
        # Configuration from environment
        self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
        self.temperature = float(os.getenv('GROQ_TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('GROQ_MAX_TOKENS', '200'))
        
        # Load Q&A data and create embeddings
        if self.qa_file and os.path.exists(self.qa_file):
            self.load_qa_data()
            if self.qa_pairs:
                self.create_embeddings()
        else:
            logging.warning("No Q&A file provided or file doesn't exist")
        
        logging.info(f"Chatbot initialized with {len(self.qa_pairs)} Q&A pairs")
    
    def load_qa_data(self):
        """Load Q&A pairs from JSON file"""
        try:
            if os.path.exists(self.qa_file):
                with open(self.qa_file, 'r', encoding='utf-8') as f:
                    self.qa_pairs = json.load(f)
                logging.info(f"Loaded {len(self.qa_pairs)} Q&A pairs")
            else:
                logging.error(f"Q&A file not found: {self.qa_file}")
        except Exception as e:
            logging.error(f"Error loading Q&A data: {e}")
    
    def create_embeddings(self):
        """Create TF-IDF embeddings for questions"""
        try:
            questions = [qa.get('question', '') for qa in self.qa_pairs]
            self.question_vectors = self.vectorizer.fit_transform(questions)
            logging.info("Created question embeddings successfully")
        except Exception as e:
            logging.error(f"Error creating embeddings: {e}")
    
    def find_relevant_context(self, user_question: str, top_k: int = 5) -> List[Dict]:
        """Find most relevant Q&A pairs for context with improved matching"""
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
                similarity_score = similarities[idx]
                if similarity_score > 0.05:  # Lower threshold for more context
                    qa_pair = self.qa_pairs[idx]
                    relevant_context.append({
                        'question': qa_pair.get('question', ''),
                        'answer': qa_pair.get('answer', ''),
                        'category': qa_pair.get('category', 'General'),
                        'url': qa_pair.get('url', ''),
                        'similarity': float(similarity_score)
                    })
            
            logging.info(f"Found {len(relevant_context)} relevant context items")
            return relevant_context
            
        except Exception as e:
            logging.error(f"Error finding relevant context: {e}")
            return []
    
    def create_system_prompt(self, relevant_context: List[Dict], user_question: str) -> str:
        """Create enhanced system prompt with relevant context"""
        company_name = getattr(self, 'company_name', 'our company')
        base_prompt = f"""You are a customer support assistant for {company_name}.

INSTRUCTIONS:
1. Give concise, direct answers using the provided context
2. Keep responses under 150 words
3. Be helpful and professional
4. If no specific info is available, say so briefly
5. Focus on the most important details only

COMPANY: {company_name} - providing excellent products and services to our customers.

"""
        
        if relevant_context:
            base_prompt += "RELEVANT INFO:\n"
            for i, context in enumerate(relevant_context[:3], 1):  # Limit to top 3
                base_prompt += f"{i}. {context.get('answer', '')}\n"
        else:
            base_prompt += "No specific info found. Provide a brief general response.\n"
        
        base_prompt += f"\nQUESTION: {user_question}\n"
        base_prompt += "Give a concise, helpful answer (max 150 words)."
        
        return base_prompt
    
    def get_response(self, user_question: str) -> Dict[str, Any]:
        """Get AI response using Groq API with enhanced error handling"""
        start_time = datetime.now()
        
        try:
            # Filter query to ensure it's product-related
            should_process, filtered_response = self.query_filter.filter_query(user_question)
            
            if not should_process:
                # Return standard response for non-product queries
                return {
                    'response': filtered_response,
                    'relevant_context': [],
                    'model_used': self.model,
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'success': True,
                    'filtered': True
                }
            
            # Find relevant context
            relevant_context = self.find_relevant_context(user_question)
            
            # Create system prompt
            system_prompt = self.create_system_prompt(relevant_context, user_question)
            
            # Get response from Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=0.8
            )
            
            response_text = chat_completion.choices[0].message.content
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Log successful interaction
            logging.info(f"Response generated in {response_time:.2f}s for question: {user_question[:50]}...")
            
            return {
                'response': response_text,
                'relevant_context': relevant_context,
                'model_used': self.model,
                'response_time': response_time,
                'success': True
            }
            
        except Exception as e:
            error_msg = f"I apologize, but I'm experiencing technical difficulties. Please try again later."
            logging.error(f"Error generating response: {e}")
            
            return {
                'response': error_msg,
                'relevant_context': [],
                'model_used': self.model,
                'response_time': (datetime.now() - start_time).total_seconds(),
                'success': False,
                'error': str(e)
            }
    
    def chat_loop(self):
        """Interactive chat loop with enhanced UI"""
        company_name = getattr(self, 'company_name', 'AI Customer Support')
        print(f"🚀 {company_name} - Powered by Groq")
        print("=" * 60)
        print(f"Ask me anything about {company_name}'s products, services, or policies!")
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'help' for usage tips")
        print("=" * 60)
        
        conversation_count = 0
        
        while True:
            try:
                user_input = input(f"\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    company_name = getattr(self, 'company_name', 'our support')
                    print(f"\n🤖 Thank you for using {company_name}! We had {conversation_count} exchanges.")
                    print("Have a great day! 👋")
                    break
                
                if user_input.lower() == 'help':
                    print("\n📋 Usage Tips:")
                    print("• Ask about products, services, pricing, or policies")
                    print("• Be specific for better results (e.g., 'shipping policy' vs 'shipping')")
                    company_name = getattr(self, 'company_name', 'our company')
                    print(f"• I can help with technical questions about {company_name} solutions")
                    print("• Type 'quit' to exit")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 Analyzing your question...")
                
                # Get AI response
                result = self.get_response(user_input)
                conversation_count += 1
                
                company_name = getattr(self, 'company_name', 'AI Assistant')
                print(f"\n🤖 {company_name}:")
                print("-" * 40)
                print(result['response'])
                
                # Show additional info
                if result['relevant_context']:
                    print(f"\n📚 Response based on {len(result['relevant_context'])} relevant sources")
                
                if result.get('response_time'):
                    print(f"⚡ Response time: {result['response_time']:.2f}s")
                
            except KeyboardInterrupt:
                print(f"\n\n🤖 Session ended. We had {conversation_count} exchanges. Goodbye! 👋")
                break
            except Exception as e:
                logging.error(f"Error in chat loop: {e}")
                print(f"\n❌ Unexpected error: {e}")

def main():
    """Main function to run the advanced chatbot"""
    try:
        print("🚀 Initializing Advanced Groq-powered Chatbot...")
        chatbot = AdvancedGroqChatbot()
        
        if not chatbot.qa_pairs:
            print("❌ No Q&A data loaded. Please run the scraper and data processor first.")
            print("Run: python reprocess_data.py")
            return
        
        # Start chat
        chatbot.chat_loop()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure GROQ_API_KEY is set")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        logging.error(f"Failed to initialize chatbot: {e}")

if __name__ == "__main__":
    main()