
import json
import os
import glob
import yaml
from pathlib import Path

# Configuration
MCP_SRC_DIR = "/Users/chrism1/Code/ai/agentic/mcp/ibmcloud/mcp/src"
AGENTS_DIR = "/Users/chrism1/Code/ai/agentic/a2a/ibmcloud-agents/src/agents"

# Core Styling Prompt (extracted from core/README.md)
CORE_STYLING_PROMPT = """
Use the following styles when listing services in the catalog:

- Use 💰 for plans 
- Use ⚙️ for services
- Use 📍for deployments.
- Display country flags next to geographic locations when possible.
- Use ⛭ for service instances
- Use ㊮ for resource instances
- Use ⛬ before resource groups
- Use 📚 before catalogs
- Use 🏷️ before tags
- Use 📁 for account groups
- Use 🏦 for accounts
- Display 🥞for full stack Install Types
- Display 💾for software Install Types
- Display ⚙️for terraform Install Types
- Use 👔 before power workspaces
- Use 💻 before instances (power, z, x86/amd64 virtual server instances)
- Use ☁️ before “off-prem” (eg. Public cloud)
- Use 🏢 before “on-prem”
- Use 💿 before image names
- Use 🗄️ before volumes
- Use 👤 before user id’s 
- Use ⚙️ before service id’s 
- use 🔐👥 before access group names
- use 👤🔑 before user api key names and ids 
- use ⚙️🔑 before service api key names and ids 
- Use 🧑‍💼 for manager roles
- Use 🎛️ for operator roles
- Use 👨‍⚖️ for administrator roles
- Use 👁️ for viewer roles
- Use ✍️ for editor roles
- Use 👓 for reader roles
- Use ✍️for writer roles
- Use 📧 next to email id’s, within a link to mail the user.
- Use 📜🔑 next to access policy
- Display appropriate icons for state 
- Display appropriate icons for current status and health status
- When showing emails of user id’s, don’t use links
- Use appropriate icons for user state
"""

def generate_agents():
    print(f"Scanning {MCP_SRC_DIR}...")
    
    # Ensure agents directory exists
    os.makedirs(AGENTS_DIR, exist_ok=True)
    
    # Find all mcp.*.json configs
    config_pattern = os.path.join(MCP_SRC_DIR, "*", "configs", "mcp.*.json")
    config_files = glob.glob(config_pattern)
    
    print(f"Found {len(config_files)} config files.")
    
    for config_path in config_files:
        if "all-tools" in config_path or "status" in config_path:
            print(f"Skipping {config_path}")
            continue
            
        try:
            # Parse Config
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Extract domain
            # Path: .../src/<domain>/configs/mcp.<variant>.json
            path_obj = Path(config_path)
            domain = path_obj.parent.parent.name
            filename = path_obj.name
            
            # Extract tools
            server_name_key = list(data.get('mcpServers', {}).keys())[0]
            server_config = data['mcpServers'][server_name_key]
            args = server_config.get('args', [])
            
            tools_list = ""
            if '--mcp-tools' in args:
                idx = args.index('--mcp-tools')
                if idx + 1 < len(args):
                    tools_list = args[idx+1]
            
            if not tools_list:
                print(f"Warning: No tools found in {filename}, using generic approach or skipping if empty.")
                # Some configs might not have tools defined in list if it's "all", but we skip all-tools.
                # Let's verify if 'args' is list of strings or what.
            
            # Construct Agent Data
            # Name: ibmcloud_<domain>_<variant>_agent
            # Variant comes from mcp.<variant>.json
            variant_part = filename.replace("mcp.", "").replace(".json", "")
            
            # If variant is same as domain (e.g. mcp.cbr.json in cbr), just ibmcloud_cbr_agent?
            # Or ibmcloud_cbr_cbr_agent? 
            # Existing examples: ibmcloud_serverless_agent using serverless/configs/mcp.code_engine.json (wait, manual match?)
            # The existing ibmcloud_serverless_agent uses serverless/configs/ibmcloud_mcp_serverless_agent_config.json which seems to be custom or renamed?
            # The user request says "Agent Factory... thousands of tools... create configurations".
            # The user wants to create agents FOR THE existing configs.
            
            agent_name = f"ibmcloud_{domain}_{variant_part}_agent".replace("-", "_").lower()
            
            # Agent YAML Content
            # Extract 'when_to_use' information
            # Priority 1: Enhanced Metadata JSON (if available)
            # Priority 2: README extraction (heuristic)
            # Priority 3: Fallback generic text
            
            when_to_use = f"General purpose agent for {domain} {variant_part}"
            
            # Load enhanced metadata if not already loaded
            if 'enhanced_metadata' not in globals():
                metadata_path = os.path.join(os.path.dirname(__file__), "enhanced_metadata.json")
                try:
                    with open(metadata_path, 'r') as mf:
                        globals()['enhanced_metadata'] = json.load(mf)
                except Exception as e:
                    print(f"Warning: Could not load enhanced_metadata.json: {e}")
                    globals()['enhanced_metadata'] = {}
            
            enhanced_metadata = globals()['enhanced_metadata']
            
            codename = None
            if agent_name in enhanced_metadata:
                entry = enhanced_metadata[agent_name]
                if isinstance(entry, dict):
                    when_to_use = entry.get('when_to_use', when_to_use)
                    codename = entry.get('codename')
                else:
                    when_to_use = entry
            else:
                # Fallback to README heuristic
                readme_path = os.path.join(path_obj.parent.parent, "README.md")
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r') as rf:
                             readme_content = rf.read()
                            
                        # Look for the config filename in the README
                        lines = readme_content.split('\n')
                        for line in lines:
                            if filename in line:
                                parts = line.split(" - ")
                                if len(parts) > 1:
                                    potential_desc = parts[1].strip()
                                    if potential_desc:
                                        when_to_use = potential_desc
                                        break
                    except Exception as re:
                         print(f"Error reading README {readme_path}: {re}")

            capabilities = {
                "concurrency_group": "ibm_cloud_mcp",
                "when_to_use": when_to_use
            }
            
            if codename:
                capabilities["codename"] = codename

            agent_yaml = {
                "name": agent_name,
                "description": f"IBM Cloud agent for {domain} focusing on {variant_part}.",
                "instruction": f"""
You are an expert IBM Cloud automation agent specializing in {domain} and {variant_part}.
Your goal is to assist the user with tasks related to this domain using the provided MCP tools.

IMPORTANT: Always use your tools to get real data. Never give generic responses!

{CORE_STYLING_PROMPT}
""",
                "capabilities": capabilities,
                "mcp": {
                    "tools": tools_list,
                    "server_name": f"ibmcloud-{domain}", # Approximate server name, usually arbitrary for stdio but good for logging
                    "config_file": f"{agent_name}.json",
                    "allow_write": True
                }
            }
            
            # Write YAML
            output_path = os.path.join(AGENTS_DIR, f"{agent_name}.yaml")
            with open(output_path, 'w') as f:
                yaml.dump(agent_yaml, f, sort_keys=False, width=1000)
            
            print(f"Generated {agent_name} at {output_path}")

        except Exception as e:
            print(f"Failed to process {config_path}: {e}")

if __name__ == "__main__":
    generate_agents()
