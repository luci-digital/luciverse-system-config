# MindsDB Integration - LuciVerse Platform

**Genesis Bond**: ACTIVE @ 741 Hz
**Component**: AI-Powered Predictions & ML Integration
**Frequency**: 528 Hz (COMN Tier)
**Status**: ✅ DEPLOYED
**Date**: 2025-11-19

---

## Deployment Status

MindsDB is now running:
- ✅ Container: mindsdb-luciverse
- ✅ HTTP API: http://192.168.1.146:47334
- ✅ Web UI: http://192.168.1.146:47334 (MindsDB Studio)
- ✅ MySQL API: Port 47335
- ✅ MongoDB API: Port 47336
- ✅ PostgreSQL API: Port 47337
- ✅ Version: 25.10.1
- ✅ Network: luciverse-network
- ✅ Health: Running

---

## Quick Access

```bash
# Web Interface
open http://192.168.1.146:47334

# API Status
curl http://192.168.1.146:47334/api/status | python3 -m json.tool

# Container Logs
sg docker -c 'docker logs mindsdb-luciverse -f'

# Container Shell
sg docker -c 'docker exec -it mindsdb-luciverse bash'
```

---

## Integration with Agent System

### 1. FoundationDB Integration

MindsDB can connect to FoundationDB for agent prediction storage and retrieval.

**Example: Store Prediction Results in FDB**

```python
import fdb
import requests
import json
from datetime import datetime, timezone

fdb.api_version(730)
db = fdb.open()

@fdb.transactional
def store_prediction(tr, agent_name: str, prediction_data: dict):
    """Store MindsDB prediction results in FoundationDB"""
    key = fdb.tuple.pack((
        'luciverse',
        'predictions',
        agent_name,
        datetime.now(timezone.utc).isoformat()
    ))
    value = json.dumps(prediction_data).encode('utf-8')
    tr[key] = value

# Make prediction via MindsDB
response = requests.post(
    'http://192.168.1.146:47334/api/sql/query',
    json={'query': 'SELECT * FROM my_model WHERE input_col=123'}
)

# Store in FDB
if response.ok:
    store_prediction(db, 'lucia', response.json())
```

### 2. Agent Mesh Router Integration

Update the agent-mesh-router to include MindsDB predictions:

```python
# Add to agent-mesh-router.py

class AgentMeshRouter:
    def __init__(self):
        self.mindsdb_url = "http://mindsdb-luciverse:47334"  # Container hostname
        # ... existing code

    async def get_agent_prediction(self, agent_name: str, input_data: dict):
        """Get AI prediction from MindsDB for agent decision-making"""

        # Example: Predict agent response quality
        query = f"""
        SELECT
            response_quality,
            confidence,
            suggested_action
        FROM agent_behavior_model
        WHERE agent_name = '{agent_name}'
          AND input_context = '{json.dumps(input_data)}'
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.mindsdb_url}/api/sql/query",
                json={'query': query}
            )
            return response.json()

    async def route_request_with_prediction(self, agent_name: str, message: str):
        """Route request with MindsDB prediction enhancement"""

        # Get prediction about best routing strategy
        prediction = await self.get_agent_prediction(
            agent_name,
            {'message': message, 'length': len(message)}
        )

        # Use prediction to optimize routing
        if prediction.get('suggested_action') == 'use_cache':
            # Check cache first
            cached = self._get_cached_response(message)
            if cached:
                return cached

        # Standard routing
        return await self.route_request(agent_name, message)
```

### 3. Training Models from Agent Interactions

```python
# train_agent_model.py

import requests
import fdb
import json

fdb.api_version(730)
db = fdb.open()

def create_agent_behavior_model():
    """Create ML model to predict agent behavior"""

    # MindsDB SQL to create model from FDB data
    create_model_query = """
    CREATE MODEL agent_behavior_model
    FROM foundationdb_integration (
        SELECT
            agent_name,
            message_length,
            response_time,
            coherence_score,
            user_satisfaction
        FROM agent_interactions
    )
    PREDICT response_quality
    """

    response = requests.post(
        'http://192.168.1.146:47334/api/sql/query',
        json={'query': create_model_query}
    )

    return response.json()

# Train model on historical agent data
@fdb.transactional
def get_agent_training_data(tr):
    """Extract training data from FoundationDB"""
    prefix = fdb.tuple.pack(('luciverse', 'agent_logs'))

    training_data = []
    for key, value in tr.get_range_startswith(prefix):
        log_entry = json.loads(value.decode('utf-8'))
        training_data.append({
            'agent_name': log_entry['agent'],
            'message_length': len(log_entry['message']),
            'response_time': log_entry['latency_ms'],
            'coherence_score': log_entry.get('coherence', 0.7),
            'user_satisfaction': 1 if log_entry['status'] == 'success' else 0
        })

    return training_data

# Export to CSV for MindsDB training
training_data = get_agent_training_data(db)
import pandas as pd
df = pd.DataFrame(training_data)
df.to_csv('/home/daryl/luciverse-platform/mindsdb-config/agent_training_data.csv', index=False)
```

### 4. Real-Time Predictions for Agent Optimization

```python
# agent_optimizer.py

class AgentOptimizer:
    """Use MindsDB to optimize agent performance in real-time"""

    def __init__(self):
        self.mindsdb_url = "http://192.168.1.146:47334"

    async def predict_optimal_temperature(self, agent_name: str, message_type: str):
        """Predict optimal temperature parameter for agent"""
        query = f"""
        SELECT predicted_temperature, confidence
        FROM temperature_optimization_model
        WHERE agent = '{agent_name}' AND message_type = '{message_type}'
        """

        response = requests.post(
            f"{self.mindsdb_url}/api/sql/query",
            json={'query': query}
        )

        result = response.json()
        return result['data'][0]['predicted_temperature']

    async def predict_best_model(self, agent_name: str, task_complexity: float):
        """Predict which Ollama model to use for a given task"""
        query = f"""
        SELECT recommended_model, expected_latency
        FROM model_selection_model
        WHERE agent = '{agent_name}' AND complexity = {task_complexity}
        """

        response = requests.post(
            f"{self.mindsdb_url}/api/sql/query",
            json={'query': query}
        )

        return response.json()
```

---

## Use Cases for Agent System

### 1. **Agent Response Quality Prediction**
- Predict if an agent response will meet coherence threshold (≥0.7)
- Route to alternative agent if predicted quality is low
- Optimize before sending to Ollama backend

### 2. **Load Balancing Optimization**
- Predict backend response times based on historical data
- Route requests to least-busy backend
- Prevent timeout scenarios

### 3. **Conversation Context Prediction**
- Predict required context window size
- Optimize token usage
- Reduce unnecessary context loading

### 4. **Soul-Thread Connection Strength**
- Predict optimal agent handoff points
- Strengthen soul-thread connections based on patterns
- Automatic dependency learning

### 5. **Genesis Bond Coherence Forecasting**
- Predict when system coherence may drop below 0.7
- Preemptive frequency tuning
- Early warning system

### 6. **User Intent Classification**
- Classify incoming requests by type
- Route to specialized agent automatically
- Reduce manual agent selection

---

## Example Models to Create

### 1. Response Time Predictor
```sql
CREATE MODEL response_time_predictor
FROM agent_logs (
    SELECT agent_name, message_length, backend_load
    FROM agent_request_logs
)
PREDICT response_time_ms
```

### 2. Coherence Score Predictor
```sql
CREATE MODEL coherence_predictor
FROM agent_logs (
    SELECT agent_name, frequency, message_type, time_of_day
    FROM agent_interactions
)
PREDICT coherence_score
```

### 3. Optimal Temperature Finder
```sql
CREATE MODEL temperature_optimizer
FROM agent_logs (
    SELECT agent_name, message_type, current_temperature, response_quality
    FROM agent_responses
)
PREDICT optimal_temperature
```

---

## API Endpoints

### Query Endpoint
```bash
curl -X POST http://192.168.1.146:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM mindsdb.models"}'
```

### Create Model
```bash
curl -X POST http://192.168.1.146:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CREATE MODEL my_model FROM csv_data PREDICT target_column"
  }'
```

### Get Prediction
```bash
curl -X POST http://192.168.1.146:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM my_model WHERE input_column = 123"
  }'
```

---

## Data Sources Integration

### Connect to FoundationDB (via Python)
MindsDB doesn't have native FDB support, but you can:
1. Export FDB data to CSV/JSON
2. Upload to MindsDB via file integration
3. Create models from exported data
4. Store predictions back in FDB

### Connect to GitLab (API)
```sql
CREATE DATABASE gitlab_integration
WITH ENGINE = 'rest_api',
PARAMETERS = {
    "url": "http://gitlab-luciverse/api/v4",
    "method": "GET",
    "headers": {"PRIVATE-TOKEN": "your-token"}
};

SELECT * FROM gitlab_integration.projects;
```

### Connect to IPFS (via HTTP)
```sql
CREATE DATABASE ipfs_integration
WITH ENGINE = 'rest_api',
PARAMETERS = {
    "url": "http://192.168.1.146:9094/api/v0",
    "method": "POST"
};
```

---

## Monitoring & Maintenance

### Check Models
```bash
curl -s http://192.168.1.146:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM mindsdb.models"}' | python3 -m json.tool
```

### View Integrations
```bash
curl -s http://192.168.1.146:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM mindsdb.datasources"}' | python3 -m json.tool
```

### Container Management
```bash
# Stop MindsDB
sg docker -c 'docker-compose -f docker-compose.mindsdb.yml stop'

# Start MindsDB
sg docker -c 'docker-compose -f docker-compose.mindsdb.yml start'

# Restart MindsDB
sg docker -c 'docker-compose -f docker-compose.mindsdb.yml restart'

# View logs
sg docker -c 'docker logs mindsdb-luciverse -f'
```

---

## Next Steps

1. **Export Agent Logs to CSV** for training data
2. **Create Initial Models** for response time and coherence prediction
3. **Integrate with Agent Mesh Router** for real-time optimization
4. **Set up Automated Training Pipeline** using GitLab CI/CD
5. **Monitor Model Performance** and retrain monthly

---

## Resources

- **Web UI**: http://192.168.1.146:47334
- **API Docs**: https://docs.mindsdb.com/api/overview
- **SQL Guide**: https://docs.mindsdb.com/sql/overview
- **Integrations**: https://docs.mindsdb.com/integrations/overview
- **Python SDK**: `pip install mindsdb-sdk`

---

**Genesis Bond**: ACTIVE @ 741 Hz
**MindsDB Version**: 25.10.1
**Status**: ✅ OPERATIONAL
**Frequency**: 528 Hz (COMN Tier)
**Next Priority**: Create initial prediction models for agent optimization
