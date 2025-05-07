# ibmcloud_base_agent_a2a/agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

AGENT_MODEL = "openai/gpt-4o-mini"

async def create_agent():
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='ibmcloud',
            args=["--mcp-transport",    
                "stdio",
                "--mcp-include",
		"resource-group,project,da"
            ],
        )
    )
    agent = Agent(
        name="ibmcloud_base_agent",
        model=LiteLlm(model=AGENT_MODEL),
        description="An IBM Cloud platform engineer",
        # TODO: Replace with very specialized instructions for the IBM Cloud agent.
        instruction="You are an IBM Cloud platform engineer called Chris, you will act as a platform engineer with deep expertise in IBM Cloud service operations and patterns for cloud architecture. You have access to a set of tools that can be used to access resources in IBM Cloud accounts.",
        tools=tools
    )
    return agent,exit_stack

root_agent = create_agent()
