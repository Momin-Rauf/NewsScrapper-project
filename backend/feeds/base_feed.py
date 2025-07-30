"""
Abstract base class for feed handlers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import feedparser
from datetime import datetime
from utils.logger import setup_logger
from utils.rate_limiter import retry_on_failure, FeedRateLimiter
from utils.cache_manager import CacheManager
from config.settings import REQUEST_TIMEOUT

logger = setup_logger(__name__)


class BaseFeed(ABC):
    """
    Abstract base class for all feed handlers
    """
    
    def __init__(self, name: str, url: str):
        """
        Initialize feed handler
        
        Args:
            name: Name of the feed source
            url: URL of the feed
        """
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsScrapper/1.0 (London Intelligence Map)'
        })
        
        # Initialize rate limiter and cache
        self.rate_limiter = FeedRateLimiter()
        self.cache = CacheManager()
    
    @retry_on_failure(max_retries=3, base_delay=2.0, exponential_backoff=True)
    def fetch_feed(self) -> Optional[feedparser.FeedParserDict]:
        """
        Fetch and parse the RSS/Atom feed with caching and rate limiting
        
        Returns:
            Parsed feed data or None if failed
        """
        # Check cache first
        cached_data = self.cache.get(self.url)
        if cached_data:
            logger.info(f"Using cached data for {self.name}")
            return cached_data
        
        # Apply rate limiting
        self.rate_limiter.wait_for_source(self.name.lower())
        
        try:
            logger.info(f"Fetching feed from {self.name}: {self.url}")
            response = self.session.get(self.url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warnings for {self.name}: {feed.bozo_exception}")
            
            # Cache the parsed feed (cache for 5 minutes)
            self.cache.set(self.url, feed, ttl=300)
            
            logger.info(f"Successfully fetched {len(feed.entries)} entries from {self.name}")
            return feed
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch feed from {self.name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching feed from {self.name}: {str(e)}")
            return None
    
    @abstractmethod
    def parse_entries(self, feed: feedparser.FeedParserDict) -> List[Dict[str, Any]]:
        """
        Parse feed entries into standardized format
        
        Args:
            feed: Parsed feed data
            
        Returns:
            List of parsed entries
        """
        pass
    
    def get_entries(self) -> List[Dict[str, Any]]:
        """
        Main method to fetch and parse feed entries
        
        Returns:
            List of parsed entries
        """
        feed = self.fetch_feed()
        if feed is None:
            return []
        
        return self.parse_entries(feed)
    
    def cleanup(self):
        """
        Clean up resources
        """
        self.session.close()
    
    def get_feed_stats(self) -> Dict[str, Any]:
        """
        Get statistics about this feed
        
        Returns:
            Dictionary with feed statistics
        """
        cache_stats = self.cache.get_stats()
        return {
            'name': self.name,
            'url': self.url,
            'cache_stats': cache_stats
        } 