# 🧠 AI Prioritization Engine - API Documentation

## Overview

The AI Prioritization Engine provides a RESTful API for intelligent task prioritization with automatic metric calculation. The API is designed to be simple to use while providing powerful AI-driven prioritization capabilities.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.prioriti.ai` (if deployed)

## API Versions

- **v1**: Current stable version with full auto-calculation features

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing:
- API keys
- OAuth 2.0
- JWT tokens

## Interactive Documentation

- **Swagger UI**: `/docs` - Interactive API documentation with request/response examples
- **ReDoc**: `/redoc` - Alternative documentation format
- **OpenAPI Spec**: `/openapi.json` - Machine-readable API specification

## Quick Start

### 1. Submit a Task for Prioritization

```bash
curl -X POST "http://localhost:8000/api/v1/prioritization/" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task_001",
    "title": "CFO cannot open PowerPoint presentation", 
    "description": "CFO has board meeting in 45 minutes and cannot open critical financial presentation",
    "category": "MEETING_PREP",
    "requester_role": "CFO",
    "requester_name": "John Smith"
  }'
```

### 2. Get Immediate Priority Assessment

```bash
curl -X POST "http://localhost:8000/api/v1/prioritization/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task_002", 
    "title": "System outage affecting 100+ users",
    "description": "E-commerce platform completely down, customers cannot place orders",
    "category": "INFRASTRUCTURE",
    "requester_role": "MANAGER",
    "requester_name": "Sarah Johnson"
  }'
```

### 3. Check System Health

```bash
curl -X GET "http://localhost:8000/api/v1/health/"
```

## API Endpoints

### Priority Management (`/api/v1/prioritization/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/` | Submit task for async prioritization |
| `POST` | `/sync` | Get immediate priority assessment |
| `GET` | `/status/{task_id}` | Check task processing status |
| `GET` | `/history` | Get prioritization history |

### Health & Monitoring (`/api/v1/health/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Basic health check |
| `GET` | `/detailed` | Extended health with metrics |
| `GET` | `/metrics` | System performance metrics |

### Configuration (`/api/v1/config/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categories` | Task categories and multipliers |
| `GET` | `/roles` | User roles and priority weights |
| `GET` | `/priority-model` | Priority calculation details |
| `GET` | `/thresholds` | System thresholds configuration |

## Request/Response Examples

### Task Submission Request

```json
{
  "id": "task_001",
  "title": "Critical system failure",
  "description": "Database server crashed, affecting all customer transactions",
  "category": "INFRASTRUCTURE",
  "requester_role": "IT_ADMIN", 
  "requester_name": "Alex Thompson",
  "meeting_time": "2025-06-27T15:00:00Z",
  "deadline": "2025-06-27T16:00:00Z",
  "context": "Peak business hours, revenue impact estimated at $10K/hour",
  "tags": ["urgent", "revenue-impact", "customer-facing"]
}
```

### Priority Assessment Response

```json
{
  "request_id": "task_001",
  "urgency_level": "CRITICAL",
  "priority_metrics": {
    "final_priority_score": 8.7,
    "urgency_score": 9.2,
    "business_impact_score": 9.5,
    "risk_score": 8.8,
    "role_weight": 3.0,
    "time_sensitivity_score": 9.8
  },
  "reasoning": "Critical infrastructure failure with high revenue impact during peak hours",
  "ai_confidence": 0.94,
  "suggested_sla_hours": 1.0,
  "escalation_recommended": true,
  "user_suggestions": [
    {
      "title": "Switch to backup database",
      "description": "Activate the standby database server while primary is being repaired",
      "category": "workaround",
      "estimated_resolution_time": "10 minutes",
      "confidence_level": 0.9
    }
  ],
  "next_actions": [
    "Escalate to senior IT staff immediately",
    "Begin resolution within 1.0 hours",
    "Notify stakeholders of incident"
  ],
  "risk_assessment": "High revenue impact, customer satisfaction risk, potential data loss"
}
```

## Automatic Metric Calculation

The AI automatically calculates these metrics from task content:

| Metric | Range | Description |
|--------|-------|-------------|
| **Business Value** | 1-10 | Impact on business operations |
| **Risk Level** | 1-10 | Security, operational, and reputational risk |
| **Effort Hours** | 0.1-100+ | Estimated time to resolve |
| **Affected Users** | 1-10000+ | Number of impacted users |
| **Workaround Available** | true/false | Alternative solution likelihood |

### How Metrics Are Calculated

1. **Content Analysis**: AI analyzes task title, description, and context
2. **Keyword Detection**: Security terms, impact indicators, urgency signals
3. **Role Weighting**: Executive roles increase business value
4. **Category Multipliers**: Security and infrastructure get higher priority
5. **Time Sensitivity**: Meeting times and deadlines affect urgency

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `202` | Accepted (async processing) |
| `400` | Bad Request (invalid input) |
| `404` | Not Found |
| `500` | Internal Server Error |
| `503` | Service Unavailable |

### Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-27T14:30:00Z"
}
```

## Rate Limiting

- **Concurrent Requests**: 10 simultaneous requests
- **Request Timeout**: 30 seconds
- **Processing Time**: Max 120 seconds for complex analysis

## GDPR Compliance

- **Sensitive Data Detection**: Automatically detects PII, financial data, credentials
- **Local Processing**: Sensitive tasks processed without external AI calls
- **Data Retention**: Configure retention policies in environment settings
- **Audit Logging**: All sensitive data handling is logged

## Integration Examples

### Python

```python
import requests

def prioritize_task(task_data):
    response = requests.post(
        "http://localhost:8000/api/v1/prioritization/sync",
        json=task_data
    )
    return response.json()

# Example usage
task = {
    "id": "urgent_001",
    "title": "CEO laptop not working", 
    "description": "CEO's laptop won't start before important client meeting",
    "category": "SUPPORT",
    "requester_role": "CEO",
    "requester_name": "Maria Garcia"
}

result = prioritize_task(task)
print(f"Priority: {result['urgency_level']}")
print(f"SLA: {result['suggested_sla_hours']} hours")
```

### JavaScript/Node.js

```javascript
async function prioritizeTask(taskData) {
  const response = await fetch('http://localhost:8000/api/v1/prioritization/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskData)
  });
  return response.json();
}

// Example usage
const task = {
  id: 'urgent_002',
  title: 'Server room temperature alarm',
  description: 'Data center cooling system failed, temperature rising rapidly',
  category: 'INFRASTRUCTURE',
  requester_role: 'IT_ADMIN',
  requester_name: 'David Kim'
};

prioritizeTask(task).then(result => {
  console.log(`Priority: ${result.urgency_level}`);
  console.log(`Escalate: ${result.escalation_recommended}`);
});
```

### cURL Scripts

```bash
#!/bin/bash
# Submit multiple tasks for processing

TASKS=(
  '{"id":"task_1","title":"Email server down","description":"Users cannot send/receive emails","category":"INFRASTRUCTURE","requester_role":"IT_ADMIN","requester_name":"Admin"}'
  '{"id":"task_2","title":"CEO presentation issue","description":"Slides not displaying correctly for board meeting","category":"MEETING_PREP","requester_role":"CEO","requester_name":"CEO"}'
)

for task in "${TASKS[@]}"; do
  curl -X POST "http://localhost:8000/api/v1/prioritization/" \
    -H "Content-Type: application/json" \
    -d "$task"
  echo ""
done
```

## Monitoring and Observability

### Health Check Monitoring

```bash
# Basic health check
curl http://localhost:8000/api/v1/health/

# Detailed health with performance metrics
curl http://localhost:8000/api/v1/health/detailed

# System performance metrics
curl http://localhost:8000/api/v1/health/metrics
```

### Configuration Monitoring

```bash
# Check priority model configuration
curl http://localhost:8000/api/v1/config/priority-model

# Check system thresholds
curl http://localhost:8000/api/v1/config/thresholds
```

## WebSocket Support (Future)

Planning for real-time updates:

```javascript
// Future WebSocket implementation
const ws = new WebSocket('ws://localhost:8000/ws/prioritization');

ws.onmessage = function(event) {
  const update = JSON.parse(event.data);
  console.log(`Task ${update.task_id} priority updated: ${update.priority_score}`);
};
```

## Security Considerations

### Production Deployment

1. **HTTPS Only**: Always use SSL/TLS in production
2. **API Authentication**: Implement proper authentication
3. **Rate Limiting**: Configure appropriate limits
4. **Input Validation**: Validate all inputs server-side
5. **CORS Configuration**: Restrict origins appropriately

### Data Privacy

1. **PII Detection**: Automatic sensitive data detection
2. **Data Encryption**: Encrypt data at rest and in transit
3. **Access Logging**: Log all API access for auditing
4. **Data Retention**: Implement appropriate retention policies

## Support and Troubleshooting

### Common Issues

1. **Redis Connection Failed**: Ensure Redis is running on port 6379
2. **OpenAI API Error**: Verify API key configuration
3. **Slow Response Times**: Check system load and Redis performance
4. **Invalid Category**: Use only supported category values

### Debug Mode

Enable debug logging in development:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Health Check Failures

If health checks fail:

1. Check Redis connectivity: `redis-cli ping`
2. Verify OpenAI API key: Check `.env` configuration
3. Review application logs for errors
4. Ensure all dependencies are installed

---

For additional support, check the health endpoint at `/api/v1/health/` or review the interactive documentation at `/docs`.
