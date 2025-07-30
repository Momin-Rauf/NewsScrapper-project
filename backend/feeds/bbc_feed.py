"""
BBC News RSS feed handler
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from feeds.base_feed import BaseFeed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BBCFeed(BaseFeed):
    """
    Handler for BBC News RSS feed
    """
    
    def __init__(self):
        super().__init__("BBC News", "https://feeds.bbci.co.uk/news/rss.xml")
    
    def parse_entries(self, feed) -> List[Dict[str, Any]]:
        """
        Parse BBC News RSS entries
        
        Args:
            feed: Parsed feed data
            
        Returns:
            List of parsed entries
        """
        entries = []
        
        for entry in feed.entries:
            try:
                # Extract basic information
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                description = entry.get('summary', '')
                
                # Parse publication date
                pub_date = None
                if 'published' in entry:
                    try:
                        pub_date = date_parser.parse(entry.published)
                    except:
                        pub_date = datetime.now()
                else:
                    pub_date = datetime.now()
                
                # Combine title and description for content analysis
                content = f"{title} {description}".lower()
                
                # Create entry
                parsed_entry = {
                    'title': title,
                    'link': link,
                    'description': description,
                    'content': content,
                    'published': pub_date,
                    'source': 'bbc',
                    'type': 'news'
                }
                
                entries.append(parsed_entry)
                
            except Exception as e:
                logger.error(f"Error parsing BBC entry: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(entries)} entries from BBC News")
        return entries 