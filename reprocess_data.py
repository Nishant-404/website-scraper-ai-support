#!/usr/bin/env python3
"""
Advanced data reprocessing with better cleaning and Q&A generation
Usage: python reprocess_data.py <company_name> [--use-api] [--api-key YOUR_KEY]
"""

import sys
import os
import json
import argparse
from processor.advanced_cleaner import AdvancedContentCleaner, EnhancedContent
from processor.smart_qa_generator import SmartQAGenerator, SmartQAPair

class AdvancedDataProcessor:
    def __init__(self, company_name: str, use_api: bool = False, api_key: str = None):
        self.company_name = company_name
        self.data_dir = "scraped_data"
        self.company_folder = os.path.join(self.data_dir, company_name)
        self.cleaner = AdvancedContentCleaner()
        self.qa_generator = SmartQAGenerator(use_api=use_api, api_key=api_key)
    
    def get_latest_raw_data_file(self) -> str:
        """Get the most recent raw data file"""
        raw_data_dir = os.path.join(self.company_folder, 'raw_data')
        
        if not os.path.exists(raw_data_dir):
            raise FileNotFoundError(f"No raw data found for {self.company_name}")
        
        raw_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
        if not raw_files:
            raise FileNotFoundError(f"No JSON files found in {raw_data_dir}")
        
        latest_file = sorted(raw_files)[-1]
        return os.path.join(raw_data_dir, latest_file)
    
    def load_raw_data(self, raw_file: str) -> List[Dict]:
        """Load raw scraped data"""
        with open(raw_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('pages', [])
    
    def advanced_clean_data(self, raw_pages: List[Dict]) -> List[EnhancedContent]:
        """Clean data with advanced processing"""
        enhanced_contents = []
        
        print(f"Advanced cleaning of {len(raw_pages)} pages...")
        
        for i, page in enumerate(raw_pages):
            try:
                title = page.get('title', '').strip()
                content = page.get('content', '').strip()
                url = page.get('url', '')
                
                # Skip if no meaningful content
                if not title and not content:
                    continue
                
                if len(content) < 50:  # Skip very short content
                    continue
                
                # Advanced cleaning and enhancement
                enhanced = self.cleaner.clean_and_enhance_content(content, title, url)
                
                # Only keep high-quality content
                if enhanced.quality_score > 0.2:
                    enhanced_contents.append(enhanced)
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(raw_pages)} pages...")
                    
            except Exception as e:
                print(f"Error processing page {i}: {e}")
                continue
        
        print(f"Successfully enhanced {len(enhanced_contents)} pages")
        return enhanced_contents
    
    def reprocess_company_data(self) -> Dict:
        """Reprocess all data with advanced methods"""
        print(f"🔄 Advanced reprocessing for {self.company_name}")
        print("=" * 60)
        
        # Step 1: Load raw data
        print("Step 1: Loading raw scraped data...")
        raw_data_file = self.get_latest_raw_data_file()
        raw_pages = self.load_raw_data(raw_data_file)
        
        # Step 2: Advanced cleaning
        print("Step 2: Advanced content cleaning and enhancement...")
        enhanced_contents = self.advanced_clean_data(raw_pages)
        
        if not enhanced_contents:
            print("❌ No content could be enhanced!")
            return {}
        
        # Step 3: Save enhanced content
        print("Step 3: Saving enhanced content...")
        processed_dir = os.path.join(self.company_folder, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        enhanced_file = os.path.join(processed_dir, 'enhanced_content.json')
        self.save_enhanced_content(enhanced_contents, enhanced_file)
        
        # Step 4: Generate smart Q&A pairs
        print("Step 4: Generating smart Q&A pairs...")
        smart_qa_pairs = self.qa_generator.generate_all_smart_qa_pairs(enhanced_contents)
        
        qa_dir = os.path.join(self.company_folder, 'qa_pairs')
        os.makedirs(qa_dir, exist_ok=True)
        
        smart_qa_file = os.path.join(qa_dir, 'smart_qa_pairs.json')
        self.qa_generator.save_smart_qa_pairs(smart_qa_pairs, smart_qa_file)
        
        # Step 5: Generate statistics
        print("Step 5: Generating advanced statistics...")
        stats = self.generate_advanced_stats(enhanced_contents, smart_qa_pairs)
        
        stats_file = os.path.join(processed_dir, 'advanced_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Advanced reprocessing complete! Generated {len(smart_qa_pairs)} smart Q&A pairs")
        return stats
    
    def save_enhanced_content(self, contents: List[EnhancedContent], output_file: str):
        """Save enhanced content to JSON file"""
        enhanced_data = []
        
        for content in contents:
            enhanced_data.append({
                'title': content.title,
                'content': content.content,
                'category': content.category,
                'url': content.url,
                'keywords': content.keywords,
                'content_type': content.content_type,
                'structured_data': content.structured_data,
                'quality_score': content.quality_score
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(contents)} enhanced pages to {output_file}")
    
    def generate_advanced_stats(self, contents: List[EnhancedContent], qa_pairs: List[SmartQAPair]) -> Dict:
        """Generate advanced processing statistics"""
        # Content statistics
        content_types = {}
        categories = {}
        quality_distribution = {'high': 0, 'medium': 0, 'low': 0}
        total_content_length = 0
        
        for content in contents:
            # Count content types
            content_type = content.content_type
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Count categories
            category = content.category
            categories[category] = categories.get(category, 0) + 1
            
            # Quality distribution
            if content.quality_score >= 0.7:
                quality_distribution['high'] += 1
            elif content.quality_score >= 0.4:
                quality_distribution['medium'] += 1
            else:
                quality_distribution['low'] += 1
            
            total_content_length += len(content.content)
        
        # Q&A statistics
        qa_categories = {}
        answer_types = {}
        high_confidence_qa = 0
        
        for qa in qa_pairs:
            qa_cat = qa.category
            qa_categories[qa_cat] = qa_categories.get(qa_cat, 0) + 1
            
            answer_type = qa.answer_type
            answer_types[answer_type] = answer_types.get(answer_type, 0) + 1
            
            if qa.confidence >= 0.8:
                high_confidence_qa += 1
        
        stats = {
            'company_name': self.company_name,
            'processing_summary': {
                'total_pages_enhanced': len(contents),
                'total_smart_qa_pairs': len(qa_pairs),
                'high_confidence_qa_pairs': high_confidence_qa,
                'total_content_length': total_content_length,
                'average_content_length': total_content_length // len(contents) if contents else 0,
                'average_quality_score': sum(c.quality_score for c in contents) / len(contents) if contents else 0
            },
            'content_distribution': {
                'by_type': content_types,
                'by_category': categories,
                'by_quality': quality_distribution
            },
            'qa_distribution': {
                'by_category': qa_categories,
                'by_answer_type': answer_types,
                'confidence_breakdown': {
                    'high (0.8+)': high_confidence_qa,
                    'medium (0.6-0.8)': len([qa for qa in qa_pairs if 0.6 <= qa.confidence < 0.8]),
                    'low (<0.6)': len([qa for qa in qa_pairs if qa.confidence < 0.6])
                }
            }
        }
        
        return stats
    
    def print_advanced_summary(self, stats: Dict):
        """Print advanced processing summary"""
        print("\n📊 Advanced Processing Summary")
        print("=" * 50)
        
        summary = stats['processing_summary']
        print(f"Company: {stats['company_name']}")
        print(f"Pages enhanced: {summary['total_pages_enhanced']}")
        print(f"Smart Q&A pairs: {summary['total_smart_qa_pairs']}")
        print(f"High confidence Q&A: {summary['high_confidence_qa_pairs']}")
        print(f"Average quality score: {summary['average_quality_score']:.2f}")
        print(f"Total content: {summary['total_content_length']:,} characters")
        
        print("\n📂 Content Quality Distribution:")
        quality_dist = stats['content_distribution']['by_quality']
        for quality, count in quality_dist.items():
            print(f"  {quality}: {count}")
        
        print("\n🏷️ Content by Category:")
        for category, count in sorted(stats['content_distribution']['by_category'].items()):
            print(f"  {category}: {count}")
        
        print("\n❓ Smart Q&A by Answer Type:")
        for atype, count in sorted(stats['qa_distribution']['by_answer_type'].items()):
            print(f"  {atype}: {count} pairs")

def main():
    parser = argparse.ArgumentParser(description='Advanced data reprocessing')
    parser.add_argument('company_name', help='Company name to reprocess')
    parser.add_argument('--use-api', action='store_true', help='Use API for answer enhancement')
    parser.add_argument('--api-key', help='API key for enhancement service')
    
    args = parser.parse_args()
    
    try:
        processor = AdvancedDataProcessor(
            args.company_name, 
            use_api=args.use_api, 
            api_key=args.api_key
        )
        stats = processor.reprocess_company_data()
        processor.print_advanced_summary(stats)
        
        print(f"\n🎉 Advanced reprocessing complete for {args.company_name}!")
        print("Files created:")
        print(f"  📄 Enhanced content: scraped_data/{args.company_name}/processed/enhanced_content.json")
        print(f"  ❓ Smart Q&A pairs: scraped_data/{args.company_name}/qa_pairs/smart_qa_pairs.json")
        print(f"  📊 Advanced stats: scraped_data/{args.company_name}/processed/advanced_stats.json")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure you have scraped data for this company first!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()