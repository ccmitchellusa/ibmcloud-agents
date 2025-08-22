"""
IBM Cloud Serverless Agent - extends the base agent with serverless computing capabilities.
"""
import logging
from ibmcloud_base_agent.agent import IBMCloudBaseAgent

logger = logging.getLogger(__name__)

class IBMCloudServerlessAgent(IBMCloudBaseAgent):
    """IBM Cloud Serverless Agent with Code Engine and serverless computing capabilities."""
    
    def create_serverless_agent(self, **kwargs):
        """Create a serverless agent with configurable parameters."""
        return self.create_agent(
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
If a current resource group has not been targetted, target the 'default' resource group, then display the targets to the user.

IMPORTANT: Always use your tools to get real data. Never give generic responses!
""",
            mcp_tools="target,resource_groups,code-engine_application_list,code-engine_project_select,code-engine_project_list,code-engine_project_get,code-engine_project_current,code-engine_application_get,code-engine_application_logs,code-engine_application_restart,code-engine_application_create,code-engine_build_list,code-engine-build_get,code-engine_application_events,code-engine_buildrun_logs,code-engine_buildrun_list,code-engine_buildrun_get",
            mcp_server_name="ibmcloud-serverless",
            config_file="ibmcloud_mcp_serverless_agent_config.json",
            allow_write=True,
            **kwargs
        )

# Global instance
_serverless_instance = IBMCloudServerlessAgent()

def create_serverless_agent(**kwargs):
    """Create a serverless agent with configurable parameters."""
    return _serverless_instance.create_serverless_agent(**kwargs)

# For direct import compatibility
try:
    root_agent = create_serverless_agent(enable_tools=True)
except Exception as e:
    logger.error(f"❌ Failed to create module-level serverless_agent: {e}")
    root_agent = None

# Export everything for flexibility
__all__ = ['create_serverless_agent', 'root_agent']