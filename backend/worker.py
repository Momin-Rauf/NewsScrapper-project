"""
Worker script for running the news scraper on Render
Optimized for free tier with reduced polling frequency
"""

import os
import time
import signal
import sys
from datetime import datetime
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import NewsScraper
from utils.logger import setup_logger

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = setup_logger(__name__)

class RenderWorker:
    def __init__(self):
        self.scraper = None
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        if self.scraper:
            self.scraper.running = False
    
    def run(self):
        """Main worker loop optimized for Render free tier"""
        logger.info("Starting Render Worker for News Scraper...")
        logger.info(f"Environment: {os.environ.get('RENDER_ENVIRONMENT', 'unknown')}")
        
        # Initialize scraper with basic filter to reduce resource usage
        try:
            self.scraper = NewsScraper(use_advanced_filter=False)
            logger.info("News Scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            return
        
        self.running = True
        cycle_count = 0
        
        # Render free tier has limitations, so we use longer intervals
        # and run fewer cycles to stay within limits
        polling_interval = 300  # 5 minutes instead of 30 seconds
        max_cycles_per_hour = 10  # Limit cycles to stay within free tier
        
        logger.info(f"Using polling interval: {polling_interval} seconds")
        logger.info(f"Max cycles per hour: {max_cycles_per_hour}")
        
        while self.running:
            try:
                cycle_count += 1
                current_hour = datetime.now().hour
                
                logger.info(f"Starting cycle {cycle_count} at {datetime.now()}")
                
                # Run a single cycle
                success = self.scraper.run_single_cycle()
                
                if success:
                    logger.info(f"Cycle {cycle_count} completed successfully")
                else:
                    logger.warning(f"Cycle {cycle_count} failed")
                
                # Check if we've hit the hourly limit
                if cycle_count >= max_cycles_per_hour:
                    logger.info(f"Reached hourly limit ({max_cycles_per_hour} cycles), waiting for next hour...")
                    # Wait until the next hour
                    time.sleep(3600)  # Wait 1 hour
                    cycle_count = 0
                else:
                    # Wait for next cycle
                    logger.info(f"Waiting {polling_interval} seconds until next cycle...")
                    time.sleep(polling_interval)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}")
                if self.running:
                    time.sleep(polling_interval)
        
        # Cleanup
        logger.info("Worker shutting down...")
        if self.scraper:
            try:
                self.scraper.cleanup_cache()
                logger.info("Cache cleanup completed")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        logger.info("Render Worker stopped")

def main():
    """Main entry point for the worker"""
    worker = RenderWorker()
    worker.run()

if __name__ == "__main__":
    main() 