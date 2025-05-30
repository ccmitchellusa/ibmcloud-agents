# ☁️ IBM Cloud Base Agent 🤖 *(A2A compliant)* 

The base AI agent for building IBM Cloud agents that have built-in access to IBM Cloud CLI commands as MCP tools. 
The heart of this agent is found in `ibmcloud_base_agent/agent.py`, which has the 🧠llm, 🛠️ibmcloud mcp server tool configuration, and agent 📃instructions.

## Features

- **MCP-compliant IBM Cloud command support**: Select a subset of IBM Cloud commands that can be used by your agent.

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

## Containerization

### Build

```bash
podman build --load -t ibmcloud-base-agent:latest .
```

### Deploy to local Podman, Rancher or Docker desktop

```bash
podman images ls
```

1. Get the image id that was pushed
2. Now run the image (on local podman)

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

### Run from source code in IBM Cloud Code Engine

1. Navigate to Containers/Serverless/Projects
2. Create a project, eg. “A2A-play”
3. Navigate to “Applications”
4. Create application
	Name: pirate-agent-a2a
	Code repo URL: https://github.com/ccmitchellusa/pirate-agent-a2a

5. Navigate to "Optional settings"
	Image start options
		Listening port: 8000

6. Scroll back up to Code section.
7.  Select “Specify build details” > Next > Next >.
8. Select a container registry namespace
9. Select Done


## CLI Usage

Start the agent:
```bash
./run.sh
```
Open browser on http://0.0.0.0:8000/agent-card.json to view card JSON.

## A2A CLI Usage

To connect with Chris Hay's A2A CLI client (Localhost):
```bash
uvx a2a-cli --server http://localhost:8000 chat

```
Connect a2a-cli to agent running on Code Engine:
1. In the IBM Cloud console> Code Engine > Application page, click "Test Application" in upper right corner.  Copy the app's url.
2. Replace the url in the following snippet with the actual app's url from step 1:

```bash
uvx a2a-cli --server https://ibmcloud-base-agent.1uo9xqkaspg3.us-east.codeengine.appdomain.cloud chat
# add --log-level DEBUG for detailed output
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Special thanks to Chris Hay and the open-source community for providing tools and inspiration for this project.
