# ibmcloud_base_agent_a2a/agent.py
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import asyncio
import threading

AGENT_MODEL = "openai/gpt-4o-mini"
TOOL_FILTER = "resource-group,project,da"

#TODO: Load the above from os.environ

_loop = asyncio.new_event_loop()
_thr = threading.Thread(target=_loop.run_forever,name="Async Runner",daemon=True)

# This will block the calling thread until the coroutine is finished.
# Any exception that occurs in the coroutine is raised in the caller
def run_sync(coro):  # coro is a couroutine
    if not _thr.is_alive():
        _thr.start()
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result()

async def create_agent_with_mcp_servers():
    print("Spawning embedded MCP server(s)...")
    common_exit_stack = AsyncExitStack()
    print("Loading filesystem tools...")
    filesystem_tools, _ = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
                "/Users/chrism1/Code",
            ],
        ),
        async_exit_stack=common_exit_stack
    )
    print(f"Loading ibmcloud tools with filter: {TOOL_FILTER}")
    from mcp.client.stdio import get_default_environment
    print(get_default_environment())
    ibmcloud_tools, _ = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='/Users/chrism1/Code/cli/bluemix-cli/out/ibmcloud-darwin-arm64',
            args=[
                "--mcp-transport",    
                "stdio",
                "--mcp-tools",
		        TOOL_FILTER
            ]
        ),
        async_exit_stack=common_exit_stack
    )
 
    print("Creating agent...")
    agent = Agent(
        name="ibmcloud_base_agent",
        model=LiteLlm(model=AGENT_MODEL),
        description="An IBM Cloud platform engineer",
        # TODO: Replace with very specialized instructions for the IBM Cloud agent.
        instruction="You are an IBM Cloud platform engineer called Chris, you will act as a platform engineer with deep expertise " \
            "in IBM Cloud service operations and patterns for cloud architecture. You have access to a set of tools that can be used " \
            "to access and work with cloud resources in IBM Cloud accounts."\
            "Ask the user what resource group to target, and offer to list available resource groups.",
        tools=[
            *filesystem_tools,
            *ibmcloud_tools
        ]
    )
    print("Agent created")
    return agent    # ,common_exit_stack  
                    # TODO: a2a_server doesnt handle coroutines or tuples returned here, but should
root_agent = run_sync(create_agent_with_mcp_servers())