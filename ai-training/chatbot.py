"""AI Customer Support Chatbot using free local models"""

import json
import re
from typing import List, Dict, Optional
import importlib.util
import os

# Import embeddings module
spec = importlib.util.spec_from_file_location("embeddings", os.path.join(os.path.dirname(__file__), "embeddings.py"))
embeddings_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embeddings_module)
EmbeddingManager = embeddings_module.EmbeddingManager

class CustomerSupportBot:
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.embedding_manager = EmbeddingManager()
        self.conversation_history = []
        
        # Response templates
        self.response_templates = {
            'greeting': [
                f"Hello! I'm here to help you with {company_name} products. What can I assist you with today?",
                f"Hi there! Welcome to {company_name} support. How can I help you?",
                f"Welcome! I'm your {company_name} assistant. What would you like to know?"
            ],
            'product_info': "Based on our products, here's what I found: {answer}",
            'policy_info': "Here's the information about our policy: {answer}",
            'no_match': "I'm sorry, I couldn't find specific information about that. Could you try rephrasing your question or ask about our products, shipping, or return policies?",
            'multiple_options': "I found several relevant options for you: {options}",
            'clarification': "Could you be more specific? Are you asking about: {categories}"
        }
    
    def load_knowledge_base(self, embeddings_file: str):
        """Load the knowledge base embeddings"""
        self.embedding_manager.load_embeddings(embeddings_file)
        print(f"Knowledge base loaded for {self.company_name}")
    
    def preprocess_query(self, query: str) -> str:
        """Clean and preprocess user query"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Handle common variations
        query = re.sub(r'\bwhat\'s\b', 'what is', query)
        query = re.sub(r'\bcan\'t\b', 'cannot', query)
        query = re.sub(r'\bdon\'t\b', 'do not', query)
        
        return query
    
    def detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        # Greeting patterns
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'
        
        # Product inquiry patterns
        if any(word in query_lower for word in ['product', 'mouse', 'keyboard', 'chair', 'headphone', 'webcam']):
            return 'product_inquiry'
        
        # Policy inquiry patterns
        if any(word in query_lower for word in ['shipping', 'return', 'refund', 'policy', 'warranty']):
            return 'policy_inquiry'
        
        # Comparison patterns
        if any(word in query_lower for word in ['compare', 'difference', 'better', 'best', 'recommend']):
            return 'comparison'
        
        return 'general_inquiry'
    
    def generate_response(self, query: str) -> Dict:
        """Generate response to user query"""
        # Preprocess query
        processed_query = self.preprocess_query(query)
        intent = self.detect_intent(processed_query)
        
        # Handle greetings
        if intent == 'greeting':
            return {
                'response': self.response_templates['greeting'][0],
                'intent': intent,
                'confidence': 1.0,
                'sources': []
            }
        
        # Search knowledge base
        relevant_info = self.embedding_manager.search_knowledge_base(processed_query, threshold=0.3)
        
        if not relevant_info:
            return {
                'response': self.response_templates['no_match'],
                'intent': intent,
                'confidence': 0.0,
                'sources': []
            }
        
        # Generate response based on intent and found information
        return self.format_response(relevant_info, intent, processed_query)
    
    def format_response(self, relevant_info: List[Dict], intent: str, query: str) -> Dict:
        """Format the final response"""
        if len(relevant_info) == 1:
            # Single best match
            info = relevant_info[0]
            response = info['answer']
            
            # Add context based on intent
            if intent == 'product_inquiry':
                response = f"Here's what I found about that product: {response}"
            elif intent == 'policy_inquiry':
                response = f"Here's our policy information: {response}"
            
            return {
                'response': response,
                'intent': intent,
                'confidence': info['similarity'],
                'sources': [info]
            }
        
        elif len(relevant_info) <= 3:
            # Multiple good matches - provide options
            options = []
            for info in relevant_info:
                options.append(f"• {info['question']}: {info['answer'][:100]}...")
            
            response = f"I found several relevant options:\n\n" + "\n\n".join(options)
            
            return {
                'response': response,
                'intent': intent,
                'confidence': sum(info['similarity'] for info in relevant_info) / len(relevant_info),
                'sources': relevant_info
            }
        
        else:
            # Too many matches - ask for clarification
            categories = list(set(info['category'] for info in relevant_info[:5]))
            category_text = ", ".join(categories)
            
            response = f"I found information about several topics. Could you be more specific? Are you asking about: {category_text}?"
            
            return {
                'response': response,
                'intent': 'clarification',
                'confidence': 0.5,
                'sources': relevant_info[:5]
            }
    
    def chat(self, query: str) -> str:
        """Simple chat interface"""
        response_data = self.generate_response(query)
        
        # Add to conversation history
        self.conversation_history.append({
            'user': query,
            'bot': response_data['response'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence']
        })
        
        return response_data['response']