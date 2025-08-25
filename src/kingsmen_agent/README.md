# The Kingsmen 🎩

An elite team of IBM Cloud specialists, each with codenames and specialized expertise areas. The Kingsmen agent demonstrates how to create a pre-configured supervisor agent with a themed team structure.

## Overview

The Kingsmen are an elite team of IBM Cloud agents, each with their own codename and area of specialization:

| Codename | Real Identity | Expertise | Specialties |
|----------|---------------|-----------|-------------|
| **Galahad** | `ibmcloud_base_agent` | Foundation & Infrastructure | Resource groups, service instances, targets, basic operations |
| **Lancelot** | `ibmcloud_account_admin_agent` | Security & Access Control | User management, IAM policies, access groups, service IDs, API keys |
| **Percival** | `ibmcloud_serverless_agent` | Serverless & Modern Apps | Code Engine, functions, serverless apps, container deployments |
| **Gareth** | `ibmcloud_guide_agent` | Strategy & Best Practices | Architecture guidance, best practices, troubleshooting |
| **Tristan** | `ibmcloud_cloud_automation_agent` | Automation & DevOps | Deployable architectures, projects, Schematics, Terraform |

## Architecture

```
Arthur (Kingsmen Leader/Coordinator)
           ↓
    [Mission Analysis & Agent Selection]
           ↓
     Elite Team Deployment
    ↙    ↓    ↓    ↓    ↘
 Galahad Lancelot Percival Gareth Tristan
 (Base)  (Security) (Serverless) (Guide) (Automation)
```

## Features

- **🎩 Themed Organization**: Each agent has a memorable codename and clear specialization
- **🎯 Enhanced Selection**: Intelligent routing based on expertise areas and specialties
- **🔄 Pre-configured Team**: No need to manually configure agent URLs
- **🌍 Environment Flexibility**: Support for development, staging, and production deployments
- **📊 Team Management**: Built-in roster management and status tracking

## Usage

### Option 1: Via agent.yaml (Recommended)

The Kingsmen are pre-configured in `agent.yaml`:

```bash
export OPENAI_API_KEY="your-api-key"
python -m a2a_server.run
```

Access at: `http://localhost:8000/kingsmen_agent`

### Option 2: Standalone Mode

```bash
export OPENAI_API_KEY="your-api-key"
python -m src.kingsmen_agent.main
```

Access at: `http://localhost:9001/kingsmen_agent`

### Option 3: Programmatic Usage

```python
from src.kingsmen_agent.kingsmen_handler import KingsmenHandler

# Development team
handler = KingsmenHandler.create_development_team()

# Production team
handler = KingsmenHandler.create_production_team(
    base_url="https://agents.prod.example.com"
)

# Custom team
handler = KingsmenHandler(
    team_environment="staging",
    custom_roster=[...],  # Custom agent list
    model="gpt-4"
)
```

## Configuration

### Environment Variables

- `KINGSMEN_MODEL`: LLM model for coordination (default: `gpt-4o-mini`)
- `KINGSMEN_HOST`: Server host for standalone mode (default: `0.0.0.0`)
- `KINGSMEN_PORT`: Server port for standalone mode (default: `9001`)
- `OPENAI_API_KEY`: OpenAI API key

### YAML Configuration

```yaml
kingsmen_agent:
  type: src.kingsmen_agent.kingsmen_handler.KingsmenHandler
  name: kingsmen_agent
  
  # Kingsmen-specific configuration
  team_environment: "localhost"  # or "development", "production"
  
  # Standard handler configuration
  model: "gpt-4o-mini"
  streaming: true
  enable_sessions: true
```

## Team Interaction Examples

### General Requests (Arthur Decides)

```
User: "I need to set up a new IBM Cloud environment"
Arthur: "Analyzing request... Deploying Galahad for infrastructure setup"
→ Routes to ibmcloud_base_agent
```

```
User: "Create a serverless application with monitoring"
Arthur: "This requires modern applications expertise... Sending Percival"
→ Routes to ibmcloud_serverless_agent
```

### Direct Agent Requests

```
User: "Have Lancelot add a new user to my account"
Arthur: "Deploying Lancelot for security operations"
→ Routes to ibmcloud_account_admin_agent
```

```
User: "Tristan, set up a deployment pipeline"
Arthur: "Deploying Tristan for automation tasks"  
→ Routes to ibmcloud_cloud_automation_agent
```

## API Methods

### Team Management

```python
# Get team roster
roster = handler.get_team_roster()
for agent in roster:
    print(f"{agent['codename']}: {agent['status']}")

# Find agent by codename
galahad = handler.get_agent_by_codename("Galahad")
print(f"Galahad handles: {galahad.expertise}")
```

### Factory Methods

```python
# Development team (localhost URLs)
dev_team = KingsmenHandler.create_development_team()

# Production team (custom base URL)
prod_team = KingsmenHandler.create_production_team(
    base_url="https://agents.production.example.com"
)
```

## Extending the Kingsmen

### Adding New Agents

```python
from src.kingsmen_agent.kingsmen_handler import KingsmanAgent, KingsmenHandler

# Create custom agent
new_agent = KingsmanAgent(
    codename="Merlin",
    real_name="ibmcloud_ai_agent",
    url="http://localhost:8000/ibmcloud_ai_agent", 
    expertise="AI & Machine Learning",
    description="The AI specialist who handles Watson services and ML pipelines",
    specialties=["watson_services", "machine_learning", "ai_pipelines"]
)

# Add to custom roster
custom_roster = KingsmenHandler.KINGSMEN_ROSTER + [new_agent]

# Create handler with extended team
handler = KingsmenHandler(custom_roster=custom_roster)
```

### Custom Deployment Environments

```python
class KingsmenHandler(SupervisorHandler):
    @classmethod
    def create_kubernetes_team(cls, namespace: str = "default", **kwargs):
        """Create Kingsmen team deployed in Kubernetes"""
        k8s_roster = []
        for agent in cls.KINGSMEN_ROSTER:
            k8s_agent = KingsmanAgent(
                codename=agent.codename,
                real_name=agent.real_name,
                url=f"http://{agent.real_name}.{namespace}.svc.cluster.local:8000/{agent.real_name}",
                expertise=agent.expertise,
                description=agent.description,
                specialties=agent.specialties
            )
            k8s_roster.append(k8s_agent)
        
        return cls(
            name="kingsmen_k8s_team",
            team_environment="kubernetes",
            custom_roster=k8s_roster,
            **kwargs
        )
```

## Benefits

1. **🎯 Clear Specialization**: Each agent has a defined role and expertise area
2. **🧠 Enhanced Intelligence**: Themed selection logic with agent personalities
3. **⚡ Quick Setup**: Pre-configured team with no manual URL configuration
4. **🔧 Flexible Deployment**: Support for different environments and custom rosters
5. **📊 Team Visibility**: Built-in roster management and status tracking
6. **🎭 Memorable Interface**: Codenames make it easy to remember and request specific agents

## Troubleshooting

### Team Assembly Issues

```bash
# Check team status
curl http://localhost:8000/kingsmen_agent/status

# View logs for connection issues
tail -f /path/to/logs | grep "Kingsmen"
```

### Agent Unavailable

If a Kingsman is unavailable:
1. Arthur will log the selection and attempt
2. Falls back to available team members
3. Provides clear error messages about team status

### Custom Roster Issues

Ensure custom agents follow the `KingsmanAgent` structure:
- Valid URLs accessible from the supervisor
- Proper codenames and expertise definitions  
- Specialties list for enhanced routing

---

*"Manners maketh man, but expertise maketh the perfect IBM Cloud operation."* - Arthur, Kingsmen Leader