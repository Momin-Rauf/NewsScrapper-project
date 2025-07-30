"""
Content filtering for security-related terms
"""

import re
from typing import List, Dict, Any
from config.settings import SECURITY_KEYWORDS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentFilter:
    """
    Filters content for security-related keywords
    """
    
    def __init__(self):
        self.keywords = SECURITY_KEYWORDS
        # Create regex patterns for better matching
        self.keyword_patterns = [re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE) 
                               for keyword in self.keywords]
    
    def contains_security_keywords(self, content: str) -> bool:
        """
        Check if content contains any security-related keywords
        
        Args:
            content: Text content to check
            
        Returns:
            True if security keywords found, False otherwise
        """
        if not content:
            return False
        
        content_lower = content.lower()
        
        # Check for exact word matches
        for pattern in self.keyword_patterns:
            if pattern.search(content):
                return True
        
        return False
    
    def get_matched_keywords(self, content: str) -> List[str]:
        """
        Get list of security keywords found in content
        
        Args:
            content: Text content to check
            
        Returns:
            List of matched keywords
        """
        if not content:
            return []
        
        matched = []
        content_lower = content.lower()
        
        for keyword in self.keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', content_lower):
                matched.append(keyword)
        
        return matched
    
    def filter_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter list of entries for security-related content
        
        Args:
            entries: List of parsed feed entries
            
        Returns:
            Filtered list containing only security-related entries
        """
        filtered_entries = []
        
        for entry in entries:
            content = entry.get('content', '')
            title = entry.get('title', '')
            
            # Check both content and title
            combined_text = f"{title} {content}"
            
            if self.contains_security_keywords(combined_text):
                # Add matched keywords to entry for debugging
                entry['matched_keywords'] = self.get_matched_keywords(combined_text)
                filtered_entries.append(entry)
                logger.debug(f"Matched entry: {entry.get('title', 'No title')} - Keywords: {entry['matched_keywords']}")
        
        logger.info(f"Filtered {len(entries)} entries down to {len(filtered_entries)} security-related entries")
        return filtered_entries 