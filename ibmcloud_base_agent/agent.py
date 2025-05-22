"""
IBM Cloud Platform Engineering base agent with IBMCloud MCP Server built in.
"""
import json
from pathlib import Path
from a2a_server.tasks.handlers.chuk.chuk_agent import create_agent_with_mcp

#TODO: Load the model from os.environ
AGENT_MODEL = "gpt-4o-mini"

# Create the configuration for the weather MCP server
config_file = ".mcp/ibmcloud/resource_management.json"
config = {
    "mcpServers": {
        "ibmcloud": {
            "command": "/Users/chrism1/Code/cli/bluemix-cli/out/ibmcloud-darwin-arm64",
            "args": [        
                "--mcp-transport",
                "stdio",
                "--mcp-tools",
                "resource_groups,catalog_list,resource_search,resource_reclamations,resource_reclamation-show,resource_service-instances,resource_service-instance-create,resource_tag-attach,resource_tag-create,resource_tag-delete,resource_tags,resource_subscriptions,resource_subscription,resource_service_instance"
            ]
        }
    }
}

# Ensure config file exists
config_path = Path(config_file)
if not config_path.exists():
    print("Config file does not exist, creating default config.")
    config_path.write_text(json.dumps(config, indent=2))

# IBM CLoud base agent with native MCP integration
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
    mcp_config_file=config_file,
    tool_namespace="tools",
    provider="openai",
    model=AGENT_MODEL,
    streaming=True
)

