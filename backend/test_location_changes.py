#!/usr/bin/env python3
"""
Test script to verify location matching changes
"""

from processors.location_matcher import LocationMatcher
from utils.logger import setup_logger

logger = setup_logger(__name__)

def test_location_matching():
    """Test that location matcher doesn't use defaults when no match found"""
    
    matcher = LocationMatcher()
    
    # Test cases
    test_cases = [
        # Should find location
        ("Police arrest suspect in Oxford Circus stabbing", "oxford circus"),
        ("Protest planned in Westminster tomorrow", "westminster"),
        
        # Should NOT find location (no London area mentioned)
        ("Weather forecast for the weekend", None),
        ("New restaurant opens in Manchester", None),
        ("Traffic accident on M25", None),
        ("General news about politics", None),
    ]
    
    print("Testing location matching behavior:")
    print("=" * 50)
    
    for text, expected in test_cases:
        print(f"\nTesting: '{text}'")
        
        # Create a mock entry
        entry = {
            'title': text,
            'description': '',
            'content': '',
            'source': 'test'
        }
        
        # Extract location
        location = matcher.extract_location_from_entry(entry)
        
        if location:
            print(f"  Found location: {location}")
            try:
                lat, lon = matcher.get_coordinates(location)
                print(f"  Coordinates: {lat}, {lon}")
            except ValueError as e:
                print(f"  ERROR: {e}")
        else:
            print(f"  No location found (expected: {expected})")
        
        # Test if this matches our expectation
        if location == expected:
            print("  ✓ PASS")
        else:
            print(f"  ✗ FAIL - Expected: {expected}, Got: {location}")

def test_process_entries():
    """Test the full process_entries method"""
    
    matcher = LocationMatcher()
    
    # Test entries
    test_entries = [
        {
            'title': 'Police arrest suspect in Oxford Circus stabbing',
            'description': 'Incident occurred in central London',
            'source': 'met_police'
        },
        {
            'title': 'Weather forecast for the weekend',
            'description': 'Sunny weather expected',
            'source': 'bbc'
        },
        {
            'title': 'New restaurant opens in Manchester',
            'description': 'Popular chain expands north',
            'source': 'bbc'
        }
    ]
    
    print("\n\nTesting process_entries method:")
    print("=" * 50)
    
    processed = matcher.process_entries(test_entries)
    
    for i, entry in enumerate(processed):
        print(f"\nEntry {i+1}: {entry['title']}")
        print(f"  Location: {entry.get('location')}")
        print(f"  Lat: {entry.get('lat')}")
        print(f"  Lon: {entry.get('lon')}")
        
        # Check if location data is properly set or None
        if entry.get('location') is None:
            if entry.get('lat') is None and entry.get('lon') is None:
                print("  ✓ Correctly has no location data")
            else:
                print("  ✗ ERROR: Location is None but coordinates are set")
        else:
            if entry.get('lat') is not None and entry.get('lon') is not None:
                print("  ✓ Correctly has location data")
            else:
                print("  ✗ ERROR: Location is set but coordinates are missing")

if __name__ == "__main__":
    test_location_matching()
    test_process_entries()
    print("\n\nTest completed!") 