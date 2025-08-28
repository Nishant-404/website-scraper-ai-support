"""Generate Q&A pairs from cleaned content for AI training"""

import json
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from .cleaner import CleanedContent

@dataclass
class QAPair:
    question: str
    answer: str
    category: str
    keywords: List[str]
    confidence: float  # 0-1 score for quality

class QAGenerator:
    def __init__(self):
        # Question templates for different content types
        self.product_question_templates = [
            "What are the features of {product_name}?",
            "Tell me about {product_name}",
            "What are the specifications of {product_name}?",
            "How much does {product_name} cost?",
            "Is {product_name} wireless?",
            "What colors are available for {product_name}?",
            "What makes {product_name} special?",
            "Can you describe {product_name}?",
        ]
        
        self.category_question_templates = {
            'gaming_mouse': [
                "What gaming mice do you have?",
                "Which mouse is best for gaming?",
                "Do you have wireless gaming mice?",
                "What's the DPI of your gaming mice?",
                "Which mouse is lightest?",
            ],
            'gaming_keyboard': [
                "What gaming keyboards are available?",
                "Do you have mechanical keyboards?",
                "Which keyboard has RGB lighting?",
                "What's the difference between your keyboards?",
                "Do you have wireless keyboards?",
            ],
            'gaming_chair': [
                "What gaming chairs do you sell?",
                "Which chair is most comfortable?",
                "Do you have ergonomic chairs?",
                "What's special about your gaming chairs?",
            ],
            'audio_equipment': [
                "What microphones do you have?",
                "Which mic is best for streaming?",
                "Do you have wireless microphones?",
                "What headphones are available?",
            ],
            'video_equipment': [
                "What webcams do you sell?",
                "Which camera is best for streaming?",
                "Do you have 4K webcams?",
                "What's the quality of your webcams?",
            ]
        }
        
        # Answer patterns for different question types
        self.answer_patterns = {
            'features': "The {product_name} features {features}. {additional_info}",
            'specifications': "The {product_name} has the following specifications: {specs}. {additional_info}",
            'general': "{product_name} is {description}. {additional_info}",
            'category': "We offer several {category} options: {products}. {additional_info}",
        }
    
    def extract_product_name(self, title: str) -> str:
        """Extract clean product name from title"""
        # Remove common suffixes
        name = re.sub(r'\s*–\s*Kreo$', '', title)
        name = re.sub(r'\s*\|\s*.*$', '', name)
        return name.strip()
    
    def extract_features_from_content(self, content: str) -> List[str]:
        """Extract key features from product content"""
        features = []
        
        # Look for feature patterns
        feature_patterns = [
            r'(\d+(?:g|dpi|hz|ms|inch))',  # Technical specs
            r'(wireless|wired|rgb|mechanical|ergonomic)',  # Key features
            r'(gaming|professional|premium|ultra|pro)',  # Quality indicators
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features.extend([match.lower() for match in matches])
        
        # Look for descriptive features
        if 'lightweight' in content.lower():
            features.append('lightweight')
        if 'comfortable' in content.lower():
            features.append('comfortable')
        if 'durable' in content.lower():
            features.append('durable')
        
        return list(set(features))
    
    def generate_product_qa_pairs(self, content: CleanedContent) -> List[QAPair]:
        """Generate Q&A pairs for a product page"""
        qa_pairs = []
        
        if content.content_type != 'product':
            return qa_pairs
        
        product_name = self.extract_product_name(content.title)
        features = self.extract_features_from_content(content.content)
        
        # Generate feature-based Q&A
        if features:
            question = f"What are the features of {product_name}?"
            feature_text = ", ".join(features[:5])  # Top 5 features
            answer = f"The {product_name} features {feature_text}. {content.content[:200]}..."
            
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                category=content.category,
                keywords=content.keywords,
                confidence=0.8
            ))
        
        # Generate general description Q&A
        question = f"Tell me about {product_name}"
        answer = f"{product_name} is {content.content[:300]}..."
        
        qa_pairs.append(QAPair(
            question=question,
            answer=answer,
            category=content.category,
            keywords=content.keywords,
            confidence=0.7
        ))
        
        # Generate category-specific questions
        if content.category in self.category_question_templates:
            templates = self.category_question_templates[content.category]
            for template in templates[:2]:  # Limit to 2 per product
                # Customize the answer based on the product
                answer = f"Yes, we have the {product_name}. {content.content[:200]}..."
                
                qa_pairs.append(QAPair(
                    question=template,
                    answer=answer,
                    category=content.category,
                    keywords=content.keywords,
                    confidence=0.6
                ))
        
        return qa_pairs
    
    def generate_policy_qa_pairs(self, content: CleanedContent) -> List[QAPair]:
        """Generate Q&A pairs for policy pages"""
        qa_pairs = []
        
        if content.content_type != 'policy':
            return qa_pairs
        
        # Common policy questions
        policy_questions = {
            'shipping': [
                "What is your shipping policy?",
                "How long does shipping take?",
                "Do you offer free shipping?",
                "What are your shipping rates?",
            ],
            'return': [
                "What is your return policy?",
                "How do I return a product?",
                "What is your refund policy?",
                "Can I exchange a product?",
            ],
            'privacy': [
                "What is your privacy policy?",
                "How do you handle my personal data?",
                "Do you share customer information?",
            ]
        }
        
        # Determine policy type
        policy_type = 'general'
        title_lower = content.title.lower()
        if 'shipping' in title_lower:
            policy_type = 'shipping'
        elif 'return' in title_lower or 'refund' in title_lower:
            policy_type = 'return'
        elif 'privacy' in title_lower:
            policy_type = 'privacy'
        
        # Generate Q&A pairs
        if policy_type in policy_questions:
            for question in policy_questions[policy_type]:
                answer = content.content[:400] + "..."
                
                qa_pairs.append(QAPair(
                    question=question,
                    answer=answer,
                    category='policy',
                    keywords=['policy', policy_type],
                    confidence=0.9
                ))
        
        return qa_pairs
    
    def generate_category_overview_qa(self, contents: List[CleanedContent]) -> List[QAPair]:
        """Generate overview Q&A pairs for product categories"""
        qa_pairs = []
        
        # Group products by category
        category_products = {}
        for content in contents:
            if content.content_type == 'product':
                category = content.category
                if category not in category_products:
                    category_products[category] = []
                category_products[category].append(content)
        
        # Generate category overview Q&A
        for category, products in category_products.items():
            if len(products) < 2:  # Skip categories with too few products
                continue
            
            product_names = [self.extract_product_name(p.title) for p in products[:5]]
            
            questions = [
                f"What {category.replace('_', ' ')} products do you have?",
                f"Show me your {category.replace('_', ' ')} collection",
                f"What are your best {category.replace('_', ' ')} products?",
            ]
            
            for question in questions:
                answer = f"We offer several {category.replace('_', ' ')} options including: {', '.join(product_names)}. Each product has unique features designed for different needs."
                
                qa_pairs.append(QAPair(
                    question=question,
                    answer=answer,
                    category=category,
                    keywords=[category.replace('_', ' ')],
                    confidence=0.7
                ))
        
        return qa_pairs
    
    def generate_all_qa_pairs(self, contents: List[CleanedContent]) -> List[QAPair]:
        """Generate all Q&A pairs from cleaned content"""
        all_qa_pairs = []
        
        print(f"Generating Q&A pairs from {len(contents)} cleaned pages...")
        
        # Generate product-specific Q&A
        product_count = 0
        for content in contents:
            if content.content_type == 'product':
                qa_pairs = self.generate_product_qa_pairs(content)
                all_qa_pairs.extend(qa_pairs)
                product_count += 1
            elif content.content_type == 'policy':
                qa_pairs = self.generate_policy_qa_pairs(content)
                all_qa_pairs.extend(qa_pairs)
        
        # Generate category overview Q&A
        category_qa = self.generate_category_overview_qa(contents)
        all_qa_pairs.extend(category_qa)
        
        print(f"Generated {len(all_qa_pairs)} Q&A pairs from {product_count} products")
        return all_qa_pairs
    
    def save_qa_pairs(self, qa_pairs: List[QAPair], output_file: str):
        """Save Q&A pairs to JSON file"""
        qa_data = []
        
        for qa in qa_pairs:
            qa_data.append({
                'question': qa.question,
                'answer': qa.answer,
                'category': qa.category,
                'keywords': qa.keywords,
                'confidence': qa.confidence
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(qa_pairs)} Q&A pairs to {output_file}")
        
        # Print some statistics
        categories = {}
        for qa in qa_pairs:
            cat = qa.category
            categories[cat] = categories.get(cat, 0) + 1
        
        print("Q&A pairs by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} pairs")