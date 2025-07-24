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

def create_account_admin_agent(**kwargs):
    """
    Create an account admin agent with configurable parameters.
    
    Args:
        **kwargs: Configuration parameters passed from YAML
    """    

    # Extract session-related parameters with defaults

    enable_sessions = kwargs.get('enable_sessions', True)  # Default to False for utility agents
    enable_tools = kwargs.get('enable_tools', True)         # Default to True for MCP tools
    debug_tools = kwargs.get('debug_tools', False)
    infinite_context = kwargs.get('infinite_context', True)
    token_threshold = kwargs.get('token_threshold', 4000)
    max_turns_per_segment = kwargs.get('max_turns_per_segment', 50)
    session_ttl_hours = kwargs.get('session_ttl_hours', 24) # hours
    
    # Extract other configurable parameters
    provider = kwargs.get('provider', 'openai')
    model = kwargs.get('model', 'gpt-4o-mini')
    streaming = kwargs.get('streaming', True)
    
    # MCP configuration
    config_file = kwargs.get('mcp_config_file', "ibmcloud_mcp_account_admin_config.json")
    mcp_servers = kwargs.get('mcp_servers', ["ibmcloud-account-admin"])

    logger.info(f"🕒 Creating account admin agent with sessions: {enable_sessions}")
    logger.info(f"🕒 Using model: {provider}/{model}")
    logger.info(f"🕒 MCP tools enabled: {enable_tools}")
 
    try:
        if enable_tools:
            # Try to create with MCP tools
            try:
                # IBM Cloud serverless computing agent
                root_agent = ChukAgent(
                    name="ibmcloud_account_admin_agent",
                    description="An IBM Cloud agent that help with account and IAM administrative tasks.",
                    instruction="""
You are an IBM Cloud platform engineer called Carlos, you will act as an expert with deep expertise
in IBM Cloud account and Identity and Access Management (IAM) capabilities. 
You have access to the native tool engine with a set of tools that can be used 
to access and work with code engine resources in IBM Cloud accounts. 
For all subsequent prompts, assume the user is interacting with IBM Cloud--you do NOT understand other cloud providers.

When a tool's output is not JSON format, display the tool's output without further summary or transformation for display--unless specifically asked 
to do so by the user.

IMPORTANT: Always use your tools to get real data. Never give generic responses!

To determine what a USER_ID has access to:
1. Find the access policies that the user is assigned to.
2. Find the access groups that are available. The access group details include information like the role(s) and resources that users assigned to the access group can use.
3. For each access group check the access groups list of users to see if USER_ID is listed.
4. Display a detailed report that provides information about what the user has access to.""",
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
                    mcp_transport="stdio",
                    mcp_config_file=str(config_file),
                    mcp_servers=["ibmcloud-account-admin"],
                    namespace="stdio",

                    # Pass through any other kwargs
                    **{k: v for k, v in kwargs.items() if k not in [
                        'enable_sessions', 'enable_tools', 'debug_tools',
                        'infinite_context', 'token_threshold', 'max_turns_per_segment',
                        'session_ttl_hours', 'provider', 'model', 'streaming',
                        'mcp_config_file', 'mcp_servers'
                    ]}
                )
                logger.info("IBM Cloud Account Admin agent created successfully with MCP tools")
                
            except Exception as mcp_error:
                logger.error(f"🕒 Failed to create IBM Cloud Account Admin agent. MCP initialization failed: {mcp_error}")
                logger.error("🕒 Make sure to install: ibmcloud-mcp-server")
                logger.info("🕒 Creating fallback agent without MCP tools")
                enable_tools = False
                
        if not enable_tools:        
            # Fallback agent with clear error message
            root_agent = ChukAgent(
                name="ibmcloud_account_admin_agent",
                provider=provider,
                model=model,
                description="An IBM Cloud agent that performs account administration tasks.",
                instruction="""I'm the IBM Cloud Account Admin agent, but my IBM Cloud connection is currently unavailable.

In the meantime, I recommend checking:
- cloud.ibm.com for IBM Cloud status

I apologize for the inconvenience!""",
                streaming=streaming,
                
                # Session management
                enable_sessions=enable_sessions,
                infinite_context=infinite_context,
                token_threshold=token_threshold,
                max_turns_per_segment=max_turns_per_segment,
                session_ttl_hours=session_ttl_hours,
                
                # Pass through any other kwargs
                **{k: v for k, v in kwargs.items() if k not in [
                    'enable_sessions', 'infinite_context', 'token_threshold',
                    'max_turns_per_segment', 'session_ttl_hours', 'provider',
                    'model', 'streaming'
                ]}
            )
            logger.info("🕒 Created fallback Account Admin agent - MCP tools unavailable")  
            logger.warning("Created fallback IBM Cloud Account Admin agent - MCP tools unavailable")

    except Exception as e:
            logger.error(f"Failed to create Account Admin agent: {e}")
            logger.error("Creating basic Account Admin agent without tools")
            
            # Basic fallback
            agent = ChukAgent(
                name="account_admin_agent",
                provider=provider,
                model=model,
                description="An IBM Cloud agent that performs account administration tasks.",
                instruction="I'm the IBM Cloud Account Admin agent. I can usually help with general account administration tasks, but I'm not functioning properly at this time.",
                streaming=streaming,
                enable_sessions=enable_sessions,
                infinite_context=infinite_context,
                token_threshold=token_threshold,
                max_turns_per_segment=max_turns_per_segment,
                session_ttl_hours=session_ttl_hours
            )
        
            # Debug logging
            logger.info(f"🕒 Account Admin agent created: {type(agent)}")
            logger.info(f"🕒 Internal sessions enabled: {agent.enable_sessions}")
            logger.info(f"🕒 Tools enabled: {getattr(agent, 'enable_tools', False)}")
            
            if enable_sessions:
                logger.info(f"🕒 Agent will manage account admin sessions internally")
            else:
                logger.info(f"🕒 External sessions will be managed by handler")
            
            return agent

# 🔧 OPTIMIZED: Lazy loading to prevent duplicate creation
_account_admin_agent_cache = None

def get_account_admin_agent():
    """Get or create a default account admin agent instance (cached)."""
    global _account_admin_agent_cache
    if _account_admin_agent_cache is None:
        _account_admin_agent_cache = create_account_admin_agent(enable_tools=True)  # Conservative default
        logger.info("✅ Cached account_admin_agent created")
    return _account_admin_agent_cache

# 🔧 OPTIMIZED: Create module-level agent only when accessed
@property
def _account_admin_agent():
    """Module-level account admin agent instance (lazy loaded)."""
    return get_account_admin_agent()

# For direct import compatibility, create the instance
try:
    account_admin_agent = get_account_admin_agent()
except Exception as e:
    logger.error(f"❌ Failed to create module-level account_admin_agent: {e}")
    account_admin_agent = None

# Export everything for flexibility
__all__ = ['create_account_admin_agent', 'get_account_admin_agent', 'account_admin_agent']