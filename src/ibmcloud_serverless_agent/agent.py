"""
IBM Cloud Platform Engineering base agent with IBMCloud MCP Server built in.
"""
import json
import logging
import os
from pathlib import Path
from a2a_server.tasks.handlers.chuk.chuk_agent import ChukAgent
from chuk_llm.configuration import ProviderConfig

logger = logging.getLogger(__name__)

AGENT_PROVIDER = os.getenv("PROVIDER","openai")
AGENT_MODEL = os.getenv("MODEL","gpt-4o-mini")

runtime_overlay = {
    "litellm": {
        "client": "chuk_llm.llm.providers.openai_client:OpenAILLMClient",
        "api_key_env": "LITELLM_PROXY_API_KEY",
        "default_model": AGENT_MODEL,
        "api_base": os.getenv("LITELLM_PROXY_URL"),
    }
}
provider_config = ProviderConfig(runtime_overlay)

#IBMCLOUD_MCP_TOOLS = os.getenv("IBMCLOUD_MCP_TOOLS")
IBMCLOUD_MCP_TOOLS = "target,resource_groups,code-engine_application_list,code-engine_project_select,code-engine_project_list,code-engine_project_get,code-engine_project_current,code-engine_application_get,code-engine_application_logs,code-engine_application_restart,code-engine_application_create,code-engine_build_list,code-engine-build_get,code-engine_application_events,code-engine_buildrun_logs,code-engine_buildrun_list,code-engine_buildrun_get"

# Create the configuration for the MCP server
config_file = "ibmcloud_mcp_serverless_agent_config.json"
config = {
    "mcpServers": {
        "ibmcloud-serverless": {
            "command": "ibmcloud",
            "args": [        
                "--mcp-transport",
                "stdio",
                "--mcp-allow-write",
                "--mcp-tools",
                IBMCLOUD_MCP_TOOLS
            ]
        }
    }
}

# Write config to a file
config_path = Path(config_file)
config_path.write_text(json.dumps(config, indent=2))

try:
    # IBM Cloud serverless computing agent
    root_agent = ChukAgent(
        name="ibmcloud_serverless_agent",
        description="An IBM Cloud agent that performs serverless computing tasks.",
        instruction="""
You are an IBM Cloud platform engineer called Simon, you will act as an expert with deep expertise
in IBM Cloud serverless computing capabilities and the Code Engine service. You have access to the native tool engine with a set of tools that can be used 
to access and work with code engine resources in IBM Cloud accounts. For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT 
understand other cloud providers.

When a tool's output is not JSON format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

In IBM Cloud, 'target' is a term used to describe how a user selects the accounts, resource groups, regions and api endpoints which act the scope or
context that will be used in subsequent tool calls. Use the target tool to get the currently targeted account, region, api endpoint and resource group. 
If a current resource group has not been targetted, target the 'default' resource group, then display the targets to the user.",
IMPORTANT: Always use your tools to get real data. Never give generic responses!
""",
        mcp_servers=["ibmcloud-serverless"],
        mcp_config_file=str(config_file),
        tool_namespace="tools",
        provider=AGENT_PROVIDER,
        model=AGENT_MODEL,
#        config=provider_config,
        streaming=True
    )
    logger.info("IBM Cloud Serverless Computing agent created successfully with MCP tools")
    
except Exception as e:
    logger.error(f"Failed to create IBM Cloud Serverless Computing agent with MCP: {e}")
    logger.error("Make sure to install: ibmcloud-mcp-server")
    
    # Fallback agent with clear error message
    root_agent = ChukAgent(
        name="ibmcloud_serverless_agent",
        description="An IBM Cloud agent that performs serverless computing tasks.",
        instruction="""I'm the IBM Cloud Serverless Computing agent, but my IBM Cloud connection is currently unavailable.

In the meantime, I recommend checking:
- cloud.ibm.com for IBM Cloud status

I apologize for the inconvenience!""",

        provider=AGENT_PROVIDER,
        model=AGENT_MODEL,
        mcp_transport="stdio",
        mcp_servers=[],  # No MCP servers for fallback
        namespace="stdio"
    )
    logger.warning("Created fallback IBM Cloud Serverless Computing agent - MCP tools unavailable")
