"""
File handling utilities for alerts.json
"""

import json
import os
from typing import List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


def save_alerts(alerts: List[Dict[str, Any]], filepath: str) -> bool:
    """
    Save alerts to JSON file with error handling
    
    Args:
        alerts: List of alert dictionaries
        filepath: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist (only if there's a directory path)
        directory = os.path.dirname(filepath)
        if directory:  # Only create directory if there's actually a directory path
            os.makedirs(directory, exist_ok=True)
        
        # Write alerts to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully saved {len(alerts)} alerts to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save alerts to {filepath}: {str(e)}")
        return False


def load_alerts(filepath: str) -> List[Dict[str, Any]]:
    """
    Load alerts from JSON file with error handling
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        List of alert dictionaries, empty list if file doesn't exist or error
    """
    try:
        if not os.path.exists(filepath):
            logger.info(f"Alerts file {filepath} doesn't exist, starting with empty list")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
        
        logger.info(f"Successfully loaded {len(alerts)} alerts from {filepath}")
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to load alerts from {filepath}: {str(e)}")
        return []


def backup_alerts(filepath: str) -> bool:
    """
    Create a backup of the current alerts file
    
    Args:
        filepath: Path to the alerts file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(filepath):
            logger.info(f"No alerts file to backup at {filepath}")
            return True
        
        backup_path = f"{filepath}.backup"
        with open(filepath, 'r', encoding='utf-8') as source:
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(source.read())
        
        logger.info(f"Created backup at {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return False 