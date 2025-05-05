# ibmcloud_base_agent_a2a/agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

AGENT_MODEL = "openai/gpt-4o-mini"

root_agent = Agent(
    name="ibmcloud_base_agent",
    model=LiteLlm(model=AGENT_MODEL),
    description="An IBM Cloud platform engineer",
    instruction="You are an IBM Cloud platform engineer called Chris, you will act as a platform engineer with deep expertise in IBM Cloud service operations and patterns for cloud architecture. You have access to a set of tools that can be used to access resources in IBM Cloud accounts."
)