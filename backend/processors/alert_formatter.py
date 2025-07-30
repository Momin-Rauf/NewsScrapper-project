"""
Alert formatting for final JSON output
"""

from typing import List, Dict, Any
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AlertFormatter:
    """
    Formats processed entries into final alert structure
    """
    
    def __init__(self):
        self.alert_types = {
            'police': 'crime',
            'news': 'news', 
            'government': 'emergency'
        }
    
    def format_entry_to_alert(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a processed entry to the final alert format
        
        Args:
            entry: Processed feed entry
            
        Returns:
            Formatted alert dictionary
        """
        # Determine alert type based on source
        source_type = entry.get('type', 'news')
        alert_type = self.alert_types.get(source_type, 'news')
        
        # Format the alert
        alert = {
            'type': alert_type,
            'location': entry.get('location'),
            'time': entry.get('published', datetime.now()).isoformat(),
            'lat': entry.get('lat'),
            'lon': entry.get('lon'),
            'title': entry.get('title', 'No title'),
            'link': entry.get('link', ''),
            'source': entry.get('source', 'unknown'),
            'description': entry.get('description', ''),
            'matched_keywords': entry.get('matched_keywords', [])
        }
        
        return alert
    
    def format_alerts(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format all entries into alerts
        
        Args:
            entries: List of processed entries
            
        Returns:
            List of formatted alerts
        """
        alerts = []
        
        for entry in entries:
            try:
                alert = self.format_entry_to_alert(entry)
                alerts.append(alert)
            except Exception as e:
                logger.error(f"Error formatting entry to alert: {str(e)}")
                continue
        
        logger.info(f"Formatted {len(entries)} entries into {len(alerts)} alerts")
        return alerts
    
    def deduplicate_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate alerts based on title and location
        
        Args:
            alerts: List of alerts
            
        Returns:
            Deduplicated list of alerts
        """
        seen = set()
        unique_alerts = []
        
        for alert in alerts:
            # Create a key based on title and location
            key = f"{alert.get('title', '')}_{alert.get('location', '')}"
            
            if key not in seen:
                seen.add(key)
                unique_alerts.append(alert)
            else:
                logger.debug(f"Dropping duplicate alert: {alert.get('title', 'No title')}")
        
        logger.info(f"Deduplicated {len(alerts)} alerts down to {len(unique_alerts)} unique alerts")
        return unique_alerts
    
    def sort_alerts_by_time(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort alerts by publication time (newest first)
        
        Args:
            alerts: List of alerts
            
        Returns:
            Sorted list of alerts
        """
        try:
            sorted_alerts = sorted(alerts, key=lambda x: x.get('time', ''), reverse=True)
            logger.info(f"Sorted {len(alerts)} alerts by time")
            return sorted_alerts
        except Exception as e:
            logger.error(f"Error sorting alerts: {str(e)}")
            return alerts 