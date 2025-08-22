"""
IBM Cloud Platform Engineering base agent with IBMCloud MCP Server built in.
This module provides a base class for creating IBM Cloud agents with common functionality.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from a2a_server.tasks.handlers.chuk.chuk_agent import ChukAgent
from chuk_llm.configuration import ProviderConfig

logger = logging.getLogger(__name__)

class IBMCloudBaseAgent:
    """Base class for IBM Cloud agents with common configuration and patterns."""
    
    def __init__(self):
        self.provider = os.getenv("PROVIDER", "openai")
        self.model = os.getenv("MODEL", "gpt-4o-mini")
        self.provider_config = self._create_provider_config()
    
    def _create_provider_config(self) -> ProviderConfig:
        """Create provider configuration with runtime overlay."""
        runtime_overlay = {
            "litellm": {
                "client": "chuk_llm.llm.providers.openai_client:OpenAILLMClient",
                "api_key_env": "LITELLM_PROXY_API_KEY",
                "default_model": self.model,
                "api_base": os.getenv("LITELLM_PROXY_URL"),
            }
        }
        return ProviderConfig(runtime_overlay)
    
    def _create_mcp_config(self, config_file: str, mcp_tools: str, server_name: str, allow_write: bool = False) -> None:
        """Create MCP configuration file."""
        args = [
            "--mcp-transport",
            "stdio",
        ]
        
        if allow_write:
            args.append("--mcp-allow-write")
            
        args.extend([
            "--mcp-tools",
            mcp_tools
        ])
        
        config = {
            "mcpServers": {
                server_name: {
                    "command": "ibmcloud",
                    "args": args
                }
            }
        }
        
        config_path = Path(config_file)
        config_path.write_text(json.dumps(config, indent=2))
    
    def create_agent(
        self,
        name: str,
        description: str,
        instruction: str,
        mcp_tools: Optional[str] = None,
        mcp_server_name: Optional[str] = None,
        config_file: Optional[str] = None,
        allow_write: bool = False,
        **kwargs
    ) -> ChukAgent:
        """
        Create an IBM Cloud agent with common configuration.
        
        Args:
            name: Agent name
            description: Agent description
            instruction: Agent instruction/prompt
            mcp_tools: Comma-separated list of MCP tools
            mcp_server_name: Name of the MCP server
            config_file: Path to MCP config file
            allow_write: Whether to allow write operations
            **kwargs: Additional parameters for ChukAgent
        """
        # Set default session and tool parameters
        default_params = {
            'enable_sessions': kwargs.get('enable_sessions', True),
            'enable_tools': kwargs.get('enable_tools', True),
            'debug_tools': kwargs.get('debug_tools', False),
            'infinite_context': kwargs.get('infinite_context', True),
            'token_threshold': kwargs.get('token_threshold', 4000),
            'max_turns_per_segment': kwargs.get('max_turns_per_segment', 50),
            'session_ttl_hours': kwargs.get('session_ttl_hours', 24),
            'provider': kwargs.get('provider', self.provider),
            'model': kwargs.get('model', self.model),
            'streaming': kwargs.get('streaming', True),
            'tool_namespace': kwargs.get('tool_namespace', "tools"),
            'namespace': kwargs.get('namespace', "stdio")
        }
        
        # Update with any additional kwargs
        agent_params = {**default_params, **kwargs}
        
        try:
            if mcp_tools and mcp_server_name and config_file and agent_params['enable_tools']:
                # Create MCP configuration
                self._create_mcp_config(config_file, mcp_tools, mcp_server_name, allow_write)
                
                # Create agent with MCP tools
                agent = ChukAgent(
                    name=name,
                    description=description,
                    instruction=instruction,
                    mcp_servers=[mcp_server_name],
                    mcp_config_file=str(config_file),
                    **agent_params
                )
                
                logger.info(f"{name} created successfully with MCP tools")
                return agent
                
        except Exception as e:
            logger.error(f"Failed to create {name} with MCP: {e}")
            logger.error("Make sure to install: ibmcloud-mcp-server")
            agent_params['enable_tools'] = False
        
        # Create fallback agent without MCP tools
        fallback_instruction = f"""I'm the {name}, but my IBM Cloud connection is currently unavailable.

In the meantime, I recommend checking:
- cloud.ibm.com for IBM Cloud status

I apologize for the inconvenience!"""
        
        # Remove MCP-specific parameters for fallback
        fallback_params = {k: v for k, v in agent_params.items() 
                          if k not in ['mcp_servers', 'mcp_config_file']}
        
        agent = ChukAgent(
            name=name,
            description=description,
            instruction=fallback_instruction,
            **fallback_params
        )
        
        logger.warning(f"Created fallback {name} - MCP tools unavailable")
        return agent

# Global instance for backward compatibility
_base_agent_instance = IBMCloudBaseAgent()

def create_base_agent(**kwargs) -> ChukAgent:
    """Create a basic IBM Cloud base agent."""
    return _base_agent_instance.create_agent(
        name="ibmcloud_base_agent",
        description="An IBM Cloud platform engineering base agent that can do basic IBM Cloud resource management.",
        instruction="""
You are an IBM Cloud platform engineer called Chris, you will act as a platform engineer with deep expertise
in IBM Cloud service operations and patterns for cloud architecture. You have access to the native tool engine with a set of tools that can be used 
to access and work with cloud resources in IBM Cloud accounts. For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT 
understand other cloud providers.

When a tool's output is not JSON format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

In IBM Cloud, 'target' is a term used to describe how a user selects the accounts, resource groups, regions and api endpoints which act the scope or
context that will be used in subsequent tool calls. Use the target tool to get the currently targeted account, region, api endpoint and resource group. 
If a current resource group has not been targetted, target the 'default' resource group, then display the targets to the user.

IMPORTANT: Always use your tools to get real data. Never give generic responses!
""",
        **kwargs
    )

# Create default instance for backward compatibility
root_agent = create_base_agent()