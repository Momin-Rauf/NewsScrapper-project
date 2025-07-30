"""
Test script for the News Scraper backend
"""

import json
from datetime import datetime

# Import our modules
from feeds.bbc_feed import BBCFeed
from feeds.met_police_feed import MetPoliceFeed
from feeds.govuk_feed import GOVUKFeed
from processors.content_filter import ContentFilter
from processors.location_matcher import LocationMatcher
from processors.alert_formatter import AlertFormatter
from utils.logger import setup_logger

logger = setup_logger(__name__)


def test_feeds():
    """Test feed fetching"""
    logger.info("Testing feed fetching...")
    
    feeds = [
        BBCFeed(),
        MetPoliceFeed(),
        GOVUKFeed()
    ]
    
    for feed in feeds:
        try:
            logger.info(f"Testing {feed.name}...")
            entries = feed.get_entries()
            logger.info(f"✓ {feed.name}: Got {len(entries)} entries")
            
            if entries:
                # Show first entry as example
                first_entry = entries[0]
                logger.info(f"  Example: {first_entry.get('title', 'No title')}")
            
        except Exception as e:
            logger.error(f"✗ {feed.name}: Error - {str(e)}")
        finally:
            feed.cleanup()


def test_content_filter():
    """Test content filtering"""
    logger.info("Testing content filtering...")
    
    filter_obj = ContentFilter()
    
    # Test cases
    test_cases = [
        ("Police arrest suspect in Oxford Circus stabbing", True),
        ("Weather forecast for London", False),
        ("Protest planned in Westminster tomorrow", True),
        ("New restaurant opens in Soho", False),
        ("Terror alert issued for central London", True),
        ("Traffic accident on M25", True),
    ]
    
    for text, expected in test_cases:
        result = filter_obj.contains_security_keywords(text)
        status = "✓" if result == expected else "✗"
        logger.info(f"{status} '{text}' -> {result} (expected {expected})")


def test_location_matcher():
    """Test location matching"""
    logger.info("Testing location matching...")
    
    matcher = LocationMatcher()
    
    # Test cases
    test_cases = [
        ("Police arrest suspect in Oxford Circus stabbing", "oxford circus"),
        ("Protest planned in Westminster tomorrow", "westminster"),
        ("New restaurant opens in Soho", "soho"),
        ("Traffic accident on M25 near Heathrow", "heathrow"),
        ("Weather forecast for London", None),
    ]
    
    for text, expected in test_cases:
        locations = matcher.find_locations_in_text(text)
        found = locations[0] if locations else None
        status = "✓" if found == expected else "✗"
        logger.info(f"{status} '{text}' -> {found} (expected {expected})")
        
        if found:
            lat, lon = matcher.get_coordinates(found)
            logger.info(f"  Coordinates: {lat}, {lon}")


def test_full_pipeline():
    """Test the full processing pipeline"""
    logger.info("Testing full processing pipeline...")
    
    # Create test data
    test_entries = [
        {
            'title': 'Police arrest suspect in Oxford Circus stabbing',
            'link': 'https://example.com/1',
            'description': 'A man has been arrested following a stabbing incident in Oxford Circus',
            'content': 'police arrest suspect oxford circus stabbing incident',
            'published': datetime.now(),
            'source': 'bbc',
            'type': 'news'
        },
        {
            'title': 'Protest planned in Westminster tomorrow',
            'link': 'https://example.com/2',
            'description': 'Demonstrators plan to gather in Westminster to protest new legislation',
            'content': 'protest planned westminster tomorrow demonstrators legislation',
            'published': datetime.now(),
            'source': 'bbc',
            'type': 'news'
        },
        {
            'title': 'Weather forecast for London',
            'link': 'https://example.com/3',
            'description': 'Sunny weather expected across London this weekend',
            'content': 'weather forecast london sunny weekend',
            'published': datetime.now(),
            'source': 'bbc',
            'type': 'news'
        }
    ]
    
    # Process through pipeline
    content_filter = ContentFilter()
    location_matcher = LocationMatcher()
    alert_formatter = AlertFormatter()
    
    # Step 1: Filter
    filtered = content_filter.filter_entries(test_entries)
    logger.info(f"Filtered: {len(filtered)} entries")
    
    # Step 2: Add locations
    located = location_matcher.process_entries(filtered)
    logger.info(f"Located: {len(located)} entries")
    
    # Step 3: Format alerts
    alerts = alert_formatter.format_alerts(located)
    logger.info(f"Alerts: {len(alerts)} entries")
    
    # Show results
    for alert in alerts:
        logger.info(f"Alert: {alert['title']} at {alert['location']} ({alert['lat']}, {alert['lon']})")


def main():
    """Run all tests"""
    logger.info("Starting backend tests...")
    
    try:
        test_content_filter()
        test_location_matcher()
        test_full_pipeline()
        test_feeds()
        
        logger.info("All tests completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    main() 