#!/usr/bin/env python3
"""
AI Summary Manager
Manages AI-generated project summaries with caching and storage for better performance.
"""

import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AISummaryManager:
    """Manages AI-generated SDGP (Software Development Group Project) project summaries with caching."""
    
    def __init__(self, cache_dir: str = "ai_cache"):
        """
        Initialize the summary manager.
        
        Args:
            cache_dir: Directory to store cached summaries
        """
        self.cache_dir = cache_dir
        self.summaries_file = os.path.join(cache_dir, "project_summaries.json")
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        self.summaries = {}
        self.metadata = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing summaries
        self._load_summaries()
    
    def _load_summaries(self):
        """Load existing summaries from cache."""
        try:
            if os.path.exists(self.summaries_file):
                with open(self.summaries_file, 'r', encoding='utf-8') as f:
                    self.summaries = json.load(f)
                logger.info(f"✅ Loaded {len(self.summaries)} cached summaries")
            
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info("✅ Loaded summary metadata")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to load cached summaries: {e}")
            self.summaries = {}
            self.metadata = {}
    
    def _save_summaries(self):
        """Save summaries to cache."""
        try:
            with open(self.summaries_file, 'w', encoding='utf-8') as f:
                json.dump(self.summaries, f, indent=2, ensure_ascii=False)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
                
            logger.info("✅ Saved summaries to cache")
            
        except Exception as e:
            logger.error(f"❌ Failed to save summaries: {e}")
    
    def _generate_project_hash(self, project: Dict) -> str:
        """Generate a hash for a project to detect changes."""
        basic_info = project.get('basic_info', {})
        detailed_info = project.get('detailed_info', {})
        
        # Create a hash from key project data
        hash_data = {
            'title': basic_info.get('title', ''),
            'subtitle': basic_info.get('subtitle', ''),
            'status': basic_info.get('status', ''),
            'domains': basic_info.get('domains', []),
            'projectTypes': basic_info.get('projectTypes', []),
            'year': basic_info.get('year', ''),
            'updated_at': basic_info.get('updatedAt', ''),
            'content_hash': self._hash_content(detailed_info)
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _hash_content(self, detailed_info: Dict) -> str:
        """Generate hash for detailed content."""
        if not detailed_info or 'content' not in detailed_info:
            return ""
        
        content = detailed_info['content']
        
        # Extract key content for hashing
        content_data = {
            'problem_statement': content.get('projectDetails', {}).get('problem_statement', ''),
            'solution': content.get('projectDetails', {}).get('solution', ''),
            'features': content.get('projectDetails', {}).get('features', ''),
            'team_size': len(content.get('team', [])),
            'tech_stack': [assoc.get('techStack', '') for assoc in content.get('associations', []) 
                          if assoc.get('type') == 'PROJECT_TECH']
        }
        
        content_string = json.dumps(content_data, sort_keys=True)
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def get_summary(self, project_id: str, project: Dict) -> Optional[str]:
        """
        Get cached summary for a project, or None if not cached or outdated.
        
        Args:
            project_id: Unique identifier for the project
            project: Project data dictionary
            
        Returns:
            Cached summary or None if not available/outdated
        """
        if project_id not in self.summaries:
            return None
        
        # Check if project has changed
        current_hash = self._generate_project_hash(project)
        cached_hash = self.metadata.get(project_id, {}).get('hash', '')
        
        if current_hash != cached_hash:
            logger.info(f"🔄 Project {project_id} has changed, summary needs update")
            return None
        
        return self.summaries.get(project_id)
    
    def store_summary(self, project_id: str, project: Dict, summary: str):
        """
        Store a summary for a project.
        
        Args:
            project_id: Unique identifier for the project
            project: Project data dictionary
            summary: AI-generated summary
        """
        self.summaries[project_id] = summary
        
        # Store metadata
        self.metadata[project_id] = {
            'hash': self._generate_project_hash(project),
            'created_at': datetime.now().isoformat(),
            'title': project.get('basic_info', {}).get('title', 'Unknown')
        }
        
        # Save to disk
        self._save_summaries()
    
    def get_summary_stats(self) -> Dict:
        """Get statistics about cached summaries."""
        total_summaries = len(self.summaries)
        
        # Count by creation date
        creation_dates = {}
        for metadata in self.metadata.values():
            date = metadata.get('created_at', '')[:10]  # YYYY-MM-DD
            creation_dates[date] = creation_dates.get(date, 0) + 1
        
        return {
            'total_summaries': total_summaries,
            'creation_dates': creation_dates,
            'cache_size_mb': self._get_cache_size()
        }
    
    def _get_cache_size(self) -> float:
        """Get cache size in MB."""
        try:
            if os.path.exists(self.summaries_file):
                size_bytes = os.path.getsize(self.summaries_file)
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return 0.0
    
    def clear_cache(self):
        """Clear all cached summaries."""
        self.summaries = {}
        self.metadata = {}
        
        # Remove cache files
        try:
            if os.path.exists(self.summaries_file):
                os.remove(self.summaries_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            logger.info("✅ Cache cleared")
        except Exception as e:
            logger.error(f"❌ Failed to clear cache: {e}")
    
    def export_summaries(self, output_file: str = None) -> str:
        """
        Export all summaries to a JSON file.
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ai_summaries_export_{timestamp}.json"
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'total_summaries': len(self.summaries),
            'summaries': self.summaries,
            'metadata': self.metadata
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported {len(self.summaries)} summaries to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Failed to export summaries: {e}")
            raise


def main():
    """Test the summary manager."""
    print("🧠 AI Summary Manager Test")
    print("=" * 50)
    
    # Create manager
    manager = AISummaryManager()
    
    # Get stats
    stats = manager.get_summary_stats()
    print(f"📊 Cache Statistics:")
    print(f"  Total summaries: {stats['total_summaries']}")
    print(f"  Cache size: {stats['cache_size_mb']} MB")
    
    if stats['creation_dates']:
        print(f"  Creation dates: {stats['creation_dates']}")
    
    print("\n✅ Summary manager ready!")


if __name__ == "__main__":
    main() 