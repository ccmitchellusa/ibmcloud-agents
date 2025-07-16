import json

import httpx

from common.types import (
    A2AClientJSONError,
    AgentCard,
)

TIMEOUT = 60  # (seconds) Give some extra time for agent instances to spin up that may have scaled down to 0.

class A2ACardResolver:
    def __init__(self, base_url, agent_card_path='/.well-known/agent.json'):
        self.base_url = base_url.rstrip('/')
        self.agent_card_path = agent_card_path.lstrip('/')

    def get_agent_card(self) -> AgentCard:
        with httpx.Client() as client:
            agent_card_url = self.base_url + '/' + self.agent_card_path
            print("Fetching agent card from:", agent_card_url)
            response = client.get(agent_card_url,timeout=TIMEOUT) 
            response.raise_for_status()
            try:
                return AgentCard(**response.json())
            except json.JSONDecodeError as e:
                raise A2AClientJSONError(str(e)) from e
