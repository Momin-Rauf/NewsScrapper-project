"""
Rate limiting and retry utilities for feed fetching
"""

import time
import random
from typing import Callable, Any, Optional
from functools import wraps
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """
    Rate limiter to prevent overwhelming news sources
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_request(self) -> bool:
        """Check if a request can be made"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a request"""
        self.requests.append(time.time())
    
    def wait_if_needed(self):
        """Wait if rate limit is reached"""
        if not self.can_request():
            wait_time = self.time_window / self.max_requests
            logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        self.record_request()


def retry_on_failure(max_retries: int = 3, base_delay: float = 1.0, 
                    max_delay: float = 60.0, exponential_backoff: bool = True):
    """
    Decorator for retrying failed operations with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_backoff: Whether to use exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise last_exception
                    
                    # Calculate delay
                    if exponential_backoff:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay
                    
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1 * delay)
                    total_delay = delay + jitter
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. Retrying in {total_delay:.2f} seconds...")
                    time.sleep(total_delay)
            
            raise last_exception
        
        return wrapper
    return decorator


def rate_limited(rate_limiter: RateLimiter):
    """
    Decorator to apply rate limiting to a function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            rate_limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class FeedRateLimiter:
    """
    Per-feed rate limiter with different limits for different sources
    """
    
    def __init__(self):
        # Different rate limits for different sources
        self.limiters = {
            'bbc': RateLimiter(max_requests=5, time_window=60),  # BBC is more sensitive
            'met_police': RateLimiter(max_requests=10, time_window=60),  # Met Police allows more
            'govuk': RateLimiter(max_requests=8, time_window=60),  # GOV.UK moderate
            'default': RateLimiter(max_requests=6, time_window=60)  # Default for unknown sources
        }
    
    def get_limiter(self, source: str) -> RateLimiter:
        """Get rate limiter for a specific source"""
        return self.limiters.get(source.lower(), self.limiters['default'])
    
    def wait_for_source(self, source: str):
        """Wait if rate limit is reached for a specific source"""
        limiter = self.get_limiter(source)
        limiter.wait_if_needed() 