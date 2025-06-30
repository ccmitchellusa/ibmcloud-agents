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
IBMCLOUD_MCP_TOOLS = "assist"

# Create the configuration for the MCP server
config_file = "ibmcloud_mcp_guide_config.json"
config = {
    "mcpServers": {
        "ibmcloud": {
            "command": "ibmcloud",
            "args": [        
                "--mcp-transport",
                "stdio",
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
        name="ibmcloud_guide_agent",
        description="An expert Guide that can assist with any questions about IBM Cloud.",
        instruction="""
    You are an expert guide for IBM Cloud called Brian, you will act as an expert with deep expertise
    in IBM Cloud capabilities and including catalog services. You have access to the native tool engine with a set of tools that can be used 
    to access specialized information about IBM Cloud. For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT 
    understand other cloud providers.

    When a tool's output is not json format, display the tool's output without further summary or transformation for display--unless specifically asked 
    to do so by the user.",
    """,
        mcp_servers=["ibmcloud"],
        mcp_config_file=str(config_file),
        tool_namespace="tools",
        provider=provider,
        model=model,
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
    logger.info("IBM Cloud Guide agent created successfully with MCP tools")
   
except Exception as e:
    logger.error(f"Failed to create IBM Cloud Guide agent with MCP: {e}")
    logger.error("Make sure to install: ibmcloud-mcp-server")
    
    # Fallback agent with clear error message
    root_agent = ChukAgent(
        name="ibmcloud_base_agent",
        description="An expert Guide that can assist with any questions about IBM Cloud.",
        instruction="""I'm the IBM Cloud Guide agent, but my IBM Cloud connection is currently unavailable.

In the meantime, I recommend checking:
- cloud.ibm.com for IBM Cloud status

I apologize for the inconvenience!""",

        provider=provider,
        model=model,
        mcp_transport="stdio",
        mcp_servers=[],  # No MCP servers for fallback
        namespace="stdio"
    )
    logger.warning("Created fallback IBM Cloud Guide agent - MCP tools unavailable")
