"""
Caching system for feed data to reduce unnecessary requests
"""

import json
import os
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    """
    Manages caching of feed data to reduce unnecessary requests
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """
        Generate a cache key for a URL and parameters
        """
        key_data = url
        if params:
            key_data += json.dumps(params, sort_keys=True)
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the full path for a cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a URL
        
        Args:
            url: The URL that was cached
            params: Optional parameters that were used
            
        Returns:
            Cached data if valid, None if not found or expired
        """
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            ttl = cached_data.get('ttl', self.default_ttl)
            
            if datetime.now() - cached_time > timedelta(seconds=ttl):
                logger.debug(f"Cache expired for {url}")
                self.delete(url, params)
                return None
            
            logger.debug(f"Cache hit for {url}")
            return cached_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {url}: {str(e)}")
            return None
    
    def set(self, url: str, data: Any, ttl: Optional[int] = None, 
            params: Optional[Dict] = None) -> bool:
        """
        Cache data for a URL
        
        Args:
            url: The URL to cache
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
            params: Optional parameters used with the URL
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'url': url,
                'params': params,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'ttl': ttl or self.default_ttl
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cached data for {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching data for {url}: {str(e)}")
            return False
    
    def delete(self, url: str, params: Optional[Dict] = None) -> bool:
        """
        Delete cached data for a URL
        
        Args:
            url: The URL to delete from cache
            params: Optional parameters used with the URL
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.debug(f"Deleted cache for {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache for {url}: {str(e)}")
            return False
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of expired entries cleared
        """
        cleared_count = 0
        
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                cache_path = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    ttl = cached_data.get('ttl', self.default_ttl)
                    
                    if datetime.now() - cached_time > timedelta(seconds=ttl):
                        os.remove(cache_path)
                        cleared_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing cache file {filename}: {str(e)}")
                    # Remove corrupted cache files
                    try:
                        os.remove(cache_path)
                        cleared_count += 1
                    except:
                        pass
            
            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            total_files = 0
            total_size = 0
            expired_files = 0
            
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                cache_path = os.path.join(self.cache_dir, filename)
                total_files += 1
                total_size += os.path.getsize(cache_path)
                
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    ttl = cached_data.get('ttl', self.default_ttl)
                    
                    if datetime.now() - cached_time > timedelta(seconds=ttl):
                        expired_files += 1
                        
                except:
                    expired_files += 1
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'expired_files': expired_files,
                'valid_files': total_files - expired_files,
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {} 