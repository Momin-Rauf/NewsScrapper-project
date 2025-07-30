# News Scraper Backend

A Python backend system that polls multiple news sources for security-related incidents in London and generates alerts for display on an interactive map.

## Features

- **Multi-source polling**: BBC News RSS, Met Police news, GOV.UK alerts
- **Content filtering**: Automatically filters for security-related keywords
- **Location matching**: Maps London locations to coordinates
- **Real-time processing**: Updates every 30 seconds
- **Structured output**: Generates JSON alerts for frontend consumption

## Project Structure

```
backend/
├── main.py                 # Main orchestrator script
├── test_backend.py         # Test script
├── requirements.txt        # Python dependencies
├── config/
│   ├── settings.py         # Configuration constants
│   └── locations.py        # London location mappings
├── feeds/
│   ├── base_feed.py        # Abstract base class for feeds
│   ├── bbc_feed.py         # BBC News RSS handler
│   ├── met_police_feed.py  # Met Police news handler
│   └── govuk_feed.py       # GOV.UK Atom feed handler
├── processors/
│   ├── content_filter.py   # Security term filtering
│   ├── location_matcher.py # Location extraction & geocoding
│   └── alert_formatter.py  # JSON structure formatting
└── utils/
    ├── logger.py           # Logging configuration
    └── file_handler.py     # alerts.json file operations
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the system**:
   ```bash
   python test_backend.py
   ```

3. **Run the scraper**:
   ```bash
   python main.py
   ```

## Configuration

### Settings (`config/settings.py`)
- `POLLING_INTERVAL`: How often to poll feeds (default: 30 seconds)
- `SECURITY_KEYWORDS`: List of keywords to filter for
- `OUTPUT_FILE`: Where to save alerts.json

### Locations (`config/locations.py`)
- Comprehensive mapping of London areas to coordinates
- Includes major areas, transport hubs, landmarks, etc.

## Output Format

The system generates `alerts.json` with the following structure:

```json
[
  {
    "type": "crime",
    "location": "Oxford Circus",
    "time": "2025-01-15T14:33:00",
    "lat": 51.5154,
    "lon": -0.1411,
    "title": "Stabbing near Oxford Circus",
    "link": "https://news.met.police.uk/...",
    "source": "met_police",
    "description": "Police are investigating...",
    "matched_keywords": ["stabbing", "police"]
  }
]
```

## Alert Types

- **crime**: Police incidents, arrests, criminal activity
- **news**: General news with security implications
- **emergency**: Government alerts, public safety notices

## Monitoring

The system provides detailed logging:
- Feed fetch status
- Content filtering results
- Location matching
- File save operations
- Error handling

## Error Handling

- Graceful handling of network failures
- Continues running if individual feeds fail
- Automatic retry on next cycle
- Comprehensive error logging

## Testing

Run the test script to verify all components:

```bash
python test_backend.py
```

This will test:
- Feed fetching from all sources
- Content filtering logic
- Location matching
- Full processing pipeline

## Deployment

The backend can run on:
- Local development machine
- VPS/server
- Cloud platforms (with minor modifications)

For production deployment, consider:
- Running as a system service
- Setting up monitoring
- Implementing backup strategies
- Adding rate limiting for feeds 