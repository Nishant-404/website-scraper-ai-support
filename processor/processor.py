"""Main data processor for cleaning and structuring scraped content"""

import os
import json
from typing import List, Dict
from .cleaner import ContentCleaner, CleanedContent
from .qa_generator import QAGenerator, QAPair

class DataProcessor:
    def __init__(self, company_name: str, data_dir: str = "scraped_data"):
        self.company_name = company_name
        self.data_dir = data_dir
        self.company_folder = os.path.join(data_dir, company_name)
        self.cleaner = ContentCleaner()
        self.qa_generator = QAGenerator()
    
    def get_latest_raw_data_file(self) -> str:
        """Get the most recent raw data file for the company"""
        raw_data_dir = os.path.join(self.company_folder, 'raw_data')
        
        if not os.path.exists(raw_data_dir):
            raise FileNotFoundError(f"No raw data found for {self.company_name}")
        
        raw_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
        if not raw_files:
            raise FileNotFoundError(f"No JSON files found in {raw_data_dir}")
        
        # Get the most recent file
        latest_file = sorted(raw_files)[-1]
        return os.path.join(raw_data_dir, latest_file)
    
    def process_company_data(self) -> Dict:
        """Process all data for a company"""
        print(f"🔄 Processing data for {self.company_name}")
        print("=" * 50)
        
        # Step 1: Load and clean raw data
        print("Step 1: Cleaning raw scraped data...")
        raw_data_file = self.get_latest_raw_data_file()
        cleaned_contents = self.cleaner.clean_company_data(raw_data_file)
        
        if not cleaned_contents:
            print("❌ No content could be cleaned!")
            return {}
        
        # Step 2: Save cleaned data
        print("Step 2: Saving cleaned data...")
        processed_dir = os.path.join(self.company_folder, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        cleaned_file = os.path.join(processed_dir, 'cleaned_content.json')
        self.save_cleaned_content(cleaned_contents, cleaned_file)
        
        # Step 3: Generate Q&A pairs
        print("Step 3: Generating Q&A pairs...")
        qa_pairs = self.qa_generator.generate_all_qa_pairs(cleaned_contents)
        
        qa_dir = os.path.join(self.company_folder, 'qa_pairs')
        os.makedirs(qa_dir, exist_ok=True)
        
        qa_file = os.path.join(qa_dir, 'qa_pairs.json')
        self.qa_generator.save_qa_pairs(qa_pairs, qa_file)
        
        # Step 4: Generate summary statistics
        print("Step 4: Generating summary statistics...")
        stats = self.generate_processing_stats(cleaned_contents, qa_pairs)
        
        stats_file = os.path.join(processed_dir, 'processing_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processing complete! Generated {len(qa_pairs)} Q&A pairs")
        return stats
    
    def save_cleaned_content(self, contents: List[CleanedContent], output_file: str):
        """Save cleaned content to JSON file"""
        cleaned_data = []
        
        for content in contents:
            cleaned_data.append({
                'title': content.title,
                'content': content.content,
                'category': content.category,
                'url': content.url,
                'keywords': content.keywords,
                'content_type': content.content_type
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(contents)} cleaned pages to {output_file}")
    
    def generate_processing_stats(self, contents: List[CleanedContent], qa_pairs: List[QAPair]) -> Dict:
        """Generate processing statistics"""
        # Content type distribution
        content_types = {}
        categories = {}
        total_content_length = 0
        
        for content in contents:
            # Count content types
            content_type = content.content_type
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Count categories
            category = content.category
            categories[category] = categories.get(category, 0) + 1
            
            # Total content length
            total_content_length += len(content.content)
        
        # Q&A statistics
        qa_categories = {}
        high_confidence_qa = 0
        
        for qa in qa_pairs:
            qa_cat = qa.category
            qa_categories[qa_cat] = qa_categories.get(qa_cat, 0) + 1
            
            if qa.confidence >= 0.8:
                high_confidence_qa += 1
        
        stats = {
            'company_name': self.company_name,
            'processing_summary': {
                'total_pages_processed': len(contents),
                'total_qa_pairs_generated': len(qa_pairs),
                'high_confidence_qa_pairs': high_confidence_qa,
                'total_content_length': total_content_length,
                'average_content_length': total_content_length // len(contents) if contents else 0
            },
            'content_distribution': {
                'by_type': content_types,
                'by_category': categories
            },
            'qa_distribution': {
                'by_category': qa_categories,
                'confidence_breakdown': {
                    'high (0.8+)': high_confidence_qa,
                    'medium (0.6-0.8)': len([qa for qa in qa_pairs if 0.6 <= qa.confidence < 0.8]),
                    'low (<0.6)': len([qa for qa in qa_pairs if qa.confidence < 0.6])
                }
            }
        }
        
        return stats
    
    def print_processing_summary(self, stats: Dict):
        """Print a nice summary of processing results"""
        print("\n📊 Processing Summary")
        print("=" * 40)
        
        summary = stats['processing_summary']
        print(f"Company: {stats['company_name']}")
        print(f"Pages processed: {summary['total_pages_processed']}")
        print(f"Q&A pairs generated: {summary['total_qa_pairs_generated']}")
        print(f"High confidence Q&A: {summary['high_confidence_qa_pairs']}")
        print(f"Total content: {summary['total_content_length']:,} characters")
        
        print("\n📂 Content by Type:")
        for content_type, count in stats['content_distribution']['by_type'].items():
            print(f"  {content_type}: {count}")
        
        print("\n🏷️ Content by Category:")
        for category, count in sorted(stats['content_distribution']['by_category'].items()):
            print(f"  {category}: {count}")
        
        print("\n❓ Q&A by Category:")
        for category, count in sorted(stats['qa_distribution']['by_category'].items()):
            print(f"  {category}: {count} pairs")
        
        print("\n🎯 Q&A Confidence Levels:")
        for level, count in stats['qa_distribution']['confidence_breakdown'].items():
            print(f"  {level}: {count} pairs")