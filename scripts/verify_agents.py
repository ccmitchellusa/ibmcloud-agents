
import os
import glob
import sys
import logging

# Set PYTHONPATH to include src
sys.path.append(os.path.join(os.getcwd(), 'src'))

from common.agent_factory import AgentFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_agents")

AGENTS_DIR = "src/agents"

def verify():
    # Find all yaml files in src/agents
    agent_files = glob.glob(os.path.join(AGENTS_DIR, "*.yaml"))
    
    print(f"Verifying {len(agent_files)} agent YAML files...")
    
    success_count = 0
    failure_count = 0
    failed_agents = []
    
    for yaml_path in agent_files:
        try:
            # We just try to load the config to check structure, 
            # and then try to create the agent roughly.
            # However, create_agent might try to import or invoke things that need env vars.
            # Let's start with just loading YAML structure validation
            config = AgentFactory.load_yaml(yaml_path)
            
            # Check basic fields
            if not all(k in config for k in ['name', 'description', 'instruction']):
                raise ValueError("Missing required fields")
                
            # Check MCP fields if present
            if 'mcp' in config:
                mcp = config['mcp']
                if not all(k in mcp for k in ['tools']):
                     # server_name and config_file are technically optional in base logic if not enabling tools? 
                     # But our factory requires them for MCP enablement.
                     # But let's check if they exist in valid agents.
                     pass
            
            # Try full factory creation (mocking might be needed if it connects to things?)
            # AgentFactory.create_agent_from_yaml instantiates ChukAgent.
            # ChukAgent init is heavy, so let's stick to structural validation mostly.
            # But let's try calling create_agent_from_yaml with enable_tools=False to test instantiation logic.
            
            AgentFactory.create_agent_from_yaml(yaml_path, enable_tools=False)
            
            # logger.info(f"OK: {os.path.basename(yaml_path)}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"FAILED: {os.path.basename(yaml_path)} - {e}")
            failure_count += 1
            failed_agents.append(os.path.basename(yaml_path))

    print(f"\nVerification Complete.")
    print(f"Success: {success_count}")
    print(f"Failed: {failure_count}")
    
    if failure_count > 0:
        print("\nFailed Agents:")
        for fa in failed_agents:
            print(f"- {fa}")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    verify()
