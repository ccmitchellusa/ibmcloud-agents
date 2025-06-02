"""
IBM Cloud Platform Engineering base agent with IBMCloud MCP Server built in.
"""
import json
import os
from pathlib import Path
from a2a_server.tasks.handlers.chuk.chuk_agent import create_agent_with_mcp
from chuk_llm.llm.configuration.provider_config import ProviderConfig


AGENT_MODEL = os.getenv("LITELLM_PROXY_MODEL")

runtime_overlay = {
    "litellm": {
        "client": "chuk_llm.llm.providers.openai_client:OpenAILLMClient",
        "api_key_env": "LITELLM_PROXY_API_KEY",
        "default_model": AGENT_MODEL,
        "api_base": os.getenv("LITELLM_PROXY_URL"),
    }
}
provider_config = ProviderConfig(runtime_overlay=runtime_overlay)

IBMCLOUD_MCP_TOOLS = os.getenv("IBMCLOUD_MCP_TOOLS", "")

# Create the configuration for the MCP server
config_file = "ibmcloud_mcp_config.json"
config = {
    "mcpServers": {
        "ibmcloud": {
            "command": "/usr/local/bin/ibmcloud",
            "args": [        
                "--mcp-transport",
                "stdio",
                "--mcp-tools",
                IBMCLOUD_MCP_TOOLS
            ]
        }
    }
}

# Create a temporary file and write the config to it
config_path = Path(config_file)
config_path.write_text(json.dumps(config, indent=2))

# IBM Cloud base agent with native MCP integration
root_agent = create_agent_with_mcp(
    name="ibmcloud_base_agent",
    description="An IBM Cloud platform engineering base agent that can do basic IBM Cloud resource management.",
    instruction="""
You are an IBM Cloud platform engineer called Chris, you will act as a platform engineer with deep expertise
in IBM Cloud service operations and patterns for cloud architecture. You have access to the native tool engine with a set of tools that can be used 
to access and work with cloud resources in IBM Cloud accounts. For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT 
understand other cloud providers.

When a tool's output is not json format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

In IBM Cloud, 'target' is a term used to describe how a user selects the accounts, resource groups, regions and api endpoints which act the scope or
context that will be used in subsequent tool calls. Use the target tool to get the currently targeted account, region, api endpoint and resource group. 
If a current resource group has not been targetted, target the 'default' resource group, then display the targets to the user.",
""",
    mcp_servers=["ibmcloud"],
    mcp_config_file=str(config_file),
    tool_namespace="tools",
    model=AGENT_MODEL,
    config=provider_config,
    provider="litellm",
    streaming=True
)

