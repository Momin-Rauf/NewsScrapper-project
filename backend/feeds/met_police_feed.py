"""
Met Police news feed handler
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from feeds.base_feed import BaseFeed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MetPoliceFeed(BaseFeed):
    """
    Handler for Met Police news website
    """
    
    def __init__(self):
        super().__init__("Met Police", "https://news.met.police.uk/news")
    
    def fetch_feed(self):
        """
        Override to fetch HTML instead of RSS
        """
        try:
            logger.info(f"Fetching news from {self.name}: {self.url}")
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            logger.info(f"Successfully fetched Met Police news page")
            return soup
            
        except Exception as e:
            logger.error(f"Failed to fetch Met Police news: {str(e)}")
            return None
    
    def parse_entries(self, soup) -> List[Dict[str, Any]]:
        """
        Parse Met Police news HTML with improved parsing
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of parsed entries
        """
        entries = []
        
        try:
            # Multiple selectors for different page layouts
            article_selectors = [
                'article.news-item',
                'div.news-item',
                'div.article',
                'div.news-article',
                'div[class*="news"]',
                'div[class*="article"]',
                'div[class*="story"]',
                'li.news-item',
                'div.news-list-item'
            ]
            
            articles = []
            for selector in article_selectors:
                articles = soup.select(selector)
                if articles:
                    logger.info(f"Found {len(articles)} articles using selector: {selector}")
                    break
            
            # Fallback: look for any divs with links that might be news
            if not articles:
                articles = soup.find_all('div', class_=re.compile(r'item|entry|news|article'))
                logger.info(f"Fallback: Found {len(articles)} potential articles")
            
            for article in articles[:30]:  # Increased limit
                try:
                    entry = self._parse_single_article(article)
                    if entry:
                        entries.append(entry)
                        
                except Exception as e:
                    logger.error(f"Error parsing Met Police article: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(entries)} entries from Met Police")
            
        except Exception as e:
            logger.error(f"Error parsing Met Police page: {str(e)}")
        
        return entries
    
    def _parse_single_article(self, article) -> Dict[str, Any]:
        """
        Parse a single article element
        """
        # Try multiple title selectors
        title_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5',
            '.title', '.headline', '.news-title',
            'a[href*="/news/"]', 'a.news-link'
        ]
        
        title = ""
        link = ""
        
        # Find title and link
        for selector in title_selectors:
            title_elem = article.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title:
                    # Try to get link from the same element or parent
                    if title_elem.name == 'a':
                        link = title_elem.get('href', '')
                    else:
                        link_elem = title_elem.find_parent('a') or title_elem.find('a')
                        if link_elem:
                            link = link_elem.get('href', '')
                    break
        
        if not title:
            return None
        
        # Clean up link
        if link and not link.startswith('http'):
            link = f"https://news.met.police.uk{link}"
        
        # Find description/summary with multiple selectors
        desc_selectors = [
            '.summary', '.description', '.excerpt', '.content',
            '.news-summary', '.article-summary', '.news-content',
            'p:not(:has(a))', 'div[class*="summary"]', 'div[class*="content"]'
        ]
        
        description = ""
        for selector in desc_selectors:
            desc_elem = article.select_one(selector)
            if desc_elem:
                desc_text = desc_elem.get_text().strip()
                if desc_text and len(desc_text) > 10:  # Minimum meaningful length
                    description = desc_text
                    break
        
        # Extract date if available
        pub_date = self._extract_date(article)
        
        # Combine content for analysis
        content = f"{title} {description}".lower()
        
        # Create entry
        parsed_entry = {
            'title': title,
            'link': link,
            'description': description,
            'content': content,
            'published': pub_date,
            'source': 'met_police',
            'type': 'police'
        }
        
        return parsed_entry
    
    def _extract_date(self, article) -> datetime:
        """
        Extract publication date from article
        """
        # Try multiple date selectors
        date_selectors = [
            '.date', '.published', '.news-date', '.article-date',
            '.timestamp', '.time', '[datetime]', '.meta-date'
        ]
        
        for selector in date_selectors:
            date_elem = article.select_one(selector)
            if date_elem:
                # Try to get datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    try:
                        from dateutil import parser as date_parser
                        return date_parser.parse(datetime_attr)
                    except:
                        pass
                
                # Try to parse text content
                date_text = date_elem.get_text().strip()
                if date_text:
                    try:
                        from dateutil import parser as date_parser
                        return date_parser.parse(date_text)
                    except:
                        pass
        
        # Return current time if no date found
        return datetime.now()
    
    def get_entries(self) -> List[Dict[str, Any]]:
        """
        Override to handle HTML instead of RSS
        """
        soup = self.fetch_feed()
        if soup is None:
            return []
        
        return self.parse_entries(soup) 