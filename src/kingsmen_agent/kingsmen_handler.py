"""
Kingsmen Agent Handler - Elite IBM Cloud Operations Team

The Kingsmen agent creates a specialized team of IBM Cloud agents,
each with specific roles and expertise areas. Like the elite spy organization,
each agent has a codename and specialized skills.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..supervisor_agent.supervisor_handler import SupervisorHandler

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
    
    # Elite team roster with codenames and specializations
    KINGSMEN_ROSTER = [
        KingsmanAgent(
            codename="Galahad",
            real_name="ibmcloud_base_agent", 
            url="http://localhost:8000/ibmcloud_base_agent",
            expertise="Foundation & Infrastructure",
            description="The foundation specialist who handles core IBM Cloud resources and infrastructure management",
            specialties=["resource_groups", "service_instances", "targets", "basic_operations"]
        ),
        KingsmanAgent(
            codename="Lancelot",
            real_name="ibmcloud_account_admin_agent",
            url="http://localhost:8000/ibmcloud_account_admin_agent", 
            expertise="Security & Access Control",
            description="The security expert who manages accounts, users, and access policies with precision",
            specialties=["user_management", "iam_policies", "access_groups", "service_ids", "api_keys"]
        ),
        KingsmanAgent(
            codename="Percival",
            real_name="ibmcloud_serverless_agent",
            url="http://localhost:8000/ibmcloud_serverless_agent",
            expertise="Serverless & Modern Applications", 
            description="The modernization specialist focused on serverless computing and cloud-native applications",
            specialties=["code_engine", "functions", "serverless_apps", "container_deployments"]
        ),
        KingsmanAgent(
            codename="Gareth",
            real_name="ibmcloud_guide_agent",
            url="http://localhost:8000/ibmcloud_guide_agent",
            expertise="Strategy & Best Practices",
            description="The strategic advisor who provides guidance, best practices, and architectural recommendations",
            specialties=["best_practices", "architecture_guidance", "service_recommendations", "troubleshooting"]
        ),
        KingsmanAgent(
            codename="Tristan", 
            real_name="ibmcloud_cloud_automation_agent",
            url="http://localhost:8000/ibmcloud_cloud_automation_agent",
            expertise="Automation & DevOps",
            description="The automation expert who handles deployable architectures, projects, and infrastructure as code",
            specialties=["deployable_architectures", "projects", "schematics", "terraform", "automation_pipelines"]
        )
    ]
    
    def __init__(
        self,
        agent=None,
        name: str = "kingsmen_agent",
        model: Optional[str] = None,
        team_environment: str = "localhost",
        custom_roster: Optional[List[KingsmanAgent]] = None,
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
            **kwargs: Additional configuration
        """
        
        # Configure the team based on environment
        self.team_environment = team_environment
        self.roster = custom_roster or self.KINGSMEN_ROSTER
        
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

Selection Guidelines:
- For basic IBM Cloud operations and resource management → ibmcloud_base_agent (Galahad)
- For account administration, users, IAM, security → ibmcloud_account_admin_agent (Lancelot)
- For serverless, Code Engine, modern applications → ibmcloud_serverless_agent (Percival)
- For guidance, best practices, recommendations → ibmcloud_guide_agent (Gareth)
- For automation, deployable architectures, projects → ibmcloud_cloud_automation_agent (Tristan)

Choose the Kingsman whose expertise best matches the user's request.
If no agent is suitable, respond with 'none'."""
        
        try:
            # Use LLM with enhanced Kingsmen context
            from litellm import acompletion
            
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            selected = response.choices[0].message.content.strip().lower()
            
            # Validate the selection
            for agent_name in self.agent_connections.keys():
                if agent_name.lower() == selected:
                    # Log the selection with Kingsmen details
                    kingsman = next((k for k in self.roster if k.real_name == agent_name), None)
                    if kingsman:
                        logger.info(f"Arthur selected {kingsman.codename} ({agent_name}) for this mission")
                    return agent_name
            
            if selected != 'none':
                logger.warning(f"Arthur selected unknown agent: {selected}")
            
            # Default to Galahad (base agent) if available
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
        
        Returns:
            Configured KingsmenHandler for development
        """
        return cls(
            name="kingsmen_dev_team",
            team_environment="development",
            **kwargs
        )
    
    @classmethod
    def create_production_team(cls, base_url: str = "https://agents.prod.example.com", **kwargs) -> 'KingsmenHandler':
        """
        Factory method to create a Kingsmen team for production environment.
        
        Args:
            base_url: Base URL for production agents
            
        Returns:
            Configured KingsmenHandler for production
        """
        # Create production roster with custom URLs
        prod_roster = []
        for agent in cls.KINGSMEN_ROSTER:
            prod_agent = KingsmanAgent(
                codename=agent.codename,
                real_name=agent.real_name,
                url=f"{base_url}/{agent.real_name}",
                expertise=agent.expertise,
                description=agent.description,
                specialties=agent.specialties
            )
            prod_roster.append(prod_agent)
        
        return cls(
            name="kingsmen_prod_team",
            team_environment="production", 
            custom_roster=prod_roster,
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