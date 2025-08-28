"""Smart Q&A generator with better question templates and API integration"""

import json
import re
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from .advanced_cleaner import EnhancedContent

@dataclass
class SmartQAPair:
    question: str
    answer: str
    category: str
    keywords: List[str]
    confidence: float
    answer_type: str  # 'direct', 'structured', 'enhanced'

class SmartQAGenerator:
    def __init__(self, use_api: bool = False, api_key: str = None):
        self.use_api = use_api
        self.api_key = api_key
        
        # Enhanced question templates
        self.product_templates = {
            'features': [
                "What are the key features of {product_name}?",
                "Tell me about {product_name} features",
                "What makes {product_name} special?",
                "What are the specifications of {product_name}?"
            ],
            'price': [
                "How much does {product_name} cost?",
                "What is the price of {product_name}?",
                "How much is {product_name}?",
                "What does {product_name} cost?"
            ],
            'availability': [
                "Is {product_name} available?",
                "Is {product_name} in stock?",
                "Can I buy {product_name}?",
                "When will {product_name} be available?"
            ],
            'colors': [
                "What colors are available for {product_name}?",
                "What color options does {product_name} have?",
                "Does {product_name} come in different colors?"
            ],
            'comparison': [
                "How does {product_name} compare to other {category}?",
                "Why should I choose {product_name}?",
                "What's better about {product_name}?"
            ]
        }
        
        # Policy question templates
        self.policy_templates = {
            'shipping': [
                "How long does shipping take?",
                "What is your shipping policy?",
                "How many days for delivery?",
                "When will my order arrive?",
                "Do you offer free shipping?"
            ],
            'return': [
                "What is your return policy?",
                "How do I return a product?",
                "Can I get a refund?",
                "How long do I have to return items?"
            ],
            'processing': [
                "How long does order processing take?",
                "When will my order be processed?",
                "How long before my order ships?"
            ]
        }
        
        # Category-specific questions
        self.category_templates = {
            'gaming_mouse': [
                "What gaming mice do you have?",
                "Which mouse is best for gaming?",
                "Do you have wireless gaming mice?",
                "What's the DPI of your gaming mice?",
                "Which gaming mouse is lightest?"
            ],
            'gaming_keyboard': [
                "What gaming keyboards are available?",
                "Do you have mechanical keyboards?",
                "Which keyboard has RGB lighting?",
                "Do you have wireless keyboards?",
                "What switches do your keyboards use?"
            ],
            'gaming_chair': [
                "What gaming chairs do you sell?",
                "Which chair is most comfortable?",
                "Do you have ergonomic chairs?",
                "What's the price range for gaming chairs?"
            ]
        }
    
    def generate_structured_answer(self, content: EnhancedContent, question_type: str) -> str:
        """Generate structured answer based on extracted data"""
        structured = content.structured_data
        product_name = structured.get('name', content.title)
        
        if question_type == 'features':
            answer_parts = [f"{product_name} offers several key features:"]
            
            if structured.get('features'):
                features_text = ", ".join(structured['features'])
                answer_parts.append(f"• Key features: {features_text}")
            
            if structured.get('specifications'):
                specs_text = ", ".join(structured['specifications'])
                answer_parts.append(f"• Specifications: {specs_text}")
            
            if structured.get('colors'):
                colors_text = ", ".join(structured['colors'])
                answer_parts.append(f"• Available colors: {colors_text}")
            
            if structured.get('rating'):
                answer_parts.append(f"• Customer rating: {structured['rating']}/5 stars")
            
            return "\n".join(answer_parts)
        
        elif question_type == 'price':
            answer_parts = [f"Pricing information for {product_name}:"]
            
            if structured.get('price'):
                answer_parts.append(f"• Price: {structured['price']}")
            
            if structured.get('discount'):
                answer_parts.append(f"• Current offer: {structured['discount']}")
            
            return "\n".join(answer_parts)
        
        elif question_type == 'availability':
            availability = structured.get('availability', 'unknown')
            if availability == 'in_stock':
                return f"{product_name} is currently in stock and available for purchase."
            elif availability == 'out_of_stock':
                return f"{product_name} is currently out of stock. Please check back later or contact us for restock information."
            else:
                return f"Please check the product page for current availability of {product_name}."
        
        elif question_type == 'colors':
            if structured.get('colors'):
                colors_text = ", ".join(structured['colors'])
                return f"{product_name} is available in the following colors: {colors_text}."
            else:
                return f"Please check the product page for available color options for {product_name}."
        
        # Fallback to original content
        return content.content[:300] + "..."
    
    def generate_policy_answer(self, content: EnhancedContent, question_type: str) -> str:
        """Generate policy-specific answers"""
        structured = content.structured_data
        
        if question_type == 'shipping':
            answer_parts = ["Here's our shipping information:"]
            
            if structured.get('processing_time'):
                answer_parts.append(f"• Processing time: {structured['processing_time']}")
            
            if structured.get('shipping_time'):
                answer_parts.append(f"• Shipping time: {structured['shipping_time']}")
            
            if structured.get('delivery_time'):
                answer_parts.append(f"• Delivery time: {structured['delivery_time']}")
            
            if structured.get('free_shipping'):
                answer_parts.append("• Free shipping is available on eligible orders")
            
            # Add key points
            if structured.get('key_points'):
                answer_parts.append("\nKey policy points:")
                for point in structured['key_points'][:3]:
                    answer_parts.append(f"• {point}")
            
            return "\n".join(answer_parts)
        
        elif question_type == 'return':
            answer_parts = ["Here's our return policy:"]
            
            if structured.get('return_period'):
                answer_parts.append(f"• Return period: {structured['return_period']}")
            
            if structured.get('key_points'):
                for point in structured['key_points'][:3]:
                    if 'return' in point.lower() or 'refund' in point.lower():
                        answer_parts.append(f"• {point}")
            
            return "\n".join(answer_parts)
        
        # Fallback
        return content.content[:300] + "..."
    
    def enhance_answer_with_api(self, question: str, base_answer: str) -> str:
        """Enhance answer using free API (if available)"""
        if not self.use_api or not self.api_key:
            return base_answer
        
        try:
            # Example using Hugging Face free API
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": f"Question: {question}\nContext: {base_answer}\nImproved answer:",
                "parameters": {"max_length": 200, "temperature": 0.7}
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    enhanced = result[0].get('generated_text', base_answer)
                    return enhanced
            
        except Exception as e:
            print(f"API enhancement failed: {e}")
        
        return base_answer
    
    def generate_product_qa_pairs(self, content: EnhancedContent) -> List[SmartQAPair]:
        """Generate Q&A pairs for products with structured data"""
        qa_pairs = []
        
        if content.content_type != 'product':
            return qa_pairs
        
        product_name = content.structured_data.get('name', content.title)
        
        # Generate different types of questions
        for question_type, templates in self.product_templates.items():
            # Skip if we don't have relevant data
            if question_type == 'price' and not content.structured_data.get('price'):
                continue
            if question_type == 'colors' and not content.structured_data.get('colors'):
                continue
            
            # Pick the best template
            template = templates[0]  # Use first template for now
            question = template.format(product_name=product_name, category=content.category)
            
            # Generate structured answer
            answer = self.generate_structured_answer(content, question_type)
            
            # Enhance with API if available
            if self.use_api:
                answer = self.enhance_answer_with_api(question, answer)
            
            qa_pairs.append(SmartQAPair(
                question=question,
                answer=answer,
                category=content.category,
                keywords=content.keywords,
                confidence=0.9,  # High confidence for structured answers
                answer_type='structured'
            ))
        
        return qa_pairs
    
    def generate_policy_qa_pairs(self, content: EnhancedContent) -> List[SmartQAPair]:
        """Generate Q&A pairs for policies"""
        qa_pairs = []
        
        if content.content_type != 'policy':
            return qa_pairs
        
        policy_type = content.structured_data.get('policy_type', 'general')
        
        if policy_type in self.policy_templates:
            templates = self.policy_templates[policy_type]
            
            for template in templates:
                answer = self.generate_policy_answer(content, policy_type)
                
                # Enhance with API if available
                if self.use_api:
                    answer = self.enhance_answer_with_api(template, answer)
                
                qa_pairs.append(SmartQAPair(
                    question=template,
                    answer=answer,
                    category='policy',
                    keywords=['policy', policy_type],
                    confidence=0.9,
                    answer_type='structured'
                ))
        
        return qa_pairs
    
    def generate_category_qa_pairs(self, contents: List[EnhancedContent]) -> List[SmartQAPair]:
        """Generate category overview Q&A pairs"""
        qa_pairs = []
        
        # Group by category
        category_products = {}
        for content in contents:
            if content.content_type == 'product' and content.quality_score > 0.5:
                category = content.category
                if category not in category_products:
                    category_products[category] = []
                category_products[category].append(content)
        
        # Generate category questions
        for category, products in category_products.items():
            if len(products) < 2 or category not in self.category_templates:
                continue
            
            templates = self.category_templates[category]
            
            # Create product list for answers
            product_names = [p.structured_data.get('name', p.title) for p in products[:5]]
            
            for template in templates:
                answer_parts = [f"We offer several {category.replace('_', ' ')} options:"]
                
                for i, product in enumerate(products[:5], 1):
                    name = product.structured_data.get('name', product.title)
                    price = product.structured_data.get('price', '')
                    features = ', '.join(product.structured_data.get('features', [])[:3])
                    
                    product_line = f"{i}. {name}"
                    if price:
                        product_line += f" - {price}"
                    if features:
                        product_line += f" ({features})"
                    
                    answer_parts.append(product_line)
                
                answer = "\n".join(answer_parts)
                
                qa_pairs.append(SmartQAPair(
                    question=template,
                    answer=answer,
                    category=category,
                    keywords=[category.replace('_', ' ')],
                    confidence=0.8,
                    answer_type='structured'
                ))
        
        return qa_pairs
    
    def generate_all_smart_qa_pairs(self, contents: List[EnhancedContent]) -> List[SmartQAPair]:
        """Generate all Q&A pairs with enhanced quality"""
        all_qa_pairs = []
        
        print(f"Generating smart Q&A pairs from {len(contents)} enhanced contents...")
        
        # Generate product Q&A
        product_count = 0
        for content in contents:
            if content.content_type == 'product' and content.quality_score > 0.3:
                qa_pairs = self.generate_product_qa_pairs(content)
                all_qa_pairs.extend(qa_pairs)
                product_count += 1
            elif content.content_type == 'policy':
                qa_pairs = self.generate_policy_qa_pairs(content)
                all_qa_pairs.extend(qa_pairs)
        
        # Generate category overview Q&A
        category_qa = self.generate_category_qa_pairs(contents)
        all_qa_pairs.extend(category_qa)
        
        print(f"Generated {len(all_qa_pairs)} smart Q&A pairs from {product_count} products")
        return all_qa_pairs
    
    def save_smart_qa_pairs(self, qa_pairs: List[SmartQAPair], output_file: str):
        """Save smart Q&A pairs to JSON file"""
        qa_data = []
        
        for qa in qa_pairs:
            qa_data.append({
                'question': qa.question,
                'answer': qa.answer,
                'category': qa.category,
                'keywords': qa.keywords,
                'confidence': qa.confidence,
                'answer_type': qa.answer_type
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(qa_pairs)} smart Q&A pairs to {output_file}")
        
        # Print statistics
        answer_types = {}
        categories = {}
        for qa in qa_pairs:
            answer_types[qa.answer_type] = answer_types.get(qa.answer_type, 0) + 1
            categories[qa.category] = categories.get(qa.category, 0) + 1
        
        print("\nSmart Q&A pairs by answer type:")
        for atype, count in sorted(answer_types.items()):
            print(f"  {atype}: {count} pairs")
        
        print("\nSmart Q&A pairs by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} pairs")