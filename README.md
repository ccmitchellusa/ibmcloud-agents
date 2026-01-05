# ☁️ IBM Cloud 🤖 Agents

**Lightweight** Platform Engineering AI agents for IBM Cloud that have built-in access to IBM Cloud MCP tools.

## Features

- **🛠️ MCP-compliant IBM Cloud tools**: Each agent can easily be configured with its own list of IBM Cloud tools that it will use. The integrated [chuk-mcp](https://github.com/chrishayuk/chuk-mcp) library provides multi-server, production quality MCP implementation that is blazing FAST.  
- **Add MCP servers as needed** For agents that require additional tools (MCP servers), you can include them in the Containerfile as a build layer and within the agent configure them alongside the IBM Cloud MCP Server.
- **🪶Lightweight 🕵️ A2A-compliant**: A2A Protocol support is provided via [a2a-server](https://github.com/chrishayuk/a2a-server). Each agent is exposed on A2A endpoints with agent cards that can be easily configured (YAML).
- **📦 Runs on _any_ Container runtime**: Agent containers can be deployed on any container runtime, including Podman, Rancher, Docker™️,  Kubernetes, IBM Cloud Code Engine (serverless), or RedHat™️ OpenShift.
- **🧠 BYOM** - Bring your own model (Caveat: Models MUST support OpenAI-compliant 🛠️tool calling features). The integrated [chuk-llm](https://github.com/chrishayuk/chuk-llm) library makes working with multiple model providers and models extremely SIMPLE--and FAST!
- **☁️ Production Services Integration** - Optional integration with IBM Cloud Monitoring (OTEL metrics), IBM Cloud Logs (centralized logging), and Object Storage (session management) for production deployments. Use the [terraform-ibm-agentic-services](https://github.com/ccmitchellusa/terraform-ibm-agentic-services) deployable architecture for infrastructure-as-code deployment.
- **🕵️ Base Agent** - A base agent example is provided that can be easily customized with different models, tools and instructions to create new IBM Cloud platform engineering agents.

## ❤️ Keeping it simple

The common core of the agents is found in [`src/common/ibm_cloud_base.py`](src/common/ibm_cloud_base.py), which provides the base logic for all agents. Agents are now defined primarily through **YAML configuration files** in `src/agents/`, which specify:

- 🧠 Model connection and parameters
- 🛠️ IBMCloud MCP Server tool configuration
- 🕵️ Agent description and 📃 instructions
- 🎩 Kingsmen metadata (codename, expertise)

The **Supervisor Agent** is the default agent that will appear when connecting to the server, providing intelligent task delegation.

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[📖 Getting Started](docs/README.md)** - Complete overview and quick start guide
- **[🤖 Agent Overview](docs/agents/README.md)** - Understanding all available agents  
- **[🎩 Kingsmen Curl Tutorial](docs/tutorials/KINGSMEN_CURL_TUTORIAL.md)** - Complete guide to using curl commands
- **[🛠️ Interactive Examples](docs/examples/kingsmen_curl_examples.sh)** - Hands-on demo script

### Quick Tutorial Access

The fastest way to get started:

```bash
# Start the server with all agents
export OPENAI_API_KEY="your-key"
export IBMCLOUD_API_KEY="your-ibm-key"
./run.sh

# Connect with the default Supervisor Agent
uvx a2a-cli --server http://localhost:8000 chat

# Or try the Kingsmen team with curl commands:
./docs/examples/kingsmen_curl_examples.sh
```

## 🗜️Installation & Setup

1. Install [`uv`](https://docs.astral.sh/uv/)
2. Install [IBM Cloud MCP Server](https://github.com/IBM-Cloud/mcp)
3. Clone the repository:

```bash
git clone https://github.com/ccmitchellusa/ibmcloud-agents.git
cd ibmcloud-agents
```

3. Install dependencies:

```bash
uv sync --reinstall
```

## Configure Keys

To run the example, you will need api keys for:
1. OpenAI or other LLM provider (Anthropic, Gemini, Watsonx, etc.) - The demos are preconfigured for OpenAI models (gpt-4o-mini). See [chuk-llm]([https://github.com/chrishayuk/chuk-llm](https://github.com/chrishayuk/chuk-llm?tab=readme-ov-file#provider-specific-dependencies)) for other supported model providers.  The chosen model MUST support Tool calls (OpenAI format) to work with these agents and MCP.
2. IBM Cloud - For a quick start demo, you should create a an account to use for testing purposes.  The agents will all be sharing your user API key which will need broad access to many areas.  NOTE: This is NOT recommended for production environements, in production, you will want to setup service id's and access groups to have tight control over what your agents can do within your account (least priviledge)!

Next, create a `.env` file with the above keys in the root of the ibmcloud-agents folder:

```bash
OPENAI_API_KEY=your_key_goes_here
IBMCLOUD_API_KEY=your_IBMCloud_api_key
```

## 🏃🏼Run the Agent Server (Local host)

Start the agent server locally (from the root folder of ibmcloud-agents):

```bash
./run.sh
```

Open browser on `http://localhost:8000/agent-card.json` to view card JSON. This verifies that the agents are running.

## Install an A2A Client


To connect to the agents over A2A protocol, you will need an A2A client.  The simplest A2A client which runs from the command line is  Chris Hay's [A2A CLI](https://github.com/chrishayuk/a2a-cli).  
In a separate shell, issue the following command to install and run the a2a-cli and connect it to the running agents.

```bash
# Connect to the Supervisor Agent (default)
uvx a2a-cli --server http://localhost:8000/supervisor_agent chat

# Connect to the Kingsmen
uvx a2a-cli --server http://localhost:8000/kingsmen_agent chat
```

# Understanding the Agent Architecture

## 🎯 Intelligent Agent Coordination

The system now features **two levels of coordination**:

### 1. **Supervisor Agent** (Default) 🤖
The **Supervisor Agent** serves as the default entry point and provides intelligent task delegation using LLM-powered routing. It analyzes your requests and automatically delegates to the most appropriate specialized agent.

**Available via**: `http://localhost:8000` (default) or `http://localhost:8000/supervisor_agent`

### 2. **The Kingsmen** 🎩 (Elite Team)
An alternative coordination approach featuring a themed team of IBM Cloud specialists, each with codenames and specialized expertise:

| Codename | Agent | Expertise |
|----------|-------|-----------|
| **Galahad** | Base Agent | Foundation & Infrastructure |
| **Lancelot** | Account Admin | Security & Access Control |
| **Percival** | Serverless Agent | Modern Applications & Serverless |
| **Gareth** | Guide Agent | Strategy & Best Practices |
| **Tristan** | Cloud Automation | DevOps & Automation |

**Available via**: `http://localhost:8000/kingsmen_agent`

## 🛠️ Specialized Agents

The following specialized agents handle specific IBM Cloud domains:

- **IBM Cloud Base Agent** - Core resource management and targeting
- **IBM Cloud Guide Agent** - Documentation and best practices  
- **IBM Cloud Serverless Agent** - Code Engine and serverless computing
- **IBM Cloud Account Admin Agent** - User management and IAM
- **IBM Cloud Cloud Automation Agent** - Deployable architectures and automation

### 🤖 Auto-Generated Agents

In addition to the curated agents above, this project now includes **over 50 specialized agents** generated from the IBM Cloud MCP Server configurations. These agents provide dedicated support for specific IBM Cloud services, including:

- **Compute**: VPC, PowerVS, Kubernetes, OpenShift, Code Engine
- **Network**: Direct Link, Transit Gateway, CIS (Cloud Internet Services)
- **Storage**: Cloud Object Storage, Block Storage, File Storage
- **Management**: Global Search, Tagging, Resource Groups
- **Observability**: Cloud Logs, Monitoring, Activity Tracker

These agents are enhanced with:
- **Codenames**: Unique identifiers (e.g., "Sentinel", "Admiral") for easier reference.
- **Why/When Metadata**: "When to use" descriptions that help the Supervisor agent route requests accurately.

You can find the full list of available agents in the [`src/agents/`](src/agents/) directory.

# 🚀 Getting Started

## Quick Start with Coordination Agents

### Option 1: Use the Supervisor Agent (Recommended)
The Supervisor Agent automatically routes your requests to the right specialist:

```bash
# Connect to the default supervisor agent
uvx a2a-cli --server http://localhost:8000 chat

# Try these example requests:
# "List all my resource groups"
# "Deploy a serverless application" 
# "Add a new user to my account"
# "Help me understand IBM Cloud best practices"
```

### Option 2: Work with The Kingsmen Elite Team
For a themed approach with codenames and personalities:

```bash
# Connect to the Kingsmen coordination
uvx a2a-cli --server http://localhost:8000/kingsmen_agent chat

# Try these example requests:
# "Show me the Kingsmen roster"
# "Have Lancelot add a user to my account"
# "Send Percival to deploy a serverless app"
# "Let Gareth help me understand cloud architecture"
```

## Direct Agent Access

You can also connect directly to specialized agents using the `/connect` command in a2a-cli:

### Base Agent (Foundation & Infrastructure)
```bash
/connect http://localhost:8000/ibmcloud_base_agent
```
**Capabilities**: Resource targeting, listing resource groups, account scoping, basic operations

### Guide Agent (Strategy & Best Practices) 
```bash
/connect http://localhost:8000/ibmcloud_guide_agent
```
**Capabilities**: IBM Cloud documentation, architecture guidance, best practices
**Try asking**: "Assist me with understanding CRN components" or "Help me plan an enterprise account structure"

### Serverless Agent (Modern Applications)
```bash
/connect http://localhost:8000/ibmcloud_serverless_agent
```
**Capabilities**: Code Engine projects, applications, jobs, serverless deployment
**Try asking**: "What can you help me with?" or "List my Code Engine projects"

### Account Admin Agent (Security & Access)
```bash
/connect http://localhost:8000/ibmcloud_account_admin_agent
```
**Capabilities**: User management, IAM policies, access groups, service IDs, API keys
**Try asking**: "List users in my account" or "Create a new access group"

### Cloud Automation Agent (DevOps & Automation)
```bash
/connect http://localhost:8000/ibmcloud_cloud_automation_agent  
```
**Capabilities**: Deployable architectures, projects, Schematics, Terraform
**Try asking**: "List deployable architectures" or "Create a new project"

# 🏗️ Architecture Deep Dive

## Agent Coordination Patterns

### Supervisor Agent 🤖
- **Purpose**: Intelligent task delegation using LLM-powered routing
- **Technology**: HTTP-based delegation with session management
- **Benefits**: Automatic agent selection, seamless experience, efficient routing
- **Use Case**: General users who want the system to choose the best agent automatically

### The Kingsmen 🎩
- **Purpose**: Themed team coordination with memorable codenames
- **Technology**: Same HTTP delegation with enhanced personality-driven routing  
- **Benefits**: Clear specializations, memorable interactions, themed experience
- **Use Case**: Users who prefer working with named specialists and want a more engaging interface

### Direct Agent Access 🎯
- **Purpose**: Direct access to specialized capabilities
- **Technology**: Direct MCP tool integration with IBM Cloud APIs
- **Benefits**: Full control, specialized expertise, no routing overhead
- **Use Case**: Expert users who know exactly which agent they need

## Implementation Details

Agents are dynamically loaded from YAML definitions in `src/agents/*.yaml`. Each definition instantiates an agent using the shared `IBMCloudBaseAgent` logic and includes:
- 🧠 **LLM Integration**: Configured via YAML and environment variables
- 🛠️ **MCP Tools**: Defined in YAML (pointing to MCP config files). Supports multiple MCP servers per agent.
- 🕵️ **Expert Instructions**: Detailed system prompts in the YAML file
- 📊 **Session Management**: Handled by the base agent infrastructure
- 🎩 **Kingsmen Metadata**: Codename, expertise, and specialties for the Kingsmen roster
- 🚦 **Concurrency Groups**: Sequential delegation support for agents sharing single-session resources (e.g., IBM Cloud MCP)
- 🔄 **Fallback Handling**: Graceful degradation when MCP tools are unavailable

- 🔄 **Fallback Handling**: Graceful degradation when MCP tools are unavailable

### ⚙️ Generating Agents

This repository includes scripts to automatically generate agent configurations from the source IBM Cloud MCP definitions. This ensures that agents always have the latest tool capabilities.

To regenerate or update the agents:

```bash
# Generate agent YAMLs from MCP configs
python3 scripts/generate_agents.py

# Verify the generated agents
python3 scripts/verify_agents.py
```

To add a new agent manually, simply add a new `.yaml` file to `src/agents/`.

## 📦Containerization

### ⚙️Build

#### Build arguments

You can customize the build process by passing build arguments using the `--build-arg` flag. Below are the available build arguments:

| Argument           | Description                                                                         | Default Value                                         | Stage(s) Used  |
| ------------------ | ----------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------- |
| `PYTHON_VERSION`   | Specifies the Python version to install.                                            | `3.12`                                                | Builder, Final |
| `IBMCLOUD_VERSION` | Specifies the version of the IBM Cloud CLI to install.                              | `2.35.0`                                              | Final          |
| `IBMCLOUD_ARCH`    | Specifies the architecture for the IBM Cloud CLI download (e.g., `amd64`, `arm64`). | `arm64`                                               | Final          |
| `IBMCLOUD_PLUGINS` | A comma-separated string of IBM Cloud CLI plugins to install                        | If not specified or empty, all plugins are installed. | Final          |


```bash
podman build --build-arg IBMCLOUD_PLUGINS="project" -t ibmcloud-agents:latest .
```

### ⚡️Deploy to local Podman, Rancher or Docker desktop

```bash
podman images ls
```

1. Get the image id that was pushed
2. Now run the image (on local podman)

#### Environment variables
```bash
IBMCLOUD_API_KEY=<Your IBMCloud API Key>
IBMCLOUD_REGION=us-south
IBMCLOUD_MCP_TOOLS=

LITELLM_PROXY_URL=
LITELLM_PROXY_API_KEY=
LITELLM_PROXY_MODEL=
```

```bash
podman run --rm -i -d --env-file=.env -p 8000:8000 ibmcloud-agents:latest
```

### Build and deploy to IBM Cloud container registry
In this example, agentic is your icr NAMESPACE and a2a is your REPOSITORY name.
Replace RESOURCE_GROUP with the name of the resource group where you want the container registry.

```bash
# Log docker into the IBM Cloud container registry at icr.io
ibmcloud cr login 
ibmcloud cr namespace-add -g RESOURCE_GROUP agentic
# Build the image and push it to the container registry in the 'agentic' namespace and 'a2a' repository.
docker build -f Dockerfile --push -t icr.io/agentic/a2a .

```

### 🏃Run from source code in IBM Cloud Code Engine

1. Navigate to Containers/Serverless/Projects
2. Create a project, eg. “A2A-play”
3. Navigate to “Applications”
4. Create application
 Name: ibmcloud-agents
 Code repo URL: https://github.com/ccmitchellusa/ibmcloud-agents

5. Navigate to "Optional settings"
	Image start options
		Listening port: 8000

6. Scroll back up to Code section.
7.  Select “Specify build details” > Next > Next >.
8. Select a container registry namespace
9. Select Done

## ☁️ IBM Cloud Services Integration

### Optional Supporting Services

When deploying to IBM Cloud Code Engine, you can optionally set up supporting services for production monitoring and session management:

- **📊 IBM Cloud Monitoring (Sysdig)** - OTEL metrics collection and application monitoring
- **📝 IBM Cloud Logs** - Centralized logging and log analysis  
- **🗂️ Object Storage** - Persistent session management and conversation history

### Setting up Supporting Services

1. **Create the services**:
   ```bash
   # Set up required environment variables
   cp .env.ibmcloud.example .env.ibmcloud
   # Edit .env.ibmcloud with your IBM Cloud settings
   
   # Create all supporting services
   make ibmcloud-services-setup
   ```

2. **Get service credentials**:
   ```bash
   # Display environment variables for the created services
   make ibmcloud-services-env
   ```

3. **Configure your deployment**:
   ```bash
   # Copy the output from step 2 to your .env.ibmcloud file
   # Set the *_ENABLED flags to true for services you want to use
   
   # Example:
   IBMCLOUD_MONITORING_ENABLED=true
   IBMCLOUD_LOGS_ENABLED=true  
   IBMCLOUD_COS_ENABLED=true
   ```

4. **Deploy with services**:
   ```bash
   # Deploy to IBM Cloud with monitoring and storage
   make ibmcloud-all
   ```

### Service Configuration Details

The agents automatically detect and configure these services based on environment variables:

- **Monitoring**: OTEL metrics are automatically exported to IBM Cloud Monitoring when enabled
- **Logging**: Application logs are sent to IBM Cloud Logs for centralized analysis
- **Storage**: Session data and conversation history are stored in Object Storage for persistence

For manual configuration, see the service configuration in [`agent.yaml`](agent.yaml) and [`src/common/services.py`](src/common/services.py).

### Connecting to remote agents running on IBM Cloud Code Engine

Connect [a2a-cli](https://github.com/chrishayuk/a2a-cli) to an agent running on Code Engine:

1. In the IBM Cloud console> Code Engine > Application page, click "Test Application" in upper right corner.  Copy the app's url.
2. Replace the url in the following snippet with the actual app's url from Step 1:

```bash
uvx a2a-cli --server https://ibmcloud-agents.1uo9xqkaspg3.us-east.codeengine.appdomain.cloud chat
# add --log-level DEBUG for detailed output
```

## 🤝Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## 🪪License

This project is licensed under the [MIT License](LICENSE).

- Makefile based on the work of Mihai Criveti, from [MCP Context Forge](https://github.com/IBM/mcp-context-forge/blob/main/LICENSE) under Apache v2 License.
- Agents are based on [a2a-server](https://github.com/chrishayuk/a2a-server) under MIT License.
- [IBM Cloud MCP Server](https://github.com/IBM-Cloud/ibmcloud-mcp-server) is built into the containerized version of these agents.

## 👏Acknowledgments

- Special thanks to Chris Hay for the awesome work on a2a-server, a2a-cli, mcp-cli and the chuk-* collection of libraries and for providing inspiration for this project.
