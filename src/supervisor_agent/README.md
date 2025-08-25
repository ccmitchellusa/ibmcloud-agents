# Supervisor Agent

A supervisory agent that can delegate tasks to multiple specialized IBM Cloud agents using the a2a protocol. Built on the a2a-server framework without Google ADK dependencies.

## Overview

The supervisor agent acts as a coordinator that:
- Receives user requests
- Uses LLM-powered routing to determine the best agent for each request
- Delegates tasks to appropriate agents via a2a protocol
- Supports streaming responses and session management
- Coordinates responses from multiple agents when needed

## Architecture

This supervisor agent is built on the **a2a-server framework** and includes:
- **Simple A2A Client**: Lightweight client library for agent communication
- **Session Management**: Built-in session support with external storage
- **Streaming Support**: Real-time response streaming
- **LLM Routing**: Intelligent agent selection using language models
- **No Google Dependencies**: Pure a2a-server implementation

## Configuration

The supervisor agent can be configured in multiple ways, with the following priority order:

1. **Direct parameter** (programmatic usage)
2. **agent.yaml configuration** (recommended)
3. **Environment variables**
4. **Default values**

### agent.yaml Configuration (Recommended)

Configure agent URLs directly in the `agent.yaml` file:

```yaml
supervisor_agent:
  type: src.supervisor_agent.supervisor_handler.SupervisorHandler
  name: supervisor_agent
  
  # Supervisor-specific configuration
  agent_urls:
    - "http://localhost:8000/ibmcloud_base_agent"
    - "http://localhost:8000/ibmcloud_account_admin_agent"
    - "http://localhost:8000/ibmcloud_serverless_agent"
    - "http://localhost:8000/ibmcloud_guide_agent"
    - "http://localhost:8000/ibmcloud_cloud_automation_agent"
  
  # Model configuration
  model: "gpt-4o-mini"
  streaming: true
  enable_sessions: true
```

### Environment Variables

- `SUPERVISOR_AGENT_URLS`: Comma-separated list of agent URLs to delegate to
  - Format: `http://<host>:<port>/<agent_name>`
  - Example: `http://localhost:8001/ibmcloud_base_agent,http://localhost:8002/ibmcloud_serverless_agent`
- `SUPERVISOR_HOST`: Host to bind the server to (default: `0.0.0.0`) - standalone mode only
- `SUPERVISOR_PORT`: Port to run the server on (default: `9000`) - standalone mode only
- `SUPERVISOR_MODEL`: LLM model to use (default: `openai/gpt-4o-mini`)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI models)
- `LITELLM_PROXY_URL`: LiteLLM proxy URL (if using proxy)
- `LITELLM_PROXY_API_KEY`: LiteLLM proxy API key

### Configuration Priority

The supervisor agent uses this priority order for agent URLs:

1. **Direct parameter**: `SupervisorHandler(agent_urls=[...])`
2. **YAML config**: `agent_urls:` in agent.yaml
3. **Environment variable**: `SUPERVISOR_AGENT_URLS`
4. **Default**: URLs for unified server setup

## Usage

The supervisor agent is now integrated into the main `agent.yaml` configuration and can be run as part of the unified a2a-server.

### Option 1: Using agent.yaml (Recommended)

The agent URLs are already configured in `agent.yaml`. Simply:

1. Set your API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Run the unified server:
```bash
python -m a2a_server.run
```

The supervisor agent will be available at `http://localhost:8000/supervisor_agent`

**To customize agent URLs**, edit the `agent_urls` section in `agent.yaml`:
```yaml
supervisor_agent:
  agent_urls:
    - "http://localhost:8000/ibmcloud_base_agent"
    - "http://localhost:8000/ibmcloud_serverless_agent"
    # Add or remove agents as needed
```

### Option 2: Standalone Mode

1. Copy the example environment file:
```bash
cp .env.supervisor.example .env.supervisor
```

2. Edit `.env.supervisor` with your configuration:
```bash
# Set the agent URLs to point to other running agents
SUPERVISOR_AGENT_URLS=http://localhost:8001/ibmcloud_base_agent,http://localhost:8002/ibmcloud_serverless_agent

# Set your API key
OPENAI_API_KEY=your-api-key-here
```

3. Run standalone:
```bash
# Load environment variables
source .env.supervisor

# Run the supervisor agent on port 9000
python -m src.supervisor_agent.main
```

### Running with Docker

```bash
docker run -p 9000:9000 \
  -e SUPERVISOR_AGENT_URLS="http://agent1:8000/base_agent,http://agent2:8000/serverless_agent" \
  -e OPENAI_API_KEY="your-api-key" \
  supervisor-agent
```

## Agent Discovery

The supervisor automatically discovers available agents at startup by:
1. Connecting to each URL specified in `SUPERVISOR_AGENT_URLS`
2. Retrieving the agent card (capabilities and description)
3. Building a registry of available agents

If an agent is unreachable during startup, the supervisor will log an error but continue with other agents.

## Example Agent Configurations

### Local Development Setup

Run each agent on a different port:

```bash
# Terminal 1: Base Agent
AGENT_PORT=8001 python -m src.ibmcloud_base_agent.main

# Terminal 2: Serverless Agent  
AGENT_PORT=8002 python -m src.ibmcloud_serverless_agent.main

# Terminal 3: Account Admin Agent
AGENT_PORT=8003 python -m src.ibmcloud_account_admin_agent.main

# Terminal 4: Supervisor Agent
SUPERVISOR_AGENT_URLS="http://localhost:8001/ibmcloud_base_agent,http://localhost:8002/ibmcloud_serverless_agent,http://localhost:8003/ibmcloud_account_admin_agent" \
SUPERVISOR_PORT=9000 \
python -m src.supervisor_agent.main
```

### Production Setup

```bash
# Use environment-specific agent URLs
export SUPERVISOR_AGENT_URLS="https://base-agent.prod.example.com/ibmcloud_base_agent,https://serverless-agent.prod.example.com/ibmcloud_serverless_agent"
export SUPERVISOR_PORT=8080
export SUPERVISOR_MODEL="gpt-4"

python -m src.supervisor_agent.main
```

## Troubleshooting

### No agents connected

Check that:
1. The agent URLs in `SUPERVISOR_AGENT_URLS` are correct
2. The target agents are running and accessible
3. Network connectivity allows the supervisor to reach the agents

### Agent delegation fails

Verify:
1. The target agent supports the requested task
2. The agent's a2a endpoint is functioning
3. Check supervisor logs for detailed error messages

## Architecture

```
User Request
     ↓
Supervisor Agent (a2a-server framework)
     ↓
[LLM-powered agent routing]
     ↓
Simple A2A Client → Remote Agent
     ↓
Streaming Response
     ↓
Session Management & Response Coordination
   ↙    ↓    ↘
Base   Serverless  Account
Agent   Agent     Admin Agent
```

### Key Components

1. **SupervisorHandler**: Main handler extending SessionAwareTaskHandler
2. **SimpleA2AClient**: Lightweight A2A communication client  
3. **RemoteAgentConnection**: Manages connections to remote agents
4. **LLM Router**: Uses language models to select optimal agents

The supervisor maintains async connections to remote agents and provides intelligent task delegation with full session support.