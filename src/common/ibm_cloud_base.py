"""
Base class for IBM Cloud agents.
Moved from ibmcloud_base_agent.agent to avoid circular imports with AgentFactory.
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
    
    def _create_mcp_config(
        self, 
        config_file: str, 
        mcp_tools: str, 
        server_name: str, 
        allow_write: bool = False,
        additional_servers: Optional[Dict[str, Any]] = None
    ) -> None:
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
        
        if additional_servers:
            config["mcpServers"].update(additional_servers)
        
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
        additional_mcp_servers: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
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
            additional_mcp_servers: Dictionary of additional MCP server configurations
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
        
        # Add capabilities if provided
        if capabilities:
            agent_params['capabilities'] = capabilities
        
        try:
            if mcp_tools and mcp_server_name and config_file and agent_params['enable_tools']:
                # Create MCP configuration
                self._create_mcp_config(
                    config_file, 
                    mcp_tools, 
                    mcp_server_name, 
                    allow_write,
                    additional_servers=additional_mcp_servers
                )
                
                # Collect all server names
                all_server_names = [mcp_server_name]
                if additional_mcp_servers:
                    all_server_names.extend(additional_mcp_servers.keys())
                
                # Create agent with MCP tools
                agent = ChukAgent(
                    name=name,
                    description=description,
                    instruction=instruction,
                    mcp_servers=all_server_names,
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
