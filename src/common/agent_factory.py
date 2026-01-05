
import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from a2a_server.tasks.handlers.chuk.chuk_agent import ChukAgent
from common.ibm_cloud_base import IBMCloudBaseAgent

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating agents from YAML definitions."""

    @staticmethod
    def load_yaml(yaml_path: str) -> Dict[str, Any]:
        """Load YAML configuration from file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load agent YAML from {yaml_path}: {e}")
            raise

    @staticmethod
    def create_agent_from_yaml(yaml_path: str, **kwargs) -> ChukAgent:
        """
        Create an agent instance from a YAML definition file.

        Args:
            yaml_path: Path to the agent.yaml file.
            **kwargs: Additional runtime overrides (like enable_tools, sessions etc).

        Returns:
            ChukAgent: Configured agent instance.
        """
        config = AgentFactory.load_yaml(yaml_path)
        
        # Get directory of the YAML file for relative path resolution
        base_dir =  os.path.dirname(os.path.abspath(yaml_path))

        # Extract core fields
        name = config.get('name')
        description = config.get('description')
        instruction = config.get('instruction')

        if not all([name, description, instruction]):
             raise ValueError(f"Agent YAML at {yaml_path} missing required fields: name, description, instruction")

        # Extract MCP config
        mcp_config = config.get('mcp', {})
        mcp_tools = mcp_config.get('tools')
        mcp_server_name = mcp_config.get('server_name')
        mcp_config_filename = mcp_config.get('config_file')
        allow_write = mcp_config.get('allow_write', False)
        additional_servers = mcp_config.get('additional_servers', None)
        
        # Extract capabilities
        capabilities = config.get('capabilities', {})

        # Resolve config file path if present
        mcp_config_file_path = None
        if mcp_config_filename:
             # Try relative to the yaml file first, if not exist, try finding it in root
             # Actually, simpler is to assume it's valid relative path or just a filename in root
             # The existing code expects config_file to be a path or filename.
             # Let's try to resolve it relative to module if it looks like a filename
             # But the current implementation of underlying _create_mcp_config writes to this path.
             # So we should probably keep it as is or resolve it carefully.
             # For now, pass it through, but if it was relative in the yaml, we might want to fix it.
             # However, existing agents put config json in root. Let's assume filename for now.
             mcp_config_file_path = mcp_config_filename

        # Base agent instance for creation logic
        # We use the existing IBMCloudBaseAgent.create_agent helper to reuse its logic 
        # for creating fallback agents etc.
        base_agent = IBMCloudBaseAgent()
        
        return base_agent.create_agent(
            name=name,
            description=description,
            instruction=instruction,
            mcp_tools=mcp_tools,
            mcp_server_name=mcp_server_name,
            config_file=mcp_config_file_path,
            allow_write=allow_write,
            additional_mcp_servers=additional_servers,
            capabilities=capabilities,
            **kwargs
        )
