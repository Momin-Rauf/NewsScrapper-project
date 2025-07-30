"""
GOV.UK Atom feed handler
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from feeds.base_feed import BaseFeed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GOVUKFeed(BaseFeed):
    """
    Handler for GOV.UK Atom feeds
    """
    
    def __init__(self):
        super().__init__("GOV.UK", "https://www.gov.uk/foreign-travel-advice.atom")
    
    def parse_entries(self, feed) -> List[Dict[str, Any]]:
        """
        Parse GOV.UK Atom feed entries
        
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
                    'source': 'govuk',
                    'type': 'government'
                }
                
                entries.append(parsed_entry)
                
            except Exception as e:
                logger.error(f"Error parsing GOV.UK entry: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(entries)} entries from GOV.UK")
        return entries 