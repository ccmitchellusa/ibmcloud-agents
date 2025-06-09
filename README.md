# ☁️ IBM Cloud Base Agent 🤖 *(A2A compliant)* 

**Lightweight** base AI agent for building IBM Cloud agents that have built-in access to IBM Cloud MCP tools.
**Platform Engineering Agent examples** Example agents for Serverless computing Redhat Openshift & Kubernetes on IBM Cloud

## Features

- **🛠️MCP-compliant IBM Cloud tools**: Select a subset of IBM Cloud tools that can be used by your agent.
- **🪶Lightweight 🕵️A2A-compliant** protocol support via [a2a-server](https://github.com/chrishayuk/a2a-server)
- **📦Runs on _any_ Container runtime**
- **🧠BYOM** - Bring your own model (must support 🛠️tool calling)

## ❤️Simple

The heart of this agent is found in `ibmcloud_base_agent/agent.py`, which has:

- 🧠LLM connection - LiteLLM
- 🛠️IBMCloud MCP Server tool configuration for basic IBM Cloud commands to set target context and listing resource groups.
- 🕵️Agent 📃instructions .

This agent is the default agent that will appear when connecting to the server with a2a-cli (or other a2a client app).

To switch to the Serverless computing agent in a2a-cli, type `/connect http://<host>:8000/ibmcloud_serverless_agent`
To switch back to the Base agent, type `/connect http://<host>:8000/ibmcloud_base_agent`

## 🕵🏼‍♂️ Serverless Computing Agent Example

An example specialized agent for Serverless computing using Code Engine is found in `ibmcloud_serverless_agent/agent.py`, which has:

- 🧠LLM connection - LiteLLM
- 🛠️IBMCloud MCP Server tool configuration for Code Engine-related tasks
- 🕵️Agent 📃instructions for Serverless computing on IBM Cloud.

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/ccmitchellusa/ibmcloud-base-agent.git
cd ibmcloud-base-agent
```

2. Install dependencies:

```bash
uv sync --reinstall
```

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
podman build --build-arg IBMCLOUD_PLUGINS="project" -t ibmcloud-base-agent:latest .
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
podman run --rm -i -d --env-file=.env -p 8000:8000 ibmcloud-base-agent:latest
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
	Name: ibmcloud-agent
	Code repo URL: https://github.com/ccmitchellusa/ibmcloud-base-agent

5. Navigate to "Optional settings"
	Image start options
		Listening port: 8000

6. Scroll back up to Code section.
7.  Select “Specify build details” > Next > Next >.
8. Select a container registry namespace
9. Select Done


## 🖥️CLI Usage

Start the agent:
```bash
./run.sh
```
Open browser on http://0.0.0.0:8000/agent-card.json to view card JSON.

## A2A CLI Usage

To connect with Chris Hay's [A2A CLI](https://github.com/chrishayuk/a2a-cli) client (Localhost):
```bash
uvx a2a-cli --server http://localhost:8000 chat

```
Connect [a2a-cli](https://github.com/chrishayuk/a2a-cli) to agent running on Code Engine:
1. In the IBM Cloud console> Code Engine > Application page, click "Test Application" in upper right corner.  Copy the app's url.
2. Replace the url in the following snippet with the actual app's url from step 1:

```bash
uvx a2a-cli --server https://ibmcloud-base-agent.1uo9xqkaspg3.us-east.codeengine.appdomain.cloud chat
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
- Agent is based on [a2a-server](https://github.com/chrishayuk/a2a-server) under MIT License.
- [IBM Cloud MCP Server](https://github.com/IBM-Cloud/ibmcloud-mcp-server) is built into the containerized version of this agent.

## 👏Acknowledgments

- Special thanks to Chris Hay for the awesome work on a2a-server, a2a-cli, mcp-cli and the chuk-* collection of libraries and for providing inspiration for this project.
