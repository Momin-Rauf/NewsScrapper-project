"""
Evening Standard RSS feed handler
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from feeds.base_feed import BaseFeed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EveningStandardFeed(BaseFeed):
    """
    Handler for Evening Standard RSS feed
    """
    
    def __init__(self):
        super().__init__("Evening Standard", "https://www.standard.co.uk/rss")
    
    def parse_entries(self, feed) -> List[Dict[str, Any]]:
        """
        Parse Evening Standard RSS entries
        
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
                elif 'updated' in entry:
                    try:
                        pub_date = date_parser.parse(entry.updated)
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
                    'source': 'evening_standard',
                    'type': 'news'
                }
                
                entries.append(parsed_entry)
                
            except Exception as e:
                logger.error(f"Error parsing Evening Standard entry: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(entries)} entries from Evening Standard")
        return entries 