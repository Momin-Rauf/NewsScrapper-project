"""
Configuration settings for the News Scraper backend
"""

# Polling settings
POLLING_INTERVAL = 30  # seconds
REQUEST_TIMEOUT = 10   # seconds

# Feed URLs
FEED_URLS = {
    'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
    'met_police': 'https://news.met.police.uk/news',
    'govuk': 'https://www.gov.uk/foreign-travel-advice.atom'
}

# Security-related keywords to filter for
SECURITY_KEYWORDS = [
    'stabbing', 'knife', 'attack', 'assault', 'murder', 'homicide',
    'protest', 'demonstration', 'riot', 'unrest', 'disorder',
    'terror', 'terrorism', 'bomb', 'explosion', 'fire',
    'shooting', 'gun', 'firearm', 'weapon',
    'emergency', 'evacuation', 'lockdown', 'alert',
    'crime', 'criminal', 'arrest', 'police', 'officer',
    'incident', 'accident', 'collision', 'crash'
]

# Output file path
OUTPUT_FILE = 'alerts.json'

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Default coordinates (central London) - kept for reference but not used
DEFAULT_LAT = 51.5074
DEFAULT_LON = -0.1278 