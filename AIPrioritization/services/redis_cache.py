"""
Enhanced Redis Caching Service
Provides intelligent caching for AI prioritization results, user data, and performance optimization
"""
import asyncio
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)

class RedisCacheService:
    """Enhanced Redis service optimized for caching with intelligent TTL and performance features"""
    
    def __init__(self):
        self.redis_url = self._build_redis_url()
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._is_connected = False
        
        # Cache configuration
        self.default_ttl = settings.CACHE_TTL_SECONDS
        self.max_cache_size = settings.CACHE_MAX_SIZE
        
        # Cache key prefixes for organization
        self.prefixes = {
            "priority_results": "pr:",
            "user_data": "user:",
            "ai_suggestions": "suggest:",
            "metrics": "metrics:",
            "sessions": "session:",
            "rate_limits": "rate:",
            "system_stats": "stats:",
            "temp_data": "temp:"
        }
    
    async def connect(self):
        """Connect to Redis and initialize the connection pool"""
        if self._is_connected:
            return
            
        await self.initialize()
        self._is_connected = True
        logger.info("Redis cache service connected successfully")
    
    async def close(self):
        """Close Redis connection pool"""
        if self._connection_pool:
            try:
                await self._client.close()
                await self._connection_pool.disconnect()
                self._is_connected = False
                self._client = None
                self._connection_pool = None
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
    
    def _build_redis_url(self) -> str:
        """Build Redis URL with authentication if configured"""
        if settings.REDIS_PASSWORD:
            return f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        else:
            return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    
    async def initialize(self):
        """Initialize Redis connection pool for caching"""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            self._client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._client.ping()
            self._is_connected = True
            
            logger.info("✅ Redis cache service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis cache: {e}")
            self._is_connected = False
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._is_connected
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Redis health check with cache-specific metrics"""
        try:
            if not self._client:
                return {"status": "unhealthy", "error": "No Redis client"}
            
            start_time = asyncio.get_event_loop().time()
            await self._client.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get Redis info
            info = await self._client.info()
            
            # Get cache statistics
            cache_stats = await self._get_cache_statistics()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "redis_info": {
                    "version": info.get("redis_version", "unknown"),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                },
                "cache_stats": cache_stats
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        try:
            stats = {}
            
            # Count keys by prefix
            for category, prefix in self.prefixes.items():
                pattern = f"{prefix}*"
                cursor = 0
                count = 0
                
                # Use SCAN to count keys efficiently
                while True:
                    cursor, keys = await self._client.scan(cursor, match=pattern, count=1000)
                    count += len(keys)
                    if cursor == 0:
                        break
                
                stats[f"{category}_keys"] = count
            
            # Calculate hit ratio
            info = await self._client.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            
            if hits + misses > 0:
                hit_ratio = hits / (hits + misses)
            else:
                hit_ratio = 0.0
            
            stats.update({
                "hit_ratio": round(hit_ratio, 3),
                "total_hits": hits,
                "total_misses": misses,
                "memory_usage": info.get("used_memory", 0)
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {"error": str(e)}
    
    def _make_key(self, prefix_type: str, key: str) -> str:
        """Create a properly prefixed cache key"""
        prefix = self.prefixes.get(prefix_type, "cache:")
        return f"{prefix}{key}"
    
    def _hash_key(self, data: str) -> str:
        """Create a hash-based key for complex data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    # Priority Results Caching
    async def cache_priority_result(self, task_id: str, result_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache AI priority result for quick retrieval"""
        if not self._client:
            return False
        
        try:
            key = self._make_key("priority_results", task_id)
            ttl = ttl or self.default_ttl
            
            # Add caching metadata
            cached_data = {
                "data": result_data,
                "cached_at": datetime.utcnow().isoformat() + "Z",
                "ttl": ttl
            }
            
            await self._client.setex(
                key,
                ttl,
                json.dumps(cached_data, default=str)
            )
            
            logger.debug(f"💾 Cached priority result: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cache priority result: {e}")
            return False
    
    async def get_cached_priority_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached priority result"""
        if not self._client:
            return None
        
        try:
            key = self._make_key("priority_results", task_id)
            cached_data = await self._client.get(key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"💾 Cache hit for priority result: {task_id}")
                return data.get("data")
            
            logger.debug(f"💾 Cache miss for priority result: {task_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving cached priority result: {e}")
            return None
    
    # AI Suggestions Caching
    async def cache_ai_suggestions(self, content_hash: str, suggestions: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        """Cache AI suggestions based on content hash"""
        if not self._client:
            return False
        
        try:
            key = self._make_key("ai_suggestions", content_hash)
            ttl = ttl or 7200  # 2 hours for AI suggestions
            
            cached_data = {
                "suggestions": suggestions,
                "cached_at": datetime.utcnow().isoformat() + "Z",
                "count": len(suggestions)
            }
            
            await self._client.setex(
                key,
                ttl,
                json.dumps(cached_data, default=str)
            )
            
            logger.debug(f"💾 Cached AI suggestions: {content_hash}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cache AI suggestions: {e}")
            return False
    
    async def get_cached_ai_suggestions(self, content_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached AI suggestions"""
        if not self._client:
            return None
        
        try:
            key = self._make_key("ai_suggestions", content_hash)
            cached_data = await self._client.get(key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"💾 Cache hit for AI suggestions: {content_hash}")
                return data.get("suggestions", [])
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving cached AI suggestions: {e}")
            return None
    
    # User Data Caching
    async def cache_user_data(self, user_id: str, user_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache user profile and preferences"""
        if not self._client:
            return False
        
        try:
            key = self._make_key("user_data", user_id)
            ttl = ttl or 3600  # 1 hour for user data
            
            await self._client.setex(
                key,
                ttl,
                json.dumps(user_data, default=str)
            )
            
            logger.debug(f"💾 Cached user data: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cache user data: {e}")
            return False
    
    async def get_cached_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached user data"""
        if not self._client:
            return None
        
        try:
            key = self._make_key("user_data", user_id)
            cached_data = await self._client.get(key)
            
            if cached_data:
                logger.debug(f"💾 Cache hit for user data: {user_id}")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving cached user data: {e}")
            return None
    
    # Rate Limiting
    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """Implement rate limiting with sliding window"""
        if not self._client:
            return {"allowed": True, "remaining": limit}
        
        try:
            key = self._make_key("rate_limits", identifier)
            now = datetime.utcnow().timestamp()
            window_start = now - window_seconds
            
            # Use sorted set for sliding window
            pipe = self._client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry
            pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
            current_count = results[1]
            
            remaining = max(0, limit - current_count)
            allowed = current_count < limit
            
            return {
                "allowed": allowed,
                "remaining": remaining,
                "limit": limit,
                "window_seconds": window_seconds,
                "current_count": current_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking rate limit: {e}")
            return {"allowed": True, "remaining": limit}
    
    # System Metrics Caching
    async def update_system_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Update system performance metrics"""
        if not self._client:
            return False
        
        try:
            key = self._make_key("system_stats", "current")
            
            # Add timestamp
            metrics["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            await self._client.setex(
                key,
                300,  # 5 minutes
                json.dumps(metrics, default=str)
            )
            
            # Also store in time series for historical data
            ts_key = self._make_key("metrics", f"ts_{datetime.utcnow().strftime('%Y%m%d_%H%M')}")
            await self._client.setex(ts_key, 86400, json.dumps(metrics, default=str))  # 24 hours
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update system metrics: {e}")
            return False
    
    async def get_system_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current system metrics"""
        if not self._client:
            return None
        
        try:
            key = self._make_key("system_stats", "current")
            cached_data = await self._client.get(key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving system metrics: {e}")
            return None
    
    # Bulk Operations
    async def bulk_delete(self, pattern: str) -> int:
        """Delete multiple keys matching pattern"""
        if not self._client:
            return 0
        
        try:
            cursor = 0
            deleted_count = 0
            
            while True:
                cursor, keys = await self._client.scan(cursor, match=pattern, count=1000)
                
                if keys:
                    deleted = await self._client.delete(*keys)
                    deleted_count += deleted
                
                if cursor == 0:
                    break
            
            logger.info(f"🗑️ Bulk deleted {deleted_count} keys matching pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error in bulk delete: {e}")
            return 0
    
    async def clear_expired_cache(self) -> Dict[str, int]:
        """Clear expired cache entries and return statistics"""
        stats = {}
        
        for category, prefix in self.prefixes.items():
            pattern = f"{prefix}*"
            deleted = await self.bulk_delete(pattern)
            stats[category] = deleted
        
        return stats

# Global Redis cache service instance
redis_cache = RedisCacheService()
