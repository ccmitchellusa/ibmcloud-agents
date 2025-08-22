"""
IBM Cloud Account Admin Agent - extends the base agent with account management capabilities.
"""
import logging
from ibmcloud_base_agent.agent import IBMCloudBaseAgent

logger = logging.getLogger(__name__)

class IBMCloudAccountAdminAgent(IBMCloudBaseAgent):
    """IBM Cloud Account Admin Agent with IAM management capabilities."""
    
    def create_account_admin_agent(self, **kwargs):
        """Create an account admin agent with configurable parameters."""
        return self.create_agent(
            name="ibmcloud_account_admin_agent",
            description="An IBM Cloud agent that help with account and IAM administrative tasks.",
            instruction="""
You are an IBM Cloud platform engineer called Carlos, you will act as an expert with deep expertise
in IBM Cloud account and Identity and Access Management (IAM) capabilities. 
You have access to the native tool engine with a set of tools that can be used 
to access and work with account and IAM resources in IBM Cloud accounts. 
For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT understand other cloud providers.

When a tool's output is not JSON format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

IMPORTANT: Always use your tools to get real data. Never give generic responses!

To determine what a USER_ID has access to:
1. Find the access policies that the user is assigned to.
2. Find the access groups that are available. The access group details include information like the role(s) and resources that users assigned to the access group can use.
3. For each access group check the access groups list of users to see if USER_ID is listed.
4. Display a detailed report that provides information about what the user has access to.""",
            mcp_tools="account,iam,users,access-groups,policies",
            mcp_server_name="ibmcloud-account-admin",
            config_file="ibmcloud_mcp_account_admin_config.json",
            **kwargs
        )

# Global instance
_account_admin_instance = IBMCloudAccountAdminAgent()

def create_account_admin_agent(**kwargs):
    """Create an account admin agent with configurable parameters."""
    return _account_admin_instance.create_account_admin_agent(**kwargs)

# Lazy loading cache
_account_admin_agent_cache = None

def get_account_admin_agent():
    """Get or create a default account admin agent instance (cached)."""
    global _account_admin_agent_cache
    if _account_admin_agent_cache is None:
        _account_admin_agent_cache = create_account_admin_agent(enable_tools=True)
        logger.info("✅ Cached account_admin_agent created")
    return _account_admin_agent_cache

# For direct import compatibility
try:
    account_admin_agent = get_account_admin_agent()
except Exception as e:
    logger.error(f"❌ Failed to create module-level account_admin_agent: {e}")
    account_admin_agent = None

# Export everything for flexibility
__all__ = ['create_account_admin_agent', 'get_account_admin_agent', 'account_admin_agent']