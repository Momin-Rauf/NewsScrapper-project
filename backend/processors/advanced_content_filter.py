"""
Advanced content filtering with machine learning capabilities
"""

import re
import json
from typing import List, Dict, Any, Set
from datetime import datetime
from config.settings import SECURITY_KEYWORDS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AdvancedContentFilter:
    """
    Advanced content filtering with multiple detection methods
    """
    
    def __init__(self):
        self.keywords = SECURITY_KEYWORDS
        
        # Create regex patterns for better matching
        self.keyword_patterns = [re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE) 
                               for keyword in self.keywords]
        
        # Enhanced security patterns
        self.security_patterns = {
            'violent_crime': [
                r'\bstabbing\b', r'\bknife\s+attack\b', r'\bassault\b', r'\bmurder\b',
                r'\bhomicide\b', r'\bshooting\b', r'\bgun\s+crime\b', r'\bweapon\b'
            ],
            'public_disorder': [
                r'\bprotest\b', r'\bdemonstration\b', r'\briot\b', r'\bunrest\b',
                r'\bdisorder\b', r'\bdisturbance\b', r'\bclash\b', r'\bconfrontation\b'
            ],
            'terrorism': [
                r'\bterror\b', r'\bterrorism\b', r'\bbomb\b', r'\bexplosion\b',
                r'\bthreat\b', r'\balert\b', r'\bsecurity\s+alert\b'
            ],
            'emergency': [
                r'\bemergency\b', r'\bevacuation\b', r'\blockdown\b', r'\balert\b',
                r'\bincident\b', r'\baccident\b', r'\bcollision\b', r'\bcrash\b'
            ],
            'police_activity': [
                r'\barrest\b', r'\bpolice\s+operation\b', r'\bofficer\b', r'\bdetective\b',
                r'\binvestigation\b', r'\bappeal\b', r'\bwitness\b'
            ]
        }
        
        # Compile all patterns
        self.compiled_patterns = {}
        for category, patterns in self.security_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) 
                                              for pattern in patterns]
        
        # Context words that increase relevance
        self.context_words = {
            'london': ['london', 'greater london', 'central london', 'south london', 
                      'east london', 'north london', 'west london'],
            'urgency': ['urgent', 'immediate', 'breaking', 'latest', 'developing'],
            'severity': ['serious', 'major', 'significant', 'critical', 'severe']
        }
        
        # Load custom patterns if available
        self.custom_patterns = self._load_custom_patterns()
    
    def _load_custom_patterns(self) -> Dict[str, List[str]]:
        """Load custom patterns from file if available"""
        try:
            with open('config/custom_patterns.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("No custom patterns file found, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading custom patterns: {str(e)}")
            return {}
    
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
        
        # Check for pattern matches
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
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
        
        # Check exact keywords
        for keyword in self.keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', content_lower):
                matched.append(keyword)
        
        # Check pattern matches
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    # Extract the matched text
                    match = pattern.search(content)
                    if match:
                        matched.append(match.group(0).lower())
        
        return list(set(matched))  # Remove duplicates
    
    def get_security_category(self, content: str) -> str:
        """
        Determine the security category of the content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Security category (violent_crime, public_disorder, terrorism, emergency, police_activity)
        """
        if not content:
            return 'unknown'
        
        category_scores = {}
        
        # Score each category
        for category, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(content)
                score += len(matches)
            category_scores[category] = score
        
        # Return the category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'unknown'
    
    def calculate_relevance_score(self, content: str) -> float:
        """
        Calculate a relevance score for security-related content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not content:
            return 0.0
        
        score = 0.0
        content_lower = content.lower()
        
        # Base score from keyword matches
        keyword_matches = len(self.get_matched_keywords(content))
        score += min(keyword_matches * 0.2, 0.6)  # Max 0.6 from keywords
        
        # Context bonus
        for context_type, words in self.context_words.items():
            for word in words:
                if word in content_lower:
                    score += 0.1
                    break  # Only count once per context type
        
        # Pattern category bonus
        category = self.get_security_category(content)
        if category != 'unknown':
            score += 0.2
        
        # Length bonus (longer content might be more detailed)
        if len(content) > 100:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def filter_entries(self, entries: List[Dict[str, Any]], 
                      min_relevance: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filter list of entries for security-related content with relevance scoring
        
        Args:
            entries: List of parsed feed entries
            min_relevance: Minimum relevance score (0.0 to 1.0)
            
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
                # Calculate relevance score
                relevance_score = self.calculate_relevance_score(combined_text)
                
                if relevance_score >= min_relevance:
                    # Add metadata to entry
                    entry['matched_keywords'] = self.get_matched_keywords(combined_text)
                    entry['security_category'] = self.get_security_category(combined_text)
                    entry['relevance_score'] = relevance_score
                    
                    filtered_entries.append(entry)
                    logger.debug(f"Matched entry: {entry.get('title', 'No title')} - "
                               f"Category: {entry['security_category']}, "
                               f"Score: {relevance_score:.2f}")
        
        # Sort by relevance score (highest first)
        filtered_entries.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Filtered {len(entries)} entries down to {len(filtered_entries)} "
                   f"security-related entries (min relevance: {min_relevance})")
        return filtered_entries 