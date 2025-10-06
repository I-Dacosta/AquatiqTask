import asyncio
import json
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Enhanced Redis Pub/Sub service for the AI Prioritization Engine"""
    
    def __init__(self):
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._publisher_client: Optional[redis.Redis] = None
        self._subscriber_client: Optional[redis.Redis] = None
        self._pubsub = None
        self._is_connected = False
        self._listener_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize Redis connections"""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True
            )
            
            self._publisher_client = redis.Redis(connection_pool=self._connection_pool)
            self._subscriber_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._publisher_client.ping()
            self._is_connected = True
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self._is_connected = False
            raise
    
    async def close(self):
        """Close Redis connections"""
        self._is_connected = False
        
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.close()
        
        if self._publisher_client:
            await self._publisher_client.close()
            
        if self._subscriber_client:
            await self._subscriber_client.close()
        
        if self._connection_pool:
            await self._connection_pool.disconnect()
        
        logger.info("🛑 Redis connections closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._is_connected
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Redis health check"""
        try:
            if not self._publisher_client:
                return {"status": "unhealthy", "error": "No Redis client"}
            
            start_time = asyncio.get_event_loop().time()
            await self._publisher_client.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "redis_url": self.redis_url
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def publish(self, channel: str, data: Dict[str, Any]) -> bool:
        """Publish data to Redis channel with error handling"""
        if not self._is_connected or not self._publisher_client:
            logger.error("Redis not connected, cannot publish")
            return False
        
        try:
            json_data = json.dumps(data, default=str)
            await self._publisher_client.publish(channel, json_data)
            logger.info(f"📤 Published to channel '{channel}': {len(json_data)} bytes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish to channel '{channel}': {e}")
            return False
    
    async def start_listening(self, message_handler):
        """Start listening for messages on the prioritization channel"""
        if not self._is_connected or not self._subscriber_client:
            logger.error("Redis not connected, cannot start listener")
            return
        
        try:
            self._pubsub = self._subscriber_client.pubsub()
            await self._pubsub.subscribe(settings.PRIORITIZATION_REQUEST_CHANNEL)
            logger.info(f"🎧 Started listening on channel: {settings.PRIORITIZATION_REQUEST_CHANNEL}")
            
            async for message in self._pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'].decode('utf-8'))
                        logger.info(f"📥 Received message: {data.get('id', 'unknown')}")
                        await message_handler(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Invalid JSON received: {e}")
                    except Exception as e:
                        logger.error(f"❌ Error processing message: {e}")
                        
        except asyncio.CancelledError:
            logger.info("🛑 Redis listener cancelled")
        except Exception as e:
            logger.error(f"❌ Redis listener error: {e}")
            # Attempt to reconnect after error
            await asyncio.sleep(5)
            if self._is_connected:
                await self.start_listening(message_handler)

# Global Redis service instance
redis_service = RedisService()

# Legacy compatibility functions
async def redis_publisher(channel: str, data: str):
    """Legacy compatibility function - use redis_service.publish() instead"""
    try:
        data_dict = json.loads(data) if isinstance(data, str) else data
        return await redis_service.publish(channel, data_dict)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data for legacy publisher")
        return False

async def redis_subscriber():
    """Legacy compatibility function - use redis_service.start_listening() instead"""
    if not redis_service.is_connected:
        await redis_service.initialize()
    return redis_service._pubsub

# Legacy compatibility functions
async def redis_publisher(channel: str, data: str):
    """Legacy compatibility function - use redis_service.publish() instead"""
    try:
        data_dict = json.loads(data) if isinstance(data, str) else data
        return await redis_service.publish(channel, data_dict)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data for legacy publisher")
        return False

async def redis_subscriber():
    """Legacy compatibility function - use redis_service.start_listening() instead"""
    if not redis_service.is_connected:
        await redis_service.initialize()
    return redis_service._pubsub
