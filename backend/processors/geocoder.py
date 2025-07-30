"""
Advanced geocoding for London locations using multiple methods
"""

import re
import requests
from typing import List, Dict, Any, Optional, Tuple
from config.locations import LONDON_LOCATIONS
from config.settings import DEFAULT_LAT, DEFAULT_LON
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AdvancedGeocoder:
    """
    Advanced geocoding using multiple methods:
    1. Local location database
    2. Named Entity Recognition (NER) patterns
    3. External geocoding APIs (optional)
    4. Context-based location assignment
    """
    
    def __init__(self):
        self.locations = LONDON_LOCATIONS
        
        # London boroughs and their approximate centers
        self.london_boroughs = {
            'barking and dagenham': {'lat': 51.5400, 'lon': 0.0800},
            'barnet': {'lat': 51.6500, 'lon': -0.2000},
            'bexley': {'lat': 51.4500, 'lon': 0.1500},
            'brent': {'lat': 51.5500, 'lon': -0.3000},
            'bromley': {'lat': 51.4000, 'lon': 0.0500},
            'camden': {'lat': 51.5455, 'lon': -0.1627},
            'croydon': {'lat': 51.3700, 'lon': -0.1000},
            'ealing': {'lat': 51.5100, 'lon': -0.3000},
            'enfield': {'lat': 51.6520, 'lon': -0.0800},
            'greenwich': {'lat': 51.4767, 'lon': -0.0000},
            'hackney': {'lat': 51.5450, 'lon': -0.0550},
            'hammersmith and fulham': {'lat': 51.4925, 'lon': -0.2225},
            'haringey': {'lat': 51.5900, 'lon': -0.1100},
            'harrow': {'lat': 51.5800, 'lon': -0.3300},
            'havering': {'lat': 51.5750, 'lon': 0.1833},
            'hillingdon': {'lat': 51.5400, 'lon': -0.4700},
            'hounslow': {'lat': 51.4700, 'lon': -0.3600},
            'islington': {'lat': 51.5362, 'lon': -0.1033},
            'kensington and chelsea': {'lat': 51.5000, 'lon': -0.1900},
            'kingston upon thames': {'lat': 51.4100, 'lon': -0.3000},
            'lambeth': {'lat': 51.4613, 'lon': -0.1156},
            'lewisham': {'lat': 51.4567, 'lon': -0.0167},
            'merton': {'lat': 51.4100, 'lon': -0.2000},
            'newham': {'lat': 51.5250, 'lon': 0.0036},
            'redbridge': {'lat': 51.5600, 'lon': 0.0700},
            'richmond upon thames': {'lat': 51.4500, 'lon': -0.3000},
            'southwark': {'lat': 51.4880, 'lon': -0.0910},
            'sutton': {'lat': 51.3600, 'lon': -0.2000},
            'tower hamlets': {'lat': 51.5200, 'lon': -0.0500},
            'waltham forest': {'lat': 51.5900, 'lon': -0.0100},
            'wandsworth': {'lat': 51.4567, 'lon': -0.1920},
            'westminster': {'lat': 51.4995, 'lon': -0.1245},
        }
        
        # Enhanced patterns for location detection
        self.location_patterns = {
            # Borough patterns
            'borough': re.compile(r'\b(\w+(?:\s+\w+)*)\s+borough\b', re.IGNORECASE),
            'council': re.compile(r'\b(\w+(?:\s+\w+)*)\s+council\b', re.IGNORECASE),
            
            # Station patterns
            'station': re.compile(r'\b(\w+(?:\s+\w+)*)\s+station\b', re.IGNORECASE),
            
            # Street patterns
            'street': re.compile(r'\b(\w+(?:\s+\w+)*)\s+street\b', re.IGNORECASE),
            'road': re.compile(r'\b(\w+(?:\s+\w+)*)\s+road\b', re.IGNORECASE),
            'lane': re.compile(r'\b(\w+(?:\s+\w+)*)\s+lane\b', re.IGNORECASE),
            
            # Location prepositions
            'in_location': re.compile(r'\bin\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
            'at_location': re.compile(r'\bat\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
            'near_location': re.compile(r'\bnear\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
        }
    
    def extract_location(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Extract location using multiple methods
        """
        title = entry.get('title', '')
        description = entry.get('description', '')
        content = entry.get('content', '')
        source = entry.get('source', '')
        
        combined_text = f"{title} {description} {content}"
        
        # Method 1: Direct location matching
        location = self._find_direct_location(combined_text)
        if location:
            return location
        
        # Method 2: Borough detection
        location = self._find_borough(combined_text)
        if location:
            return location
        
        # Method 3: Source-based assignment
        location = self._assign_by_source(entry)
        if location:
            return location
        
        # Method 4: Content-based area assignment
        location = self._assign_by_content(entry)
        if location:
            return location
        
        return None
    
    def _find_direct_location(self, text: str) -> Optional[str]:
        """Find exact location matches"""
        for location in self.locations:
            if re.search(rf'\b{re.escape(location)}\b', text, re.IGNORECASE):
                return location
        return None
    
    def _find_borough(self, text: str) -> Optional[str]:
        """Find London boroughs"""
        for borough in self.london_boroughs:
            if re.search(rf'\b{re.escape(borough)}\b', text, re.IGNORECASE):
                return borough
        return None
    
    def _assign_by_source(self, entry: Dict[str, Any]) -> Optional[str]:
        """Assign location based on source and content"""
        source = entry.get('source', '').lower()
        title = entry.get('title', '').lower()
        
        if 'met_police' in source:
            # Met Police articles often mention specific boroughs
            for borough in self.london_boroughs:
                if borough in title:
                    return borough
        
        elif 'bbc' in source:
            # BBC articles - look for London area indicators
            if 'london' in title:
                return self._get_london_area_from_content(entry)
        
        return None
    
    def _assign_by_content(self, entry: Dict[str, Any]) -> Optional[str]:
        """Assign location based on content analysis"""
        title = entry.get('title', '').lower()
        description = entry.get('description', '').lower()
        combined = f"{title} {description}"
        
        # Look for directional indicators
        if any(word in combined for word in ['south', 'south-east', 'south east']):
            return 'lambeth'  # South London
        elif any(word in combined for word in ['east', 'east london']):
            return 'newham'  # East London
        elif any(word in combined for word in ['north', 'north london']):
            return 'camden'  # North London
        elif any(word in combined for word in ['west', 'west london']):
            return 'kensington and chelsea'  # West London
        elif any(word in combined for word in ['central', 'central london']):
            return 'westminster'  # Central London
        
        return None
    
    def _get_london_area_from_content(self, entry: Dict[str, Any]) -> str:
        """Get London area from content analysis"""
        return self._assign_by_content(entry) or 'westminster'
    
    def get_coordinates(self, location_name: str) -> Tuple[float, float]:
        """Get coordinates for a location"""
        location_lower = location_name.lower()
        
        # Check local locations first
        if location_lower in self.locations:
            coords = self.locations[location_lower]
            return coords['lat'], coords['lon']
        
        # Check boroughs
        if location_lower in self.london_boroughs:
            coords = self.london_boroughs[location_lower]
            return coords['lat'], coords['lon']
        
        # Default coordinates
        logger.warning(f"Location '{location_name}' not found, using default coordinates")
        return DEFAULT_LAT, DEFAULT_LON


# Optional: External geocoding service (requires API key)
class ExternalGeocoder:
    """
    External geocoding using services like Google Maps, OpenStreetMap, etc.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode an address using external service
        Note: This requires API keys and rate limits
        """
        # Implementation would go here
        # For now, return None to use local geocoding
        return None 