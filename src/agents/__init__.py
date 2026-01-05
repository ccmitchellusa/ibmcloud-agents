
"""
Dynamic agent loader.
Scans the current directory for .yaml files and creates agent instances.
Exposes them as modules so they can be imported as:
from src.agents import agent_name
"""
import os
import sys
import glob
import logging
from types import ModuleType
from common.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

def _load_agents():
    """Load all agents from YAML files in this directory."""
    current_dir = os.path.dirname(__file__)
    yaml_files = glob.glob(os.path.join(current_dir, "*.yaml"))
    
    for yaml_path in yaml_files:
        try:
            # Extract agent name from filename
            filename = os.path.basename(yaml_path)
            agent_name = os.path.splitext(filename)[0]
            
            # Create the agent
            # We delay creation until access or create a pseudo-module?
            # The server expects to import the module and look for a `root_agent` or `create_agent`?
            # Actually, `agent.yaml` config points to:
            # type: ...
            # agent: package.module.object
            
            # So if we want `src.agents.ibmcloud_base_agent`, we need to simulate a module.
            # But simpler approach: 
            # We can't easily dynamically create submodules that are importable via standard import mechanism
            # without some sys.meta_path hooks.
            
            # However, we can just attach the objects to THIS module if the config allows:
            # agent: src.agents.ibmcloud_base_agent_instance
            
            # But the existing config uses: `agent: ibmcloud_serverless_agent.agent.root_agent`
            # We will change config to: `agent: src.agents.ibmcloud_serverless_agent` 
            # where `ibmcloud_serverless_agent` is an INSTANCE in THIS module.
            
            agent_instance = AgentFactory.create_agent_from_yaml(yaml_path, enable_tools=True)
            
            # Add to globals
            globals()[agent_name] = agent_instance
            
            logger.info(f"Loaded agent {agent_name} from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load agent from {yaml_path}: {e}")

# Load agents on import
_load_agents()
