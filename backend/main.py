"""
Main orchestrator for the News Scraper backend
"""

import time
import signal
import sys
from typing import List, Dict, Any
from datetime import datetime

# Import our modules
from feeds.bbc_feed import BBCFeed
from feeds.met_police_feed import MetPoliceFeed
from feeds.govuk_feed import GOVUKFeed
from feeds.evening_standard_feed import EveningStandardFeed
from processors.content_filter import ContentFilter
from processors.advanced_content_filter import AdvancedContentFilter
from processors.location_matcher import LocationMatcher
from processors.alert_formatter import AlertFormatter
from utils.file_handler import save_alerts, load_alerts, backup_alerts
from utils.cache_manager import CacheManager
from utils.logger import setup_logger
from config.settings import POLLING_INTERVAL, OUTPUT_FILE

logger = setup_logger(__name__)


class NewsScraper:
    """
    Main orchestrator class for the news scraper
    """
    
    def __init__(self, use_advanced_filter: bool = True):
        self.feeds = [
            BBCFeed(),
            MetPoliceFeed(),
            GOVUKFeed(),
            EveningStandardFeed()
        ]
        
        # Choose between basic and advanced content filter
        if use_advanced_filter:
            self.content_filter = AdvancedContentFilter()
            logger.info("Using advanced content filter with ML capabilities")
        else:
            self.content_filter = ContentFilter()
            logger.info("Using basic content filter")
        
        self.location_matcher = LocationMatcher()
        self.alert_formatter = AlertFormatter()
        self.cache_manager = CacheManager()
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def fetch_all_feeds(self) -> List[Dict[str, Any]]:
        """
        Fetch entries from all configured feeds
        
        Returns:
            Combined list of all feed entries
        """
        all_entries = []
        
        for feed in self.feeds:
            try:
                logger.info(f"Fetching from {feed.name}")
                entries = feed.get_entries()
                all_entries.extend(entries)
                logger.info(f"Got {len(entries)} entries from {feed.name}")
            except Exception as e:
                logger.error(f"Error fetching from {feed.name}: {str(e)}")
                continue
        
        logger.info(f"Total entries fetched: {len(all_entries)}")
        return all_entries
    
    def process_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process entries through the pipeline
        
        Args:
            entries: Raw feed entries
            
        Returns:
            Processed and formatted alerts
        """
        if not entries:
            return []
        
        # Step 1: Filter for security-related content
        logger.info("Filtering for security-related content...")
        if isinstance(self.content_filter, AdvancedContentFilter):
            filtered_entries = self.content_filter.filter_entries(entries, min_relevance=0.3)
        else:
            filtered_entries = self.content_filter.filter_entries(entries)
        
        if not filtered_entries:
            logger.info("No security-related entries found")
            return []
        
        # Step 2: Add location information
        logger.info("Adding location information...")
        located_entries = self.location_matcher.process_entries(filtered_entries)
        
        # Step 3: Format into alerts
        logger.info("Formatting alerts...")
        alerts = self.alert_formatter.format_alerts(located_entries)
        
        # Step 4: Deduplicate and sort
        logger.info("Deduplicating and sorting alerts...")
        unique_alerts = self.alert_formatter.deduplicate_alerts(alerts)
        sorted_alerts = self.alert_formatter.sort_alerts_by_time(unique_alerts)
        
        return sorted_alerts
    
    def run_single_cycle(self) -> bool:
        """
        Run a single fetch and process cycle
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("=" * 50)
            logger.info(f"Starting fetch cycle at {datetime.now()}")
            
            # Fetch from all feeds
            entries = self.fetch_all_feeds()
            
            if not entries:
                logger.warning("No entries fetched from any feed")
                return True
            
            # Process entries
            alerts = self.process_entries(entries)
            
            if not alerts:
                logger.info("No alerts generated in this cycle")
                return True
            
            # Save alerts to file
            success = save_alerts(alerts, OUTPUT_FILE)
            
            if success:
                logger.info(f"Successfully saved {len(alerts)} alerts to {OUTPUT_FILE}")
                return True
            else:
                logger.error("Failed to save alerts")
                return False
                
        except Exception as e:
            logger.error(f"Error in fetch cycle: {str(e)}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            'feeds': [],
            'cache_stats': self.cache_manager.get_stats(),
            'running': self.running
        }
        
        for feed in self.feeds:
            stats['feeds'].append(feed.get_feed_stats())
        
        return stats
    
    def cleanup_cache(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries cleared
        """
        return self.cache_manager.clear_expired()
    
    def run(self):
        """
        Main run loop with 30-second polling
        """
        logger.info("Starting News Scraper...")
        logger.info(f"Polling interval: {POLLING_INTERVAL} seconds")
        logger.info(f"Output file: {OUTPUT_FILE}")
        logger.info(f"Number of feeds: {len(self.feeds)}")
        
        self.running = True
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"Starting cycle {cycle_count}")
                
                success = self.run_single_cycle()
                
                if not success:
                    logger.warning(f"Cycle {cycle_count} failed, will retry next cycle")
                
                # Clean up cache every 10 cycles
                if cycle_count % 10 == 0:
                    cleared = self.cleanup_cache()
                    if cleared > 0:
                        logger.info(f"Cleaned up {cleared} expired cache entries")
                
                # Wait for next cycle (unless shutting down)
                if self.running:
                    logger.info(f"Waiting {POLLING_INTERVAL} seconds until next cycle...")
                    time.sleep(POLLING_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {str(e)}")
                if self.running:
                    time.sleep(POLLING_INTERVAL)
        
        # Cleanup
        logger.info("Cleaning up...")
        for feed in self.feeds:
            try:
                feed.cleanup()
            except:
                pass
        
        logger.info("News Scraper stopped")


def main():
    """Main entry point"""
    # Check command line arguments
    use_advanced_filter = True
    if len(sys.argv) > 1 and sys.argv[1] == '--basic-filter':
        use_advanced_filter = False
    
    scraper = NewsScraper(use_advanced_filter=use_advanced_filter)
    scraper.run()


if __name__ == "__main__":
    main() 