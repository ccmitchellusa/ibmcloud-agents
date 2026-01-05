"""
Kingsmen Agent Handler - Elite IBM Cloud Operations Team.

The Kingsmen agent creates a specialized team of IBM Cloud agents,
each with specific roles and expertise areas. Like the elite spy organization,
each agent has a codename and specialized skills.
"""

import os
import glob
import logging
import yaml
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from supervisor_agent.supervisor_handler import SupervisorHandler

logger = logging.getLogger(__name__)


@dataclass
class KingsmanAgent:
    """Represents a Kingsman agent with their specialization."""
    codename: str
    real_name: str
    url: str
    expertise: str
    description: str
    specialties: List[str]


class KingsmenHandler(SupervisorHandler):
    """
    Kingsmen Agent Handler - An elite team of IBM Cloud specialists.
    
    The Kingsmen are a specialized team where each agent has a codename
    and specific area of expertise within IBM Cloud operations.
    """
    
    def __init__(
        self,
        agent=None,
        name: str = "kingsmen_agent",
        model: Optional[str] = None,
        team_environment: str = "localhost",
        custom_roster: Optional[List[KingsmanAgent]] = None,
        base_url_template: str = "http://localhost:8000/{agent_name}",
        **kwargs
    ):
        """
        Initialize the Kingsmen team.
        
        Args:
            agent: Base agent (inherited from SupervisorHandler)
            name: Handler name
            model: LLM model for coordination
            team_environment: Environment for team deployment (localhost, staging, prod)
            custom_roster: Override default roster with custom agents
            base_url_template: Template for constructing agent URLs
            **kwargs: Additional configuration
        """
        
        # Configure the team based on environment
        self.team_environment = team_environment
        self.base_url_template = base_url_template
        
        # Load roster dynamically if not customized
        self.roster = custom_roster or self._load_roster_from_yaml()
        
        # Build agent URLs from roster
        agent_urls = [agent.url for agent in self.roster]
        
        # Initialize the supervisor with our specialized team
        super().__init__(
            agent=agent,
            name=name,
            model=model or os.getenv('KINGSMEN_MODEL', 'gpt-4o-mini'),
            agent_urls=agent_urls,
            **kwargs
        )
        
        # Build enhanced agent registry with Kingsmen details
        self._build_kingsmen_registry()
        
        logger.info(f"Kingsmen team assembled with {len(self.roster)} agents in {team_environment} environment")
        for agent in self.roster:
            logger.info(f"  - {agent.codename} ({agent.real_name}): {agent.expertise}")
    
    def _load_roster_from_yaml(self) -> List[KingsmanAgent]:
        """
        Load the Kingsmen roster from agent YAML files.
        Scanning src/agents/*.yaml for 'kingsman' metadata.
        """
        roster = []
        # Path to agents directory - assuming relative to this file
        # src/kingsmen_agent/kingsmen_handler.py -> src/agents
        agents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
        yaml_files = glob.glob(os.path.join(agents_dir, "*.yaml"))
        
        for yaml_path in yaml_files:
            try:
                with open(yaml_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Check if this agent is a Kingsman
                if 'kingsman' in data:
                    k_data = data['kingsman']
                    agent_name = data.get('name', os.path.splitext(os.path.basename(yaml_path))[0])
                    
                    agent = KingsmanAgent(
                        codename=k_data.get('codename', 'Unknown'),
                        real_name=agent_name,
                        url=self.base_url_template.format(agent_name=agent_name),
                        expertise=k_data.get('expertise', ''),
                        description=k_data.get('description', ''),
                        specialties=k_data.get('specialties', [])
                    )
                    roster.append(agent)
                    logger.debug(f"Recruited Kingsman {agent.codename} from {yaml_path}")
            except Exception as e:
                logger.warning(f"Failed to load Kingsman metadata from {yaml_path}: {e}")
                
        return roster

    def _build_kingsmen_registry(self):
        """Build enhanced agent registry with Kingsmen-specific information."""
        # This will be populated when agents connect, but we can pre-populate known info
        for kingsman in self.roster:
            self.kingsmen_registry = getattr(self, 'kingsmen_registry', {})
            self.kingsmen_registry[kingsman.real_name] = {
                'codename': kingsman.codename,
                'expertise': kingsman.expertise,
                'description': kingsman.description,
                'specialties': kingsman.specialties,
                'url': kingsman.url
            }
    
    async def _select_agent(self, user_text: str, history: List[Dict]) -> Optional[str]:
        """
        Enhanced agent selection using Kingsmen codenames and expertise areas.
        
        Args:
            user_text: The user's request
            history: Conversation history
            
        Returns:
            Name of the selected agent or None
        """
        await self._ensure_connections()
        
        if not self.agent_connections:
            return None
        
        # Build enhanced agent descriptions with Kingsmen details
        agent_descriptions = []
        for kingsman in self.roster:
            # Check if agent is connected OR if we are in a mode where checking connection is difficult?
            # Ideally we only select connected agents
            if kingsman.real_name in self.agent_connections:
                specialties_str = ", ".join(kingsman.specialties)
                agent_descriptions.append(
                    f"- {kingsman.real_name} (Codename: {kingsman.codename})\n"
                    f"  Expertise: {kingsman.expertise}\n" 
                    f"  Description: {kingsman.description}\n"
                    f"  Specialties: {specialties_str}"
                )
        
        agents_description = "\n\n".join(agent_descriptions)
        
        # Enhanced system prompt with Kingsmen theme
        system_prompt = f"""You are Arthur, the leader of the Kingsmen - an elite team of IBM Cloud specialists.

Your team of agents:
{agents_description}

Analyze the user's request and respond with ONLY the agent name (not codename) that should handle it.
Do not include any explanation, just the agent name.

Choose the Kingsman whose expertise best matches the user's request.
If no agent is suitable, respond with 'none'."""
        
        try:
            # Use LLM with enhanced Kingsmen context
            
            response = await self.llm_client.create_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ]
            )
            
            selected = response.get('response', '').strip().lower()
            
            # Validate the selection
            for agent_name in self.agent_connections.keys():
                if agent_name.lower() == selected:
                    # Log the selection with Kingsmen details
                    kingsman = next((k for k in self.roster if k.real_name == agent_name), None)
                    if kingsman:
                        logger.info(f"Arthur selected {kingsman.codename} ({agent_name}) for this mission")
                    return agent_name
            
            if selected != 'none' and selected != '':
                logger.warning(f"Arthur selected unknown agent: {selected}")
            
            # Default fallback logic if LLM fails to pick a valid connected agent
            # Try to find 'ibmcloud_base_agent' if available
            if 'ibmcloud_base_agent' in self.agent_connections:
                logger.info("Arthur defaulting to Galahad (ibmcloud_base_agent) for this mission")
                return 'ibmcloud_base_agent'
            
            # Return first available agent
            return list(self.agent_connections.keys())[0] if self.agent_connections else None
            
        except Exception as e:
            logger.error(f"Error in Kingsmen agent selection: {e}")
            # Default fallback
            return list(self.agent_connections.keys())[0] if self.agent_connections else None
    
    def get_team_roster(self) -> List[Dict[str, Any]]:
        """
        Get the current Kingsmen team roster.
        
        Returns:
            List of agent information with codenames and expertise
        """
        roster_info = []
        for kingsman in self.roster:
            status = "Connected" if kingsman.real_name in self.agent_connections else "Disconnected"
            roster_info.append({
                'codename': kingsman.codename,
                'real_name': kingsman.real_name,
                'expertise': kingsman.expertise,
                'description': kingsman.description,
                'specialties': kingsman.specialties,
                'url': kingsman.url,
                'status': status
            })
        return roster_info
    
    def get_agent_by_codename(self, codename: str) -> Optional[KingsmanAgent]:
        """
        Get agent information by codename.
        
        Args:
            codename: Agent codename (e.g., "Galahad", "Lancelot")
            
        Returns:
            KingsmanAgent if found, None otherwise
        """
        return next((agent for agent in self.roster if agent.codename.lower() == codename.lower()), None)

    @classmethod
    def create_development_team(cls, **kwargs) -> 'KingsmenHandler':
        """
        Factory method to create a Kingsmen team for development environment.
        """
        return cls(
            name="kingsmen_dev_team",
            team_environment="development",
            base_url_template="http://localhost:8000/{agent_name}",
            **kwargs
        )

    @classmethod
    def create_production_team(cls, base_url: str = "https://agents.prod.example.com", **kwargs) -> 'KingsmenHandler':
        """
        Factory method to create a Kingsmen team for production environment.
        """
        return cls(
            name="kingsmen_prod_team",
            team_environment="production",
            base_url_template=f"{base_url}/{{agent_name}}",
            **kwargs
        )


def create_kingsmen_handler(**kwargs) -> KingsmenHandler:
    """
    Factory function to create a Kingsmen handler.
    
    Returns:
        Configured KingsmenHandler instance
    """
    return KingsmenHandler(
        name="kingsmen_agent",
        infinite_context=True,
        token_threshold=4000,
        max_turns_per_segment=50,
        default_ttl_hours=24,
        **kwargs
    )