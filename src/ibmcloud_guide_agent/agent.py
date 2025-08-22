"""
IBM Cloud Guide Agent - extends the base agent with expert guidance capabilities.
"""
import logging
from ibmcloud_base_agent.agent import IBMCloudBaseAgent

logger = logging.getLogger(__name__)

class IBMCloudGuideAgent(IBMCloudBaseAgent):
    """IBM Cloud Guide Agent with expert guidance and documentation capabilities."""
    
    def create_guide_agent(self, **kwargs):
        """Create a guide agent with configurable parameters."""
        return self.create_agent(
            name="ibmcloud_guide_agent",
            description="An expert Guide that can assist with any questions about IBM Cloud.",
            instruction="""
You are an expert guide for IBM Cloud called Brian, you will act as an expert with deep expertise
in IBM Cloud capabilities and including catalog services. You have access to the native tool engine with a set of tools that can be used 
to access specialized information about IBM Cloud. For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT 
understand other cloud providers.

When a tool's output is not json format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.
""",
            mcp_tools="guide,docs,catalog,services",
            mcp_server_name="ibmcloud-guide",
            config_file="ibmcloud_mcp_guide_agent_config.json",
            **kwargs
        )

# Global instance
_guide_instance = IBMCloudGuideAgent()

def create_guide_agent(**kwargs):
    """Create a guide agent with configurable parameters."""
    return _guide_instance.create_guide_agent(**kwargs)

# For direct import compatibility
try:
    root_agent = create_guide_agent(enable_tools=True)
except Exception as e:
    logger.error(f"❌ Failed to create module-level guide_agent: {e}")
    root_agent = None

# Export everything for flexibility
__all__ = ['create_guide_agent', 'root_agent']