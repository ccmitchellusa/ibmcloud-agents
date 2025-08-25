# IBM Cloud Agents Overview 🤖

This document provides an overview of all available IBM Cloud agents, their capabilities, and when to use each one.

## Agent Categories

### 🏗️ Individual Specialists
Focused agents that handle specific aspects of IBM Cloud operations.

### 🤖 Supervisors
Coordination agents that delegate tasks to appropriate specialists.

### 🎩 Themed Teams
Pre-configured teams with memorable identities and clear specializations.

## Individual Specialist Agents

### 🏗️ IBM Cloud Base Agent
**Purpose:** Foundation and infrastructure management
**Best for:** Basic operations, resource groups, service instances

```bash
# Access directly
curl http://localhost:8000/ibmcloud_base_agent/task -d '{...}'

# Via Kingsmen
curl http://localhost:8000/kingsmen_agent/task -d '{"message": {"parts": [{"text": "Galahad, list my resource groups"}]}}'
```

**Key capabilities:**
- Resource group management
- Service instance listing
- Target configuration
- Basic IBM Cloud operations

---

### 🔐 IBM Cloud Account Admin Agent
**Purpose:** Security and access control
**Best for:** User management, IAM, access policies

```bash
# Access directly  
curl http://localhost:8000/ibmcloud_account_admin_agent/task -d '{...}'

# Via Kingsmen
curl http://localhost:8000/kingsmen_agent/task -d '{"message": {"parts": [{"text": "Lancelot, create a service ID"}]}}'
```

**Key capabilities:**
- User invitation and management
- Access group creation
- Service ID management
- API key generation
- IAM policy management

---

### 🚀 IBM Cloud Serverless Agent
**Purpose:** Serverless and modern applications
**Best for:** Code Engine, functions, container deployments

```bash
# Access directly
curl http://localhost:8000/ibmcloud_serverless_agent/task -d '{...}'

# Via Kingsmen  
curl http://localhost:8000/kingsmen_agent/task -d '{"message": {"parts": [{"text": "Percival, deploy a serverless app"}]}}'
```

**Key capabilities:**
- Code Engine project management
- Application deployment
- Function creation
- Serverless scaling configuration
- Container management

---

### 🧭 IBM Cloud Guide Agent  
**Purpose:** Strategy and best practices
**Best for:** Architecture guidance, recommendations, troubleshooting

```bash
# Access directly
curl http://localhost:8000/ibmcloud_guide_agent/task -d '{...}'

# Via Kingsmen
curl http://localhost:8000/kingsmen_agent/task -d '{"message": {"parts": [{"text": "Gareth, what are the best practices for..."}]}}'
```

**Key capabilities:**
- Best practice recommendations
- Architecture guidance
- Service recommendations
- Troubleshooting assistance
- IBM Cloud expertise

---

### ⚙️ IBM Cloud Automation Agent
**Purpose:** DevOps and infrastructure as code
**Best for:** Deployable architectures, projects, Terraform

```bash
# Access directly
curl http://localhost:8000/ibmcloud_cloud_automation_agent/task -d '{...}'

# Via Kingsmen
curl http://localhost:8000/kingsmen_agent/task -d '{"message": {"parts": [{"text": "Tristan, set up a CI/CD pipeline"}]}}'
```

**Key capabilities:**
- Deployable architecture management
- Project creation and management
- Schematics workspace management
- Terraform automation
- CI/CD pipeline setup

## Supervisor Agents

### 🤖 Supervisor Agent
**Purpose:** General intelligent task delegation
**Best for:** When you want automatic agent selection without themes

```bash
curl http://localhost:8000/supervisor_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-001",
    "message": {
      "role": "user", 
      "parts": [{"text": "I need help with IBM Cloud security setup"}]
    }
  }'
```

**How it works:**
1. Analyzes your request
2. Selects the most appropriate specialist agent
3. Delegates the task
4. Returns coordinated response

**Configuration:**
```yaml
supervisor_agent:
  agent_urls:
    - "http://localhost:8000/ibmcloud_base_agent"
    - "http://localhost:8000/ibmcloud_account_admin_agent"
    # ... more agents
```

---

### 🎩 Kingsmen Agent
**Purpose:** Themed elite team coordination
**Best for:** When you want memorable agent identities and specialized routing

```bash
curl http://localhost:8000/kingsmen_agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "mission-001",
    "message": {
      "role": "user",
      "parts": [{"text": "Have Lancelot audit my account security"}]
    }
  }'
```

**Team Roster:**
- **Arthur** (Coordinator) - Mission planning and agent selection
- **Galahad** (Base Agent) - Foundation and infrastructure
- **Lancelot** (Account Admin) - Security and access control  
- **Percival** (Serverless) - Modern applications
- **Gareth** (Guide) - Strategy and best practices
- **Tristan** (Automation) - DevOps and automation

**Enhanced Features:**
- Codename-based agent requests
- Themed selection logic
- Team status tracking
- Environment-specific deployments

## Decision Matrix

| Scenario | Recommended Agent | Why |
|----------|-------------------|-----|
| "List my resource groups" | Base Agent or Galahad | Basic infrastructure operation |
| "Add user with specific permissions" | Account Admin or Lancelot | Security/access management |
| "Deploy a serverless API" | Serverless Agent or Percival | Modern application deployment |
| "What's the best way to structure my account?" | Guide Agent or Gareth | Strategic guidance needed |
| "Set up automated deployment" | Automation Agent or Tristan | DevOps and automation |
| "I'm not sure which agent I need" | Supervisor Agent | Automatic selection |
| "This is a complex multi-step project" | Kingsmen Agent | Coordinated team approach |

## Usage Patterns

### Direct Agent Access
**When to use:** You know exactly which agent you need
```bash
curl http://localhost:8000/ibmcloud_serverless_agent/task -d '{...}'
```

### Supervisor Delegation  
**When to use:** You want automatic agent selection
```bash
curl http://localhost:8000/supervisor_agent/task -d '{...}'
```

### Kingsmen Coordination
**When to use:** You want themed interaction or complex coordination
```bash  
curl http://localhost:8000/kingsmen_agent/task -d '{...}'
```

### Named Agent Requests
**When to use:** You want to request specific agents by memorable names
```bash
curl http://localhost:8000/kingsmen_agent/task \
  -d '{"message": {"parts": [{"text": "Have Lancelot handle this security issue"}]}}'
```

## Agent Selection Guidelines

### 🎯 **Choose Individual Agents When:**
- You have a specific, focused task
- You know exactly what type of operation you need
- You want the most direct path to results
- You're building automated scripts

### 🤖 **Choose Supervisor Agent When:**
- You're unsure which agent is best
- You want automatic intelligent routing
- You prefer a simple, unified interface
- You're prototyping or exploring capabilities

### 🎩 **Choose Kingsmen When:**
- You want an engaging, themed experience
- You're working on complex, multi-faceted projects  
- You prefer memorable agent identities
- You want enhanced coordination features
- You're demonstrating or teaching the system

## Configuration Examples

### Minimal Setup
```yaml
handlers:
  default: ibmcloud_base_agent
  
  ibmcloud_base_agent:
    type: a2a_server.tasks.handlers.chuk.chuk_agent_handler.AgentHandler
    agent: ibmcloud_base_agent.agent.root_agent
```

### Supervisor Setup
```yaml
handlers:
  default: supervisor_agent
  
  supervisor_agent:
    type: src.supervisor_agent.supervisor_handler.SupervisorHandler
    agent_urls:
      - "http://localhost:8000/ibmcloud_base_agent"
      - "http://localhost:8000/ibmcloud_serverless_agent"
```

### Full Kingsmen Team
```yaml
handlers:
  default: kingsmen_agent
  
  kingsmen_agent:
    type: src.kingsmen_agent.kingsmen_handler.KingsmenHandler
    team_environment: "localhost"
    # Agent URLs are pre-configured in the Kingsmen class
```

## Next Steps

1. **Try the basics:** Start with individual agents for simple tasks
2. **Explore coordination:** Use the supervisor for automatic routing
3. **Experience the team:** Try the Kingsmen for complex workflows
4. **Build custom:** Create your own themed teams or specialists

For hands-on examples, see the [Kingsmen Curl Tutorial](../tutorials/KINGSMEN_CURL_TUTORIAL.md).