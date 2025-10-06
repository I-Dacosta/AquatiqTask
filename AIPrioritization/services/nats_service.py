"""
NATS JetStream Service for Event Streaming
Provides persistent messaging with at-least-once delivery guarantees
"""
import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import nats
from nats.js import JetStreamContext
from nats.js.api import (
    StreamConfig, ConsumerConfig, DeliverPolicy, AckPolicy, 
    RetentionPolicy, StorageType, DiscardPolicy
)
from nats.errors import ConnectionClosedError, TimeoutError
from core.config import settings

logger = logging.getLogger(__name__)

class NATSJetStreamService:
    """Enhanced NATS service with JetStream for persistent messaging"""
    
    def __init__(self):
        self.nc = None
        self.js: Optional[JetStreamContext] = None
        self._is_connected = False
        self._streams_initialized = False
        
    async def connect(self):
        """Connect to NATS and initialize JetStream"""
        if self._is_connected:
            return
            
        await self.initialize()
        self._is_connected = True
        logger.info("NATS JetStream service connected successfully")
    
    async def close(self):
        """Close NATS connection"""
        if self.nc:
            try:
                await self.nc.close()
                self._is_connected = False
                self.nc = None
                self.js = None
                logger.info("NATS connection closed")
            except Exception as e:
                logger.error(f"Error closing NATS connection: {e}")
                
    async def initialize(self):
        """Initialize NATS connection and JetStream"""
        try:
            # Connection options
            options = {
                "servers": [f"nats://{settings.NATS_HOST}:{settings.NATS_PORT}"],
                "name": "ai-priority-engine",
                "reconnect_time_wait": 2,
                "max_reconnect_attempts": 10,
                "ping_interval": 20,
                "max_outstanding_pings": 5,
                "allow_reconnect": True,
                "connect_timeout": 10,
            }
            
            # Add authentication if configured
            if settings.NATS_USERNAME and settings.NATS_PASSWORD:
                options["user"] = settings.NATS_USERNAME
                options["password"] = settings.NATS_PASSWORD
            
            # Connect to NATS
            self.nc = await nats.connect(**options)
            
            # Initialize JetStream
            if settings.JETSTREAM_ENABLED:
                self.js = self.nc.jetstream()
                await self._setup_streams()
                self._streams_initialized = True
            
            self._is_connected = True
            logger.info("✅ NATS JetStream service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NATS: {e}")
            self._is_connected = False
            raise
    
    async def _setup_streams(self):
        """Create JetStream streams for persistent messaging"""
        if not self.js:
            return
            
        try:
            # Priority Requests Stream - WorkQueue (messages deleted after ack)
            await self.js.add_stream(StreamConfig(
                name="PRIORITY_REQUESTS",
                subjects=[
                    "prioritization.request",
                    "prioritization.request.*",
                    "ms-ai-backend.task.for-analysis",
                    "ms-ai-backend.task.updated",
                    "ms-ai-backend.task.completed"
                ],
                retention=RetentionPolicy.WORK_QUEUE,
                max_age=86400,  # 24 hours
                max_msgs=100000,
                storage=StorageType.FILE,
                discard=DiscardPolicy.OLD
            ))
            
            # Priority Results Stream - Limits (keep for analysis)
            await self.js.add_stream(StreamConfig(
                name="PRIORITY_RESULTS",
                subjects=[
                    "prioritization.result",
                    "prioritization.result.*",
                    "ms-ai-backend.recalculate.priorities",
                    "ms-ai-backend.batch.analyze",
                    "ms-graph.task.created"
                ],
                retention=RetentionPolicy.LIMITS,
                max_age=604800,  # 7 days
                max_msgs=500000,
                storage=StorageType.FILE,
                discard=DiscardPolicy.OLD
            ))
            
            # System Events Stream - for monitoring and audit
            await self.js.add_stream(StreamConfig(
                name="SYSTEM_EVENTS",
                subjects=["system.events.*", "audit.*"],
                retention=RetentionPolicy.LIMITS,
                max_age=2592000,  # 30 days
                max_msgs=1000000,
                storage=StorageType.FILE,
                discard=DiscardPolicy.OLD
            ))
            
            logger.info("✅ JetStream streams configured")
            
        except Exception as e:
            if "stream name already in use" not in str(e).lower():
                logger.error(f"❌ Failed to setup streams: {e}")
                raise
            else:
                logger.info("✅ JetStream streams already exist")
    
    @property
    def is_connected(self) -> bool:
        """Check if NATS is connected"""
        return self._is_connected and self.nc is not None and not self.nc.is_closed
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform NATS and JetStream health check"""
        try:
            if not self.is_connected:
                return {"status": "unhealthy", "error": "Not connected"}
            
            start_time = asyncio.get_event_loop().time()
            
            # Test basic connectivity
            if self.nc:
                await self.nc.flush(timeout=5)
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            health_info = {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "server_info": {
                    "connected": self.nc.is_connected if self.nc else False,
                    "reconnects": getattr(self.nc, 'stats', {}).get('reconnects', 0) if self.nc else 0
                },
                "jetstream_enabled": settings.JETSTREAM_ENABLED
            }
            
            # JetStream specific health check
            if settings.JETSTREAM_ENABLED and self.js:
                try:
                    account_info = await self.js.account_info()
                    streams_info = await self.js.streams_info()
                    
                    health_info["jetstream"] = {
                        "streams": len(streams_info),
                        "memory_used": account_info.memory,
                        "storage_used": account_info.storage,
                        "streams_initialized": self._streams_initialized
                    }
                except Exception as js_error:
                    health_info["jetstream"] = {
                        "status": "error",
                        "error": str(js_error)
                    }
            
            return health_info
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def publish_priority_request(self, task_data: Dict[str, Any], category: str = "") -> bool:
        """Publish prioritization request with at-least-once delivery"""
        if not self.is_connected or not self.js:
            logger.error("NATS/JetStream not connected")
            return False
        
        try:
            subject = f"{settings.PRIORITY_REQUEST_SUBJECT}.{category}" if category else settings.PRIORITY_REQUEST_SUBJECT
            
            # Add metadata
            message_data = {
                "data": task_data,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "ai-priority-engine",
                "version": "1.0"
            }
            
            # Publish with acknowledgment
            ack = await self.js.publish(
                subject,
                json.dumps(message_data, default=str).encode(),
                timeout=10.0
            )
            
            logger.info(f"📤 Published priority request: {task_data.get('id', 'unknown')} -> {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish priority request: {e}")
            return False
    
    async def publish_priority_result(self, result_data: Dict[str, Any], category: str = "") -> bool:
        """Publish prioritization result"""
        if not self.is_connected or not self.js:
            logger.error("NATS/JetStream not connected")
            return False
        
        try:
            subject = f"{settings.PRIORITY_RESULT_SUBJECT}.{category}" if category else settings.PRIORITY_RESULT_SUBJECT
            
            # Add metadata
            message_data = {
                "data": result_data,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "ai-priority-engine",
                "version": "1.0"
            }
            
            # Publish with acknowledgment
            ack = await self.js.publish(
                subject,
                json.dumps(message_data, default=str).encode(),
                timeout=10.0
            )
            
            logger.info(f"📤 Published priority result: {result_data.get('request_id', 'unknown')} -> {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish priority result: {e}")
            return False
    
    async def subscribe_priority_requests(self, callback: Callable):
        """Subscribe to priority requests with durable consumer"""
        if not self.is_connected or not self.js:
            logger.error("NATS/JetStream not connected")
            return
        
        try:
            # Create durable consumer for priority requests
            consumer_config = ConsumerConfig(
                durable_name="priority-processor",
                deliver_policy=DeliverPolicy.ALL,
                ack_policy=AckPolicy.EXPLICIT,
                max_deliver=3,  # Retry up to 3 times
                ack_wait=30,    # 30 second ack timeout
                max_ack_pending=10  # Max unacknowledged messages
            )
            
            # Subscribe to the stream
            subscription = await self.js.subscribe(
                settings.PRIORITY_REQUEST_SUBJECT,
                stream="PRIORITY_REQUESTS",
                config=consumer_config
            )
            
            logger.info(f"🎧 Subscribed to priority requests: {settings.PRIORITY_REQUEST_SUBJECT}")
            
            # Process messages
            async for msg in subscription.messages:
                try:
                    # Decode message
                    message_data = json.loads(msg.data.decode())
                    task_data = message_data.get("data", message_data)  # Support both formats
                    
                    logger.info(f"📥 Received priority request: {task_data.get('id', 'unknown')}")
                    
                    # Process with callback
                    await callback(task_data)
                    
                    # Acknowledge message (at-least-once delivery)
                    await msg.ack()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in message: {e}")
                    await msg.nak()  # Negative acknowledgment
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    await msg.nak()  # Will be redelivered
                    
        except Exception as e:
            logger.error(f"❌ Error setting up subscription: {e}")
            raise
    
    async def publish_system_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Publish system events for monitoring and audit"""
        if not self.is_connected or not self.js:
            return False
        
        try:
            subject = f"system.events.{event_type}"
            
            message_data = {
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "ai-priority-engine"
            }
            
            await self.js.publish(
                subject,
                json.dumps(message_data, default=str).encode(),
                timeout=5.0
            )
            
            logger.debug(f"📊 Published system event: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish system event: {e}")
            return False
    
    async def subscribe(self, subject: str, callback=None, queue_group: str = None, durable_name: str = None) -> None:
        """Subscribe to a NATS subject with callback
        
        Args:
            subject: The subject to subscribe to
            callback: Callback function to handle messages
            queue_group: Optional queue group for load balancing
            durable_name: Optional durable subscription name for JetStream
        """
        if not self.is_connected:
            raise RuntimeError("NATS not connected")
            
        async def message_handler(msg):
            try:
                if callback:
                    # Handle both JetStream and regular NATS messages
                    if hasattr(msg, 'data'):
                        payload = json.loads(msg.data.decode())
                    else:
                        payload = json.loads(msg.decode())
                    
                    await callback(payload)
                    
                    # Acknowledge message if using JetStream
                    if hasattr(msg, 'ack'):
                        await msg.ack()
            except Exception as e:
                logger.error(f"Error handling message for {subject}: {e}")
                # Negative acknowledge if using JetStream
                if hasattr(msg, 'nak'):
                    await msg.nak()

        if self.js and settings.JETSTREAM_ENABLED:
            try:
                # Get the appropriate stream for the subject
                stream_name = self._get_stream_for_subject(subject)
                
                # Create JetStream consumer if durable name provided
                if durable_name:
                    consumer_config = ConsumerConfig(
                        durable_name=durable_name,
                        deliver_policy=DeliverPolicy.ALL,
                        ack_policy=AckPolicy.EXPLICIT,
                        max_deliver=10,
                        filter_subject=subject
                    )
                    
                    try:
                        await self.js.add_consumer(stream=stream_name, config=consumer_config)
                    except Exception as e:
                        # Consumer might already exist
                        if "already exists" not in str(e).lower():
                            logger.error(f"Failed to create consumer: {e}")

                    # Subscribe with JetStream using explicit stream
                    await self.js.subscribe(
                        subject, 
                        queue=queue_group, 
                        durable=durable_name,
                        stream=stream_name,
                        cb=message_handler
                    )
                else:
                    # Regular JetStream subscription with explicit stream
                    await self.js.subscribe(
                        subject, 
                        queue=queue_group,
                        stream=stream_name,
                        cb=message_handler
                    )
                    
                logger.info(f"✅ Subscribed to {subject} on stream {stream_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to subscribe to {subject}: {e}")
                # Fallback to regular NATS subscription
                logger.info(f"Falling back to regular NATS subscription for {subject}")
                await self.nc.subscribe(
                    subject, 
                    queue=queue_group,
                    cb=message_handler
                )
        else:
            # Regular NATS subscription
            await self.nc.subscribe(
                subject, 
                queue=queue_group,
                cb=message_handler
            )
            
        logger.info(f"✅ Subscribed to {subject}")
    
    def _get_stream_for_subject(self, subject: str) -> str:
        """Get the appropriate stream name for a subject"""
        priority_request_subjects = [
            "prioritization.request",
            "ms-ai-backend.task.for-analysis",
            "ms-ai-backend.task.updated",
            "ms-ai-backend.task.completed"
        ]
        
        priority_result_subjects = [
            "prioritization.result",
            "ms-ai-backend.recalculate.priorities",
            "ms-ai-backend.batch.analyze",
            "ms-graph.task.created"
        ]
        
        system_event_subjects = [
            "system.events",
            "audit"
        ]
        
        if any(subject.startswith(s) for s in priority_request_subjects):
            return "PRIORITY_REQUESTS"
        elif any(subject.startswith(s) for s in priority_result_subjects):
            return "PRIORITY_RESULTS"
        elif any(subject.startswith(s) for s in system_event_subjects):
            return "SYSTEM_EVENTS"
        else:
            raise ValueError(f"No stream configured for subject: {subject}")
            
    async def publish(self, subject: str, payload: Dict[str, Any], stream: str = None) -> None:
        """Publish a message to a NATS subject
        
        Args:
            subject: The subject to publish to
            payload: The message payload
            stream: Optional stream name for JetStream
        """
        if not self.is_connected:
            raise RuntimeError("NATS not connected")
            
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
            
        try:
            # Add metadata
            payload["_metadata"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "stream": stream
            }
            
            message = json.dumps(payload).encode()
            
            if self.js and settings.JETSTREAM_ENABLED and stream:
                await self.js.publish(subject, message, stream=stream)
            else:
                await self.nc.publish(subject, message)
                
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

# Global NATS service instance
nats_service = NATSJetStreamService()

async def publish_priority_request(self, task_data: Dict[str, Any], category: str = "") -> bool:
    """Publish prioritization request with at-least-once delivery"""
    if not self.is_connected or not self.js:
        logger.error("NATS/JetStream not connected")
        return False
    
    try:
        subject = f"{settings.PRIORITY_REQUEST_SUBJECT}.{category}" if category else settings.PRIORITY_REQUEST_SUBJECT
        
        # Add metadata
        message_data = {
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "ai-priority-engine",
            "version": "1.0"
        }
        
        # Publish with acknowledgment
        ack = await self.js.publish(
            subject,
            json.dumps(message_data, default=str).encode(),
            timeout=10.0
        )
        
        logger.info(f"📤 Published priority request to {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to publish priority request: {e}")
        return False

async def publish_priority_result(self, result_data: Dict[str, Any], category: str = "") -> bool:
    """Publish prioritization result"""
    if not self.is_connected or not self.js:
        logger.error("NATS/JetStream not connected")
        return False
    
    try:
        subject = f"{settings.PRIORITY_RESULT_SUBJECT}.{category}" if category else settings.PRIORITY_RESULT_SUBJECT
        
        # Add metadata
        message_data = {
            "data": result_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "ai-priority-engine",
            "version": "1.0"
        }
        
        # Publish with acknowledgment
        ack = await self.js.publish(
            subject,
            json.dumps(message_data, default=str).encode(),
            timeout=10.0
        )
        
        logger.info(f"📤 Published priority result: {result_data.get('request_id', 'unknown')} -> {subject}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to publish priority result: {e}")
        return False

async def subscribe_priority_requests(self, callback: Callable):
    """Subscribe to priority requests with durable consumer"""
    if not self.is_connected or not self.js:
        logger.error("NATS/JetStream not connected")
        return
    
    try:
        # Create durable consumer for priority requests
        consumer_config = ConsumerConfig(
            durable_name="priority-processor",
            deliver_policy=DeliverPolicy.ALL,
            ack_policy=AckPolicy.EXPLICIT,
            max_deliver=3,  # Retry up to 3 times
            ack_wait=30,    # 30 second ack timeout
            max_ack_pending=10  # Max unacknowledged messages
        )
        
        # Subscribe to the stream
        subscription = await self.js.subscribe(
            settings.PRIORITY_REQUEST_SUBJECT,
            stream="PRIORITY_REQUESTS",
            config=consumer_config
        )
        
        logger.info(f"🎧 Subscribed to priority requests: {settings.PRIORITY_REQUEST_SUBJECT}")
        
        # Process messages
        async for msg in subscription.messages:
            try:
                # Decode message
                message_data = json.loads(msg.data.decode())
                task_data = message_data.get("data", message_data)  # Support both formats
                
                logger.info(f"📥 Received priority request: {task_data.get('id', 'unknown')}")
                
                # Process with callback
                await callback(task_data)
                
                # Acknowledge message (at-least-once delivery)
                await msg.ack()
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in message: {e}")
                await msg.nak()  # Negative acknowledgment
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
                await msg.nak()  # Will be redelivered
                
    except Exception as e:
        logger.error(f"❌ Error setting up subscription: {e}")
        raise

async def publish_system_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
    """Publish system events for monitoring and audit"""
    if not self.is_connected or not self.js:
        return False
    
    try:
        subject = f"system.events.{event_type}"
        
        message_data = {
            "event_type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "ai-priority-engine"
        }
        
        await self.js.publish(
            subject,
            json.dumps(message_data, default=str).encode(),
            timeout=5.0
        )
        
        logger.debug(f"📊 Published system event: {event_type}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to publish system event: {e}")
        return False
