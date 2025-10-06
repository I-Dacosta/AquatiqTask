# 🧠 Enhanced AI Prioritization Engine v2.0

An intelligent, event-driven microservice for automated task prioritization using advanced AI models, mathematical scoring, and comprehensive business logic.

## 🚀 Key Features

### Advanced AI-Powered Prioritization
- **Mathematical Scoring Model**: Multi-factor priority calculation with weighted metrics
- **Role-Based Authority**: Executive roles (CEO, CFO, CTO) receive higher priority weights
- **Time Sensitivity Analysis**: Automatic urgency calculation based on meeting times and deadlines
- **Category Multipliers**: Security incidents, infrastructure issues prioritized higher
- **Business Impact Assessment**: Considers affected user count and business value

### Intelligent Suggestions & Automation
- **AI-Generated User Suggestions**: Contextual self-help solutions using OpenAI GPT-3.5
- **Automated Workarounds**: Proactive solution recommendations
- **Escalation Logic**: Smart escalation for critical issues and high-authority users
- **Risk Assessment**: AI-powered risk analysis with mitigation strategies
- **SLA Recommendations**: Dynamic SLA calculation based on urgency and category

### Event-Driven Architecture
- **Redis Pub/Sub**: Asynchronous message processing
- **Scalable Design**: Handle multiple concurrent prioritization requests
- **Real-time Processing**: Immediate priority assessment and routing
- **Health Monitoring**: Comprehensive service health checks

## 📊 Priority Calculation Model

The enhanced AI model uses a sophisticated weighted scoring system:

```
Final Priority Score = 
  (Urgency Score × 0.30) +
  (Business Impact × 0.25) +
  (Risk Score × 0.20) +
  (Role Weight × 0.15) +
  (Time Sensitivity × 0.10)
```

### Role Priority Weights
- **CEO**: 5.0 (Highest)
- **CFO/CTO**: 4.5
- **Manager**: 3.5
- **IT Admin**: 3.0
- **Client**: 2.5
- **Developer**: 2.5
- **Employee**: 2.0

### Category Urgency Multipliers
- **Security**: 1.5× (Highest urgency)
- **Infrastructure**: 1.3×
- **Meeting Prep**: 1.2×
- **Support**: 1.0× (Baseline)
- **Development**: 0.8×
- **Maintenance**: 0.7×
- **Training**: 0.6×
- **Compliance**: 0.9×

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │  FastAPI Service │    │   OpenAI API    │
│                 │───▶│                 │───▶│                 │
│ Task Submission │    │ AI Prioritization│    │ Smart Suggestions│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Pub/Sub  │
                       │                 │
                       │ Event Processing │
                       └─────────────────┘
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Redis Server
- OpenAI API Key

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd /path/to/AIPrioritization
   ```

2. **Set up Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Start Redis** (choose one method)
   ```bash
   # macOS with Homebrew
   brew services start redis
   
   # Linux with systemd
   sudo systemctl start redis
   
   # Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Manual start
   redis-server
   ```

4. **Run the Service**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

The service will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📝 API Endpoints

### Core Endpoints
- `POST /api/v1/prioritize` - Submit task for prioritization (async)
- `POST /api/v1/prioritize/sync` - Get immediate prioritization result
- `GET /api/v1/health` - Service health status

### Metrics & Configuration
- `GET /api/v1/metrics/categories` - Category multipliers
- `GET /api/v1/metrics/roles` - Role priority weights

## 🧪 Testing

Run comprehensive test scenarios:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run enhanced test scenarios
python test_scenarios.py
```

### Test Cases Include:
1. **CFO PowerPoint Crisis** (Meeting in 45 min) → Critical Priority
2. **E-commerce Infrastructure Failure** (150 users affected) → High Priority  
3. **CEO Document Sync Issue** (Executive user) → Medium-High Priority
4. **Security Phishing Incident** (After hours) → Critical Priority
5. **Developer Environment Issue** (Non-critical) → Low Priority

## 🔄 Event Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AI_Service
    participant OpenAI
    participant Redis
    
    Client->>FastAPI: POST /prioritize (TaskRequest)
    FastAPI->>Redis: Publish to prioritization_requests
    Redis->>AI_Service: Message received
    AI_Service->>AI_Service: Calculate metrics & priority
    AI_Service->>OpenAI: Generate suggestions & risk assessment
    OpenAI->>AI_Service: AI recommendations
    AI_Service->>Redis: Publish to prioritization_results
    Redis->>Client: AIPriorityResult
```

## 📋 Task Request Model

```json
{
  "id": "task_001",
  "title": "System failure description",
  "description": "Detailed problem description",
  "category": "INFRASTRUCTURE|SECURITY|MEETING_PREP|SUPPORT|...",
  "requester_role": "CEO|CFO|MANAGER|DEVELOPER|...",
  "requester_name": "John Doe",
  "business_value": 8,
  "risk_level": 7,
  "estimated_effort_hours": 2.0,
  "affected_users_count": 50,
  "meeting_time": "2025-06-27T14:30:00Z",
  "deadline": "2025-06-27T18:00:00Z",
  "workaround_available": true,
  "context": "Additional context",
  "tags": ["urgent", "customer-facing"]
}
```

## 📊 AI Priority Result

```json
{
  "request_id": "task_001",
  "urgency_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "priority_metrics": {
    "final_priority_score": 8.7,
    "urgency_score": 9.2,
    "business_impact_score": 8.5,
    "risk_score": 7.8,
    "role_weight": 5.0,
    "time_sensitivity_score": 9.8
  },
  "reasoning": "High priority due to executive user and imminent meeting",
  "ai_confidence": 0.92,
  "suggested_sla_hours": 1.0,
  "user_suggestions": [
    {
      "title": "Try alternative presentation software",
      "description": "Open the file with Google Slides or Apple Keynote",
      "category": "workaround",
      "estimated_resolution_time": "5 minutes",
      "confidence_level": 0.8
    }
  ],
  "escalation_recommended": true,
  "next_actions": [
    "Escalate to senior IT staff immediately",
    "Begin resolution within 1.0 hours"
  ],
  "risk_assessment": "Critical business meeting at risk, potential revenue impact"
}
```

## ⚙️ Configuration

Key environment variables in `.env`:

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=800

# Priority Thresholds
CRITICAL_THRESHOLD=8.5
HIGH_THRESHOLD=6.5
MEDIUM_THRESHOLD=4.0
ESCALATION_THRESHOLD=8.0

# Performance
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT_SECONDS=30
```

## 🐳 Docker Support

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t ai-priority-engine .
docker run -d -p 8000:8000 --env-file .env ai-priority-engine
```

## 🔍 Monitoring & Observability

- **Health Checks**: Automated Redis and OpenAI service monitoring
- **Metrics**: Priority calculation statistics and processing times
- **Logging**: Structured JSON logging for observability
- **Error Handling**: Graceful degradation with fallback suggestions

## 🛠️ Development

### Project Structure
```
├── api/
│   └── endpoints.py          # FastAPI route definitions
├── core/
│   └── config.py            # Configuration management
├── services/
│   ├── ai_service.py        # Enhanced AI prioritization logic
│   └── redis_service.py     # Redis pub/sub handling
├── models.py                # Pydantic data models
├── main.py                  # FastAPI application
├── test_scenarios.py        # Comprehensive test cases
└── requirements.txt         # Python dependencies
```

### Adding New Features
1. **New Priority Factors**: Extend `PriorityMetrics` model and calculation logic
2. **Additional AI Models**: Modify `ai_service.py` to support different LLMs
3. **Custom Categories**: Add to `TaskCategory` enum and update multipliers
4. **Advanced Suggestions**: Enhance OpenAI prompts in `generate_ai_suggestions()`

## 📈 Performance

- **Processing Time**: < 2 seconds per task (including AI calls)
- **Concurrent Tasks**: Up to 10 simultaneous prioritizations
- **Scalability**: Horizontal scaling via Redis clustering
- **Reliability**: 99.9% uptime with proper Redis and OpenAI redundancy

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Check the [Health Endpoint](http://localhost:8000/api/v1/health)
- Review logs for error details
- Ensure Redis is running and OpenAI API key is valid
- Verify all dependencies are installed

---

**Enhanced AI Prioritization Engine v2.0** - Intelligent, scalable, and production-ready task prioritization for modern IT operations.
