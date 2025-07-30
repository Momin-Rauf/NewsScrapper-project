"""
Location matching and geocoding for London areas
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from config.locations import LONDON_LOCATIONS
from config.settings import DEFAULT_LAT, DEFAULT_LON
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LocationMatcher:
    """
    Matches text content to London locations and provides coordinates
    """
    
    def __init__(self):
        self.locations = LONDON_LOCATIONS
        # Create regex patterns for location matching
        self.location_patterns = {}
        for location, coords in self.locations.items():
            # Create pattern that matches the location name
            pattern = re.compile(rf'\b{re.escape(location)}\b', re.IGNORECASE)
            self.location_patterns[location] = pattern
        
        # Enhanced location detection patterns
        self.enhanced_patterns = {
            # Borough patterns
            'borough': re.compile(r'\b(\w+)\s+borough\b', re.IGNORECASE),
            'council': re.compile(r'\b(\w+)\s+council\b', re.IGNORECASE),
            
            # Area patterns
            'area': re.compile(r'\b(\w+)\s+area\b', re.IGNORECASE),
            'district': re.compile(r'\b(\w+)\s+district\b', re.IGNORECASE),
            
            # Station patterns
            'station': re.compile(r'\b(\w+(?:\s+\w+)*)\s+station\b', re.IGNORECASE),
            
            # Street patterns
            'street': re.compile(r'\b(\w+(?:\s+\w+)*)\s+street\b', re.IGNORECASE),
            'road': re.compile(r'\b(\w+(?:\s+\w+)*)\s+road\b', re.IGNORECASE),
            'lane': re.compile(r'\b(\w+(?:\s+\w+)*)\s+lane\b', re.IGNORECASE),
            
            # General location mentions
            'in_location': re.compile(r'\bin\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
            'at_location': re.compile(r'\bat\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
            'near_location': re.compile(r'\bnear\s+(\w+(?:\s+\w+)*)\b', re.IGNORECASE),
        }
    
    def find_locations_in_text(self, text: str) -> List[str]:
        """
        Find all London locations mentioned in text using multiple methods
        
        Args:
            text: Text to search for locations
            
        Returns:
            List of found location names
        """
        if not text:
            return []
        
        found_locations = []
        
        # Method 1: Direct location name matching
        for location, pattern in self.location_patterns.items():
            if pattern.search(text):
                found_locations.append(location)
        
        # Method 2: Enhanced pattern matching
        for pattern_name, pattern in self.enhanced_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                # Clean up the match
                clean_match = match.strip().lower()
                if clean_match in self.locations:
                    found_locations.append(clean_match)
        
        # Method 3: Context-based location detection
        context_locations = self._find_context_locations(text)
        found_locations.extend(context_locations)
        
        # Remove duplicates while preserving order
        unique_locations = []
        for loc in found_locations:
            if loc not in unique_locations:
                unique_locations.append(loc)
        
        return unique_locations
    
    def _find_context_locations(self, text: str) -> List[str]:
        """
        Find locations based on context clues
        """
        locations = []
        
        # Look for specific context patterns
        context_patterns = [
            (r'\bstabbing\s+in\s+(\w+(?:\s+\w+)*)\b', 'south'),
            (r'\bincident\s+in\s+(\w+(?:\s+\w+)*)\b', 'south'),
            (r'\battack\s+in\s+(\w+(?:\s+\w+)*)\b', 'south'),
            (r'\b(\w+(?:\s+\w+)*)\s+police\b', 'south'),
            (r'\b(\w+(?:\s+\w+)*)\s+station\b', 'transport'),
        ]
        
        for pattern, context_type in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip().lower()
                if clean_match in self.locations:
                    locations.append(clean_match)
        
        return locations
    
    def get_coordinates(self, location_name: str) -> Tuple[float, float]:
        """
        Get coordinates for a location name
        
        Args:
            location_name: Name of the location
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            ValueError: If location is not found in database
        """
        location_lower = location_name.lower()
        
        if location_lower in self.locations:
            coords = self.locations[location_lower]
            return coords['lat'], coords['lon']
        
        # Raise error if location not found instead of using defaults
        logger.warning(f"Location '{location_name}' not found in database")
        raise ValueError(f"Location '{location_name}' not found in database")
    
    def extract_location_from_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Extract the most relevant location from an entry using multiple methods
        
        Args:
            entry: Parsed feed entry
            
        Returns:
            Location name or None if no location found
        """
        title = entry.get('title', '')
        description = entry.get('description', '')
        content = entry.get('content', '')
        
        # Combine all text for location search
        combined_text = f"{title} {description} {content}"
        
        # Find all locations mentioned
        locations = self.find_locations_in_text(combined_text)
        
        if not locations:
            # Try source-based location assignment
            source_location = self._get_location_from_source(entry)
            if source_location:
                return source_location
            return None
        
        # Return the first location found (could be enhanced to find the most relevant)
        return locations[0]
    
    def _get_location_from_source(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Assign location based on source and content analysis
        """
        source = entry.get('source', '').lower()
        title = entry.get('title', '').lower()
        
        # Met Police articles - try to extract borough from title
        if 'met_police' in source:
            # Look for borough names in Met Police titles
            borough_patterns = [
                r'\bin\s+(\w+)\b',  # "in Southwark"
                r'\bat\s+(\w+)\b',  # "at Romford"
                r'\b(\w+)\s+incident',  # "Southwark incident"
            ]
            
            for pattern in borough_patterns:
                matches = re.findall(pattern, title, re.IGNORECASE)
                for match in matches:
                    clean_match = match.strip().lower()
                    if clean_match in self.locations:
                        return clean_match
        
        # BBC News - try to extract London areas
        elif 'bbc' in source:
            # Look for London-specific keywords
            london_keywords = ['london', 'south london', 'east london', 'north london', 'west london']
            for keyword in london_keywords:
                if keyword in title:
                    # Assign to a relevant London area based on content
                    return self._assign_london_area(entry)
        
        return None
    
    def _assign_london_area(self, entry: Dict[str, Any]) -> str:
        """
        Assign a London area based on content analysis
        """
        title = entry.get('title', '').lower()
        description = entry.get('description', '').lower()
        combined = f"{title} {description}"
        
        # Look for directional indicators
        if any(word in combined for word in ['south', 'south-east', 'south east']):
            return 'southwark'  # South London
        elif any(word in combined for word in ['east', 'east london']):
            return 'newham'  # East London
        elif any(word in combined for word in ['north', 'north london']):
            return 'camden'  # North London
        elif any(word in combined for word in ['west', 'west london']):
            return 'chelsea'  # West London
        elif any(word in combined for word in ['central', 'central london']):
            return 'soho'  # Central London
        
         # Don't default to any area if no clear directional indicators found
        return None
    
    def process_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process entries to add location information
        
        Args:
            entries: List of parsed feed entries
            
        Returns:
            List of entries with location data added
        """
        processed_entries = []
        
        for entry in entries:
            # Extract location
            location_name = self.extract_location_from_entry(entry)
            
            if location_name:
                try:
                    lat, lon = self.get_coordinates(location_name)
                    entry['location'] = location_name
                    entry['lat'] = lat
                    entry['lon'] = lon
                    logger.debug(f"Found location '{location_name}' for entry: {entry.get('title', 'No title')}")
                except ValueError:
                    # Location name was found but coordinates are not available
                    entry['location'] = None
                    entry['lat'] = None
                    entry['lon'] = None
                    logger.debug(f"Location '{location_name}' found but coordinates not available for entry: {entry.get('title', 'No title')}")
            else:
                # Don't use default location if no match found
                entry['location'] = None
                entry['lat'] = None
                entry['lon'] = None
                logger.debug(f"No specific location found for entry: {entry.get('title', 'No title')}, skipping location data")
            
            processed_entries.append(entry)
        
        logger.info(f"Processed {len(entries)} entries with location data")
        return processed_entries 