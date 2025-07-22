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

# Extract session-related parameters with defaults
enable_sessions =True
enable_tools = True
debug_tools = False
infinite_context = True
token_threshold = 4000
max_turns_per_segment = 50
session_ttl_hours = 24 # hours

# Extract other configurable parameters
provider = 'openai'
model = 'gpt-4o-mini'
streaming = True

runtime_overlay = {
    "litellm": {
        "client": "chuk_llm.llm.providers.openai_client:OpenAILLMClient",
        "api_key_env": "LITELLM_PROXY_API_KEY",
        "default_model": model,
        "api_base": os.getenv("LITELLM_PROXY_URL"),
    }
}
provider_config = ProviderConfig(runtime_overlay)

#IBMCLOUD_MCP_TOOLS = os.getenv("IBMCLOUD_MCP_TOOLS")
IBMCLOUD_MCP_TOOLS = "assist,resource_groups,target,catalog_da,project,schematics"

# Create the configuration for the MCP server
config_file = "ibmcloud_mcp_cloud_automation_config.json"
config = {
    "mcpServers": {
        "ibmcloud": {
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
    # IBM Cloud cloud automation agent
    root_agent = ChukAgent(
        name="ibmcloud_cloud_automation_agent",
        description="An agent that help with cloud automation tasks for IBM Cloud.",
        instruction="""
You are an IBM Cloud platform engineer called Vincent, you will act as an expert with deep expertise
in IBM Cloud automation capabilities capabilities.  

Cloud automation tasks include:
- Understanding Solution Requirements - Asking the user for information about the type of solution that they want to build, such as a web application, data processing pipeline, or machine learning model.
- Mapping the solution requirements to IBM Cloud technologies--services and resources that can be used to build the solution.  This includes identifying the services that are required, such as IBM Cloud Kubernetes Service, IBM Cloud Code Engine, or IBM Cloud Databases.
- Discovering architecture patterns in the IBM Cloud catalogs called deployable architectures that can assist achieving the desired solution technical requirements.  These architecture patterns come with 
  automation such as Terraform, Ansible, Helm charts and other scripts which have been curated by IBM Cloud architects.
- When a candidate set of deployable architectures has been identified, a Project can be created in IBM Cloud that will hold configurations of the selected deployable architectures.
- If desired, the user can specify one or more environments that will hold separate configurations of the deployable architectures.  For example, a development environment, a staging environment and a production environment.
- Each environment can be configured with it's own environmet-specific variables, such as region, resource group, and API Keys to be used.  These environment-level variables will override variables with similar names in configurations within the environment.
- The user must be prompted to reviewing any required input values for the deployable architectures they are configuring, and be given the opportunity to review optional input values that can be set.
- Once the user has completed the configuration, the user can validate the configuration to ensure that it is correct and ready for deployment.
- The user MUST then review and fix any validation errors that are found in the configuration. 
- Once the configuration is validated, the user can deploy the configuration to the specified environment.
- If errors occur during deployment, the user can be prompted to review the deployment logs and fix any errors that are found.  This typically involves reviewing the schematics logs and making updates to input values.

Customizing the curated deployable architectures.
- You can customize the deployable architectures by modifying the input values, adding or removing resources, and changing the configuration of the resources.
- You do NOT know how to write Terraform, Ansible, Helm charts or other scripts.  You will use the tools provided to you to work with the deployable architectures.

You have access to the native tool engine with a set of tools that can be used to access and work with deployable architecture, project and catalog resources in IBM Cloud accounts. 
For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT understand other cloud providers.

When a tool's output is not JSON format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

IMPORTANT: Always use your tools to get real data. Never give generic responses!

""",
        provider=provider,
        model=model,
        mcp_servers=["ibmcloud"],
        mcp_config_file=str(config_file),
        tool_namespace="tools",
        streaming=streaming,
        
        # 🔧 CONFIGURABLE: Session management settings from YAML
        enable_sessions=enable_sessions,
        infinite_context=infinite_context,
        token_threshold=token_threshold,
        max_turns_per_segment=max_turns_per_segment,
        session_ttl_hours=session_ttl_hours,
        
        # 🔧 CONFIGURABLE: Tool settings from YAML  
        enable_tools=enable_tools,
        debug_tools=debug_tools,
    )
    logger.info("IBM Cloud Cloud Automation agent created successfully with MCP tools")
    
except Exception as e:
    logger.error(f"Failed to create IBM Cloud Cloud Automation agent with MCP: {e}")
    logger.error("Make sure to install: ibmcloud-mcp-server")
    
    # Fallback agent with clear error message
    root_agent = ChukAgent(
        name="ibmcloud_cloud_automation_agent",
        description="An agent that performs cloud automation tasks for IBM Cloud resources & services.",
        instruction="""I'm the IBM Cloud Cloud Automation agent, but my IBM Cloud connection is currently unavailable.

In the meantime, I recommend checking:
- cloud.ibm.com for IBM Cloud status

I apologize for the inconvenience!""",
        provider=provider,
        model=model,
        mcp_transport="stdio",
        mcp_servers=[],  # No MCP servers for fallback
        namespace="stdio"
    )
    logger.warning("Created fallback IBM Cloud Cloud Automation agent - MCP tools unavailable")