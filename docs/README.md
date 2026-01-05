# IBM Cloud Agents Documentation 📚

Welcome to the documentation for the IBM Cloud Agents project. This collection provides specialized agents for IBM Cloud operations, built on the a2a-server framework.

## 🎯 Quick Start

1. **Set up your environment:**
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

2. **Start the unified server:**
   ```bash
   python -m a2a_server.run
   ```

3. **Access agents at:**
   - Supervisor Agent: `http://localhost:8000/supervisor_agent`
   - Kingsmen Team: `http://localhost:8000/kingsmen_agent`
   - Individual agents: `http://localhost:8000/{agent_name}`

## 📋 Available Agents

### Core Agents
- **🏗️ Base Agent** (`ibmcloud_base_agent`) - Foundation & infrastructure management
- **🔐 Account Admin Agent** (`ibmcloud_account_admin_agent`) - Security & access control
- **🚀 Serverless Agent** (`ibmcloud_serverless_agent`) - Serverless & modern applications  
- **🧭 Guide Agent** (`ibmcloud_guide_agent`) - Strategy & best practices
- **⚙️ Cloud Automation Agent** (`ibmcloud_cloud_automation_agent`) - DevOps & automation

### Supervisor Agents
- **🤖 Supervisor Agent** (`supervisor_agent`) - Intelligent task delegation
- **🎩 Kingsmen Agent** (`kingsmen_agent`) - Elite themed team coordination

### Auto-Generated Agents
- **⚡️ Service Specific Agents** - Over 50+ specialized agents for individual IBM Cloud services (e.g., `ibmcloud_vpc_vpc_agent`, `ibmcloud_cos_object_storage_agent`).
- Each comes with specific "When to use" routing metadata and unique codenames.

## 📖 Tutorials

### Getting Started
- [Agent Overview](agents/README.md) - Understanding the agent ecosystem
- [Configuration Guide](configuration/README.md) - Setting up agents and environments

### Working with Agents
- **[Kingsmen Curl Tutorial](tutorials/KINGSMEN_CURL_TUTORIAL.md)** 🎩
  - Complete guide to using curl commands with the Kingsmen team
  - Session management, streaming, and advanced workflows
  - Real-world examples for each team member

### Production Deployment
- **[IBM Cloud Services Integration](IBM_CLOUD_SERVICES.md)** ☁️📊
  - Optional monitoring, logging, and storage services
  - Complete setup guide for production deployments
  - Cost optimization and troubleshooting

### API Documentation
- [A2A Protocol](api/a2a-protocol.md) - Understanding the agent-to-agent protocol
- [REST API Reference](api/rest-api.md) - HTTP endpoints and request formats

## 🛠️ Examples

### Interactive Scripts
- **[Kingsmen Examples](examples/kingsmen_curl_examples.sh)** - Interactive demo script
  ```bash
  ./docs/examples/kingsmen_curl_examples.sh
  ```

### Code Examples
- [Python Client Examples](examples/python/) - Using agents programmatically
- [Shell Script Examples](examples/shell/) - Automation and batch operations

## 🏗️ Architecture

### Agent Types

**Individual Agents:**
```
User Request → Individual Agent → IBM Cloud Services
```

**Supervisor Agent:**
```
User Request → Supervisor → [Selects Best Agent] → Specialized Agent → IBM Cloud Services
```

**Kingsmen Team:**
```
User Request → Arthur (Coordinator) → [Elite Team Selection] → Specialist Agent → IBM Cloud Services
```

### Team Structure

The Kingsmen demonstrate a themed approach to agent organization:

| Codename | Agent | Expertise |
|----------|-------|-----------|
| **Arthur** | Supervisor | Team coordination & mission planning |
| **Galahad** | Base Agent | Foundation & infrastructure |
| **Lancelot** | Account Admin | Security & access control |
| **Percival** | Serverless | Modern applications & serverless |
| **Gareth** | Guide | Strategy & best practices |
| **Tristan** | Automation | DevOps & infrastructure as code |

## 🔧 Configuration

### Environment Variables
```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional - Supervisor Configuration  
export SUPERVISOR_AGENT_URLS="http://localhost:8000/agent1,http://localhost:8000/agent2"
export SUPERVISOR_MODEL="gpt-4o-mini"

# Optional - Kingsmen Configuration
export KINGSMEN_MODEL="gpt-4o-mini"
```

### YAML Configuration
Agents are configured in `agent.yaml`:

```yaml
handlers:
  supervisor_agent:
    type: src.supervisor_agent.supervisor_handler.SupervisorHandler
    agent_urls:
      - "http://localhost:8000/ibmcloud_base_agent"
      - "http://localhost:8000/ibmcloud_serverless_agent"
      
  kingsmen_agent:
    type: src.kingsmen_agent.kingsmen_handler.KingsmenHandler
    team_environment: "localhost"
```

## 🧪 Development

### Running Tests
```bash
# Test individual components
python -m pytest tests/

# Test agent interactions
./docs/examples/kingsmen_curl_examples.sh
```

### Creating Custom Agents

1. **Extend Base Classes:**
   ```python
   from src.supervisor_agent.supervisor_handler import SupervisorHandler
   
   class MyCustomTeam(SupervisorHandler):
       # Your custom logic here
   ```

2. **Configure in agent.yaml:**
   ```yaml
   my_custom_team:
     type: src.my_custom_team.handler.MyCustomTeam
   ```

3. **Add to Documentation:**
   - Update this README
   - Add tutorial if needed
   - Include examples

## 📚 Additional Resources

### IBM Cloud
- [IBM Cloud Documentation](https://cloud.ibm.com/docs)
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli)
- [IBM Cloud Resource Management](https://cloud.ibm.com/docs/account)

### A2A Framework
- [A2A Server Documentation](https://github.com/a2a-server/docs)
- [Agent Development Guide](https://github.com/a2a-server/agent-dev-guide)

### OpenAI
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Model Selection Guide](https://platform.openai.com/docs/models)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Add your agent or improvements**
4. **Update documentation**
5. **Submit a pull request**

### Documentation Guidelines
- Add tutorials for new features
- Include practical examples
- Update the main README
- Test all code examples

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :8000

# Verify environment
echo $OPENAI_API_KEY
```

**Agent not responding:**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Check agent card
curl http://localhost:8000/{agent_name}/.well-known/agent.json
```

**Configuration issues:**
```bash
# Validate YAML
python -c "import yaml; print(yaml.safe_load(open('agent.yaml')))"

# Check logs
tail -f logs/agent.log
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Need help?** Check the tutorials, run the examples, or open an issue on GitHub! 🎩