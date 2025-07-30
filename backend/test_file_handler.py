#!/usr/bin/env python3
"""
Test script for file handler
"""

from utils.file_handler import save_alerts
from config.settings import OUTPUT_FILE

def test_save_alerts():
    """Test saving alerts to file"""
    test_alerts = [
        {
            'type': 'crime',
            'location': 'Central London',
            'time': '2025-07-29T19:07:00',
            'lat': 51.5074,
            'lon': -0.1278,
            'title': 'Test Alert',
            'link': 'https://example.com',
            'source': 'test',
            'description': 'This is a test alert',
            'matched_keywords': ['test']
        }
    ]
    
    print(f"Testing save_alerts with filepath: '{OUTPUT_FILE}'")
    success = save_alerts(test_alerts, OUTPUT_FILE)
    
    if success:
        print(f"✅ Successfully saved test alerts to {OUTPUT_FILE}")
    else:
        print(f"❌ Failed to save test alerts to {OUTPUT_FILE}")

if __name__ == "__main__":
    test_save_alerts() 