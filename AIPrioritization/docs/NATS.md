# 🚀 NATS Integration Guide for AI Prioritization Engine

## Overview

While the current implementation uses Redis for pub/sub messaging, this guide outlines how to integrate NATS.io for enterprise-grade messaging and event streaming in the AI Prioritization Engine.

## Why NATS?

NATS provides several advantages for microservice architectures:

- **High Performance**: Million+ messages per second
- **Lightweight**: Minimal resource footprint
- **Cloud Native**: Kubernetes-ready with operators
- **Clustering**: Built-in clustering and high availability
- **JetStream**: Persistent streaming with at-least-once delivery
- **Request/Reply**: Synchronous communication patterns

## NATS vs Redis Comparison

| Feature | NATS | Redis |
|---------|------|-------|
| **Performance** | 10M+ msg/sec | 1M+ msg/sec |
| **Memory Usage** | ~10MB | ~50MB+ |
| **Clustering** | Native | Redis Cluster |
| **Persistence** | JetStream | RDB/AOF |
| **Delivery Guarantees** | At-least-once, exactly-once | Fire-and-forget |
| **Security** | TLS, Auth, Authorization | AUTH, TLS |

## Implementation Plan

### Phase 1: NATS Core Integration

Replace Redis pub/sub with NATS core for basic messaging:

```python
# services/nats_service.py
import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError
from core.config import settings

class NATSService:
    def __init__(self):
        self.nc = None
        
    async def connect(self):
        """Connect to NATS server"""
        self.nc = await nats.connect(
            servers=[f"nats://{settings.NATS_HOST}:{settings.NATS_PORT}"],
            name="ai-priority-engine",
            reconnect_time_wait=2,
            max_reconnect_attempts=10,
            ping_interval=20,
            max_outstanding_pings=5,
        )
        
    async def publish_priority_request(self, task_data: str):
        """Publish prioritization request"""
        await self.nc.publish("prioritization.request", task_data.encode())
        
    async def publish_priority_result(self, result_data: str):
        """Publish prioritization result"""
        await self.nc.publish("prioritization.result", result_data.encode())
        
    async def subscribe_priority_requests(self, callback):
        """Subscribe to prioritization requests"""
        await self.nc.subscribe("prioritization.request", cb=callback)
        
    async def close(self):
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
```

### Phase 2: JetStream for Persistence

Add persistent messaging with delivery guarantees:

```python
# services/jetstream_service.py
import asyncio
import nats
from nats.js import JetStreamContext
from nats.js.api import ConsumerConfig, DeliverPolicy

class JetStreamService:
    def __init__(self):
        self.nc = None
        self.js = None
        
    async def setup_streams(self):
        """Create JetStream streams for persistent messaging"""
        
        # Priority requests stream
        await self.js.add_stream(
            name="PRIORITY_REQUESTS",
            subjects=["prioritization.request.*"],
            retention="workqueue",  # Messages deleted after acknowledgment
            max_age=86400,  # 24 hours
            storage="file"
        )
        
        # Priority results stream  
        await self.js.add_stream(
            name="PRIORITY_RESULTS", 
            subjects=["prioritization.result.*"],
            retention="limits",
            max_age=604800,  # 7 days
            storage="file"
        )
        
    async def publish_with_ack(self, subject: str, data: bytes):
        """Publish with acknowledgment"""
        ack = await self.js.publish(subject, data)
        return ack
        
    async def create_durable_consumer(self, stream: str, consumer: str):
        """Create durable consumer for reliable processing"""
        await self.js.add_consumer(
            stream=stream,
            config=ConsumerConfig(
                durable_name=consumer,
                deliver_policy=DeliverPolicy.ALL,
                ack_policy="explicit",
                max_deliver=3,  # Retry up to 3 times
                ack_wait=30,    # 30 second ack timeout
            )
        )
```

### Phase 3: Request/Reply Pattern

Implement synchronous request/reply for immediate responses:

```python
# services/request_reply_service.py
class RequestReplyService:
    def __init__(self, nats_service: NATSService):
        self.nc = nats_service.nc
        
    async def handle_sync_requests(self):
        """Handle synchronous prioritization requests"""
        async def request_handler(msg):
            try:
                # Parse request
                task_data = json.loads(msg.data.decode())
                task_request = TaskRequest(**task_data)
                
                # Process with AI
                ai_result = await get_ai_priority(task_request)
                
                # Reply with result
                await msg.respond(ai_result.model_dump_json().encode())
                
            except Exception as e:
                error_response = {"error": str(e)}
                await msg.respond(json.dumps(error_response).encode())
                
        await self.nc.subscribe("prioritization.sync", cb=request_handler)
        
    async def make_sync_request(self, task_data: dict, timeout: int = 30):
        """Make synchronous prioritization request"""
        try:
            msg = await self.nc.request(
                "prioritization.sync",
                json.dumps(task_data).encode(),
                timeout=timeout
            )
            return json.loads(msg.data.decode())
        except TimeoutError:
            raise HTTPException(status_code=408, detail="Request timeout")
```

## Configuration

### Environment Variables

Add NATS configuration to `.env`:

```bash
# NATS Configuration
NATS_HOST=localhost
NATS_PORT=4222
NATS_CLUSTER_HOST=nats://nats-cluster:4222
NATS_USERNAME=priority_engine
NATS_PASSWORD=secure_password
NATS_TLS_ENABLED=true
NATS_TLS_CERT_PATH=/certs/client.crt
NATS_TLS_KEY_PATH=/certs/client.key

# JetStream Configuration
JETSTREAM_ENABLED=true
JETSTREAM_DOMAIN=priority
JETSTREAM_MAX_MEMORY=1GB
JETSTREAM_MAX_STORAGE=10GB

# Subjects and Streams
PRIORITY_REQUEST_SUBJECT=prioritization.request
PRIORITY_RESULT_SUBJECT=prioritization.result
PRIORITY_SYNC_SUBJECT=prioritization.sync
```

### Docker Compose

Add NATS server to your deployment:

```yaml
# docker-compose.yml
version: '3.8'

services:
  nats:
    image: nats:latest
    ports:
      - "4222:4222"   # Client connections
      - "8222:8222"   # HTTP monitoring
      - "6222:6222"   # Cluster routes
    command: >
      --jetstream
      --store_dir=/data
      --max_memory_store=1GB
      --max_file_store=10GB
      --http_port=8222
    volumes:
      - nats_data:/data
    restart: unless-stopped
    
  ai-priority-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NATS_HOST=nats
      - NATS_PORT=4222
      - JETSTREAM_ENABLED=true
    depends_on:
      - nats
    restart: unless-stopped

volumes:
  nats_data:
```

## Message Schemas

### Priority Request

```json
{
  "subject": "prioritization.request.{category}",
  "data": {
    "id": "task_001",
    "title": "System failure",
    "description": "Critical database outage",
    "category": "INFRASTRUCTURE", 
    "requester_role": "IT_ADMIN",
    "requester_name": "John Doe",
    "timestamp": "2025-06-27T14:30:00Z",
    "correlation_id": "req_123456"
  }
}
```

### Priority Result

```json
{
  "subject": "prioritization.result.{category}",
  "data": {
    "request_id": "task_001",
    "correlation_id": "req_123456",
    "urgency_level": "CRITICAL",
    "priority_score": 8.7,
    "processing_time_ms": 1250,
    "timestamp": "2025-06-27T14:30:01Z"
  }
}
```

## Monitoring and Observability

### NATS Monitoring

NATS provides built-in monitoring at `http://localhost:8222`:

```bash
# Server info
curl http://localhost:8222/varz

# Connection info  
curl http://localhost:8222/connz

# JetStream info
curl http://localhost:8222/jsz
```

### Health Checks

Update health checks to include NATS:

```python
# api/v1/health.py
async def check_nats_health():
    """Check NATS connectivity and JetStream status"""
    try:
        # Test connection
        nc = await nats.connect(f"nats://{settings.NATS_HOST}:{settings.NATS_PORT}")
        
        # Test JetStream
        js = nc.jetstream()
        streams = await js.streams_info()
        
        await nc.close()
        
        return {
            "status": "healthy",
            "streams": len(streams),
            "jetstream_enabled": True
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }
```

## Performance Tuning

### Connection Pool

```python
class NATSConnectionPool:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.connections = []
        
    async def get_connection(self):
        """Get connection from pool"""
        if not self.connections:
            for _ in range(self.pool_size):
                nc = await nats.connect(
                    servers=[f"nats://{settings.NATS_HOST}:{settings.NATS_PORT}"]
                )
                self.connections.append(nc)
        return self.connections.pop()
        
    async def return_connection(self, nc):
        """Return connection to pool"""
        self.connections.append(nc)
```

### Message Batching

```python
class BatchProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_messages = []
        
    async def add_message(self, subject: str, data: bytes):
        """Add message to batch"""
        self.pending_messages.append((subject, data))
        
        if len(self.pending_messages) >= self.batch_size:
            await self.flush_batch()
            
    async def flush_batch(self):
        """Send all pending messages"""
        for subject, data in self.pending_messages:
            await self.js.publish(subject, data)
        self.pending_messages.clear()
```

## Security

### TLS Configuration

```python
# TLS connection
nc = await nats.connect(
    servers=["nats://nats-server:4222"],
    tls=tls_context,  # SSL context
    tls_hostname="nats-server"
)
```

### Authentication

```python
# Username/password auth
nc = await nats.connect(
    servers=["nats://nats-server:4222"],
    user="priority_engine",
    password="secure_password"
)

# Token auth
nc = await nats.connect(
    servers=["nats://nats-server:4222"], 
    token="jwt_token_here"
)

# NKey auth
nc = await nats.connect(
    servers=["nats://nats-server:4222"],
    nkeys_seed="path/to/nkey.seed"
)
```

## Migration Strategy

### Phase 1: Parallel Operation

Run both Redis and NATS simultaneously:

```python
class DualMessagingService:
    def __init__(self):
        self.redis_service = RedisService()
        self.nats_service = NATSService()
        
    async def publish_priority_request(self, data: str):
        """Publish to both Redis and NATS"""
        await asyncio.gather(
            self.redis_service.publish(data),
            self.nats_service.publish_priority_request(data)
        )
```

### Phase 2: Gradual Migration

Gradually shift traffic from Redis to NATS:

```python
class GradualMigrationService:
    def __init__(self, nats_percentage: int = 50):
        self.nats_percentage = nats_percentage
        
    async def route_message(self, data: str):
        """Route percentage of traffic to NATS"""
        if random.randint(1, 100) <= self.nats_percentage:
            await self.nats_service.publish(data)
        else:
            await self.redis_service.publish(data)
```

### Phase 3: Complete Migration

Remove Redis dependencies and use NATS exclusively.

## Deployment Considerations

### Kubernetes

```yaml
# k8s/nats-cluster.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nats-config
data:
  nats.conf: |
    port: 4222
    http_port: 8222
    
    jetstream {
      store_dir: /data
      max_memory_store: 1GB
      max_file_store: 10GB
    }
    
    cluster {
      name: priority-cluster
      port: 6222
      routes = [
        nats://nats-0.nats:6222
        nats://nats-1.nats:6222  
        nats://nats-2.nats:6222
      ]
    }
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nats
spec:
  serviceName: nats
  replicas: 3
  selector:
    matchLabels:
      app: nats
  template:
    metadata:
      labels:
        app: nats
    spec:
      containers:
      - name: nats
        image: nats:latest
        ports:
        - containerPort: 4222
          name: client
        - containerPort: 6222
          name: cluster
        - containerPort: 8222
          name: monitor
        volumeMounts:
        - name: config-volume
          mountPath: /etc/nats
        - name: data-volume
          mountPath: /data
        command:
        - "nats-server"
        - "--config"
        - "/etc/nats/nats.conf"
      volumes:
      - name: config-volume
        configMap:
          name: nats-config
  volumeClaimTemplates:
  - metadata:
      name: data-volume
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## Benefits of NATS Integration

1. **Scalability**: Handle millions of messages per second
2. **Reliability**: JetStream provides persistent messaging
3. **Efficiency**: Lower latency and memory usage
4. **Flexibility**: Support for multiple messaging patterns
5. **Observability**: Built-in monitoring and metrics
6. **Cloud Native**: Kubernetes operators and Helm charts

## Next Steps

1. **Prototype**: Implement basic NATS pub/sub alongside Redis
2. **Benchmark**: Compare performance between Redis and NATS
3. **JetStream**: Add persistent messaging for critical workflows
4. **Monitoring**: Integrate NATS metrics into observability stack
5. **Migration**: Plan gradual migration from Redis to NATS

---

For more information, see:
- [NATS Documentation](https://docs.nats.io/)
- [JetStream Guide](https://docs.nats.io/nats-concepts/jetstream)
- [NATS Python Client](https://github.com/nats-io/nats.py)
