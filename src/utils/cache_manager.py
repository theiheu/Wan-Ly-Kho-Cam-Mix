"""
Cache Manager for the Chicken Farm App.
This module provides caching functionality to improve performance.
"""

import os
import json
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps


class CacheManager:
    """
    Manages caching for expensive operations to improve performance.
    """

    def __init__(self, cache_dir: str = "src/data/cache"):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_ttl = {}  # Time-to-live for memory cache items

        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_from_memory(self, key: str) -> Optional[Any]:
        """
        Get an item from memory cache.

        Args:
            key: Cache key

        Returns:
            The cached value or None if not found or expired
        """
        if key in self.memory_cache:
            # Check if the cache item has expired
            if key in self.cache_ttl and self.cache_ttl[key] < time.time():
                # Cache expired, remove it
                del self.memory_cache[key]
                del self.cache_ttl[key]
                return None

            return self.memory_cache[key]

        return None

    def set_in_memory(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Store an item in memory cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self.memory_cache[key] = value
        self.cache_ttl[key] = time.time() + ttl

    def get_from_disk(self, key: str) -> Optional[Any]:
        """
        Get an item from disk cache.

        Args:
            key: Cache key

        Returns:
            The cached value or None if not found
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Check if the cache has expired
                if "expiry" in cache_data and cache_data["expiry"] < time.time():
                    # Cache expired, remove the file
                    os.remove(cache_file)
                    return None

                return cache_data.get("value")
            except Exception as e:
                print(f"Error reading cache file {cache_file}: {e}")
                return None

        return None

    def set_on_disk(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Store an item in disk cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        try:
            cache_data = {
                "value": value,
                "expiry": time.time() + ttl
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error writing cache file {cache_file}: {e}")

    def get(self, key: str, use_disk: bool = False) -> Optional[Any]:
        """
        Get an item from cache (memory or disk).

        Args:
            key: Cache key
            use_disk: Whether to check disk cache if not found in memory

        Returns:
            The cached value or None if not found
        """
        # Try memory cache first
        value = self.get_from_memory(key)

        if value is None and use_disk:
            # Try disk cache
            value = self.get_from_disk(key)

            # Store in memory for faster access next time
            if value is not None:
                self.set_in_memory(key, value)

        return value

    def set(self, key: str, value: Any, ttl: int = 300, use_disk: bool = False) -> None:
        """
        Store an item in cache (memory and optionally disk).

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            use_disk: Whether to also store in disk cache
        """
        # Store in memory
        self.set_in_memory(key, value, ttl)

        # Store on disk if requested
        if use_disk:
            self.set_on_disk(key, value, ttl)

    def invalidate(self, key: str) -> None:
        """
        Invalidate a cache item.

        Args:
            key: Cache key
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]

        if key in self.cache_ttl:
            del self.cache_ttl[key]

        # Remove from disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception as e:
                print(f"Error removing cache file {cache_file}: {e}")

    def clear(self) -> None:
        """Clear all cache items."""
        # Clear memory cache
        self.memory_cache = {}
        self.cache_ttl = {}

        # Clear disk cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except Exception as e:
                    print(f"Error removing cache file {filename}: {e}")


# Create a global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 300, use_disk: bool = False, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        use_disk: Whether to also store in disk cache
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            arg_str = ",".join([str(arg) for arg in args])
            kwarg_str = ",".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
            key = f"{key_prefix}{func.__name__}_{arg_str}_{kwarg_str}"

            # Try to get from cache
            cached_result = cache_manager.get(key, use_disk)
            if cached_result is not None:
                return cached_result

            # Call the function
            result = func(*args, **kwargs)

            # Store in cache
            cache_manager.set(key, result, ttl, use_disk)

            return result
        return wrapper
    return decorator