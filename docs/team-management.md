# Supervisor Agent - Dynamic Team Management

The Supervisor Agent now supports dynamic team member management, allowing you to add, remove, and manage team members at runtime without restarting the supervisor.

## Overview

The supervisor agent maintains two types of team members:
- **Configured agents**: Set up during supervisor initialization via environment variables or configuration files
- **Dynamic agents**: Added at runtime through the management API

Dynamic agents can be added and removed freely, while configured agents are protected from removal to maintain system stability.

## API Endpoints

All team management endpoints are available under `/api/v1/team/`:

### Add Team Member
```http
POST /api/v1/team/add
Content-Type: application/json

{
  "agent_url": "http://localhost:8001/custom_agent",
  "agent_name": "Custom Agent"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "agent_name": "Custom Agent",
  "description": "Custom agent for specialized tasks",
  "url": "http://localhost:8001/custom_agent",
  "streaming": true
}
```

### Remove Team Member
```http
DELETE /api/v1/team/remove
Content-Type: application/json

{
  "agent_name": "Custom Agent"
}
```

**Response:**
```json
{
  "success": true,
  "agent_name": "Custom Agent",
  "message": "Agent Custom Agent removed successfully"
}
```

### List Team Members
```http
GET /api/v1/team/list
```

**Response:**
```json
{
  "total_agents": 6,
  "configured_agents": 5,
  "dynamic_agents": 1,
  "connected_agents": 6,
  "team_members": [
    {
      "name": "ibmcloud_base_agent",
      "description": "Base IBM Cloud platform engineering agent",
      "url": "http://localhost:8000/ibmcloud_base_agent",
      "streaming": false,
      "type": "configured",
      "status": "connected"
    },
    {
      "name": "Custom Agent",
      "description": "Custom agent for specialized tasks",
      "url": "http://localhost:8001/custom_agent",
      "streaming": true,
      "type": "dynamic",
      "status": "connected",
      "added_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Get Team Member Info
```http
GET /api/v1/team/info/{agent_name}
```

**Response:**
```json
{
  "success": true,
  "name": "Custom Agent",
  "description": "Custom agent for specialized tasks",
  "url": "http://localhost:8001/custom_agent",
  "streaming": true,
  "type": "dynamic",
  "status": "connected",
  "added_at": "2024-01-15T10:30:00",
  "agent_card": {
    "name": "Custom Agent",
    "description": "Custom agent for specialized tasks",
    "version": "1.0.0",
    "capabilities": {
      "streaming": true,
      "custom_feature": true
    }
  }
}
```

### Reconnect Team Member
```http
POST /api/v1/team/reconnect
Content-Type: application/json

{
  "agent_name": "Custom Agent"
}
```

**Response:**
```json
{
  "success": true,
  "agent_name": "Custom Agent",
  "message": "Successfully reconnected to Custom Agent"
}
```

### Team Status Overview
```http
GET /api/v1/team/status
```

**Response:**
```json
{
  "supervisor_status": "active",
  "total_agents": 6,
  "configured_agents": 5,
  "dynamic_agents": 1,
  "connected_agents": 6,
  "disconnected_agents": 0,
  "health": "healthy"
}
```

## Batch Operations

### Batch Add Team Members
```http
POST /api/v1/team/batch/add
Content-Type: application/json

[
  {
    "agent_url": "http://localhost:8001/agent1",
    "agent_name": "Agent 1"
  },
  {
    "agent_url": "http://localhost:8002/agent2",
    "agent_name": "Agent 2"
  }
]
```

**Response:**
```json
{
  "batch_size": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "success": true,
      "agent_name": "Agent 1",
      "description": "Specialized agent 1",
      "url": "http://localhost:8001/agent1",
      "streaming": true
    },
    {
      "success": true,
      "agent_name": "Agent 2",
      "description": "Specialized agent 2",
      "url": "http://localhost:8002/agent2",
      "streaming": false
    }
  ]
}
```

### Batch Remove Team Members
```http
POST /api/v1/team/batch/remove
Content-Type: application/json

[
  {"agent_name": "Agent 1"},
  {"agent_name": "Agent 2"}
]
```

## Usage Examples

### Adding a Custom Agent

```bash
# Add a custom agent
curl -X POST http://localhost:9000/api/v1/team/add \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_url": "http://localhost:8001/custom_nlp_agent",
    "agent_name": "NLP Specialist"
  }'
```

### Checking Team Status

```bash
# Get team overview
curl http://localhost:9000/api/v1/team/status

# List all team members
curl http://localhost:9000/api/v1/team/list
```

### Removing a Dynamic Agent

```bash
# Remove a dynamically added agent
curl -X DELETE http://localhost:9000/api/v1/team/remove \\
  -H "Content-Type: application/json" \\
  -d '{"agent_name": "NLP Specialist"}'
```

## Integration with Task Delegation

Once added, dynamic team members are automatically available for task delegation. The supervisor's LLM will consider them when selecting the best agent for incoming tasks.

Example agent selection with custom agent:
```
Available agents:
- ibmcloud_base_agent: Base IBM Cloud platform engineering agent
- ibmcloud_serverless_agent: Specialized agent for IBM Cloud serverless computing
- NLP Specialist: Custom agent for natural language processing tasks

User request: "Analyze the sentiment of this customer feedback"
Selected agent: NLP Specialist
```

## Configuration

### Environment Variables

- `SUPERVISOR_HOST`: Host to bind the supervisor (default: 0.0.0.0)
- `SUPERVISOR_PORT`: Port for the supervisor API (default: 9000)
- `SUPERVISOR_AGENT_URLS`: Comma-separated list of initial agent URLs
- `SUPERVISOR_MODEL`: LLM model for agent selection (default: gpt-4o-mini)

### Agent URL Format

Agent URLs should follow the pattern: `http://host:port/agent_path`

Examples:
- `http://localhost:8000/ibmcloud_base_agent`
- `http://192.168.1.100:8001/custom_agent`
- `https://my-agent.example.com/api/agent`

## Error Handling

The API provides detailed error responses for various scenarios:

### Agent Already Exists
```json
{
  "success": false,
  "error": "Agent at http://localhost:8001/agent already connected as Existing Agent",
  "agent_name": "Existing Agent"
}
```

### Connection Failed
```json
{
  "success": false,
  "error": "Failed to connect to agent at http://localhost:8001/broken_agent"
}
```

### Cannot Remove Configured Agent
```json
{
  "success": false,
  "error": "Agent ibmcloud_base_agent is a configured agent and cannot be removed dynamically"
}
```

## Security Considerations

- Only dynamic agents can be removed; configured agents are protected
- Agent URLs are validated and normalized
- Connection failures are handled gracefully
- Name conflicts are automatically resolved with suffixes
- Batch operations are limited to 10 agents per request

## Monitoring and Observability

The team management system integrates with the supervisor's logging and monitoring:

- All team changes are logged with appropriate log levels
- Connection status is tracked and reported
- Metrics are available through the standard supervisor monitoring endpoints
- Health checks include team member connectivity status

## Integration with Event Notifications

When configured with IBM Cloud Event Notifications (see Makefile targets), the supervisor can send alerts for:

- Team member addition/removal events
- Connection failures and recoveries
- Health status changes

Configure Event Notifications using:
```bash
make ibmcloud-en-create
make ibmcloud-en-topic-create
make ibmcloud-en-destination-create
```