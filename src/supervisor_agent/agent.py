# multi_agent/agent.py

from .host_agent import HostAgent

remote_agent_addresses = [
#    'http://localhost:8000/account_admin_agent',
    'http://localhost:8000/base_agent',
#    'http://localhost:8000/serverless_agent',
#    'http://localhost:8000/guide_agent',
#    'http://localhost:8000/cloud_automation_agent'
]

# First argument is the array of agent URLs that this agent will be the host for.
root_agent = HostAgent(remote_agent_addresses).create_agent()
print("Created agent:", root_agent.name)