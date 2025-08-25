"""
Supervisor agent handler using a2a-server framework.
This agent delegates tasks to other specialized agents via A2A protocol.
"""

import os
import uuid
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any, AsyncIterable
from datetime import datetime

from a2a_server.tasks.handlers.resilient_handler import ResilientHandler
from a2a_json_rpc.spec import (
    Message, 
    TaskStatusUpdateEvent, 
    TaskArtifactUpdateEvent,
    TaskStatus,
    TaskState,
    Part,
    TextPart
)

from ..common.simple_a2a_client import (
    RemoteAgentConnection,
    TaskRequest,
    Message as ClientMessage,
    TaskState as ClientTaskState
)

from litellm import acompletion

logger = logging.getLogger(__name__)


class SupervisorHandler(ResilientHandler):
    """
    Supervisor agent that delegates tasks to specialized agents.
    Built on the a2a-server framework without Google ADK dependencies.
    """
    
    def __init__(
        self,
        agent=None,  # Required by ResilientHandler but not used by supervisor
        name: str = "supervisor_agent",
        model: Optional[str] = None,
        agent_urls: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the supervisor handler.
        
        Args:
            agent: Not used by supervisor (required by base class)
            name: Name of the supervisor agent
            model: LLM model to use for coordination
            agent_urls: List of agent URLs to delegate to
            **kwargs: Additional arguments for ResilientHandler
        """
        # Create a dummy agent object since ResilientHandler expects one
        if agent is None:
            agent = type('DummyAgent', (), {'name': name})()
        
        super().__init__(agent=agent, name=name, **kwargs)
        
        # Configure model
        self.model = model or os.getenv('SUPERVISOR_MODEL', 'gpt-4o-mini')
        
        # Get agent URLs from parameter, YAML config, or environment
        if agent_urls:
            # Direct parameter takes highest priority - but handle different formats
            if isinstance(agent_urls, str):
                # Handle comma-separated string
                self.agent_urls = [url.strip() for url in agent_urls.split(',') if url.strip()]
                logger.info(f"Using agent URLs from parameter (string): {len(self.agent_urls)} URLs")
            elif isinstance(agent_urls, list):
                # Handle list
                self.agent_urls = [str(url).strip() for url in agent_urls if str(url).strip()]
                logger.info(f"Using agent URLs from parameter (list): {len(self.agent_urls)} URLs")
            else:
                logger.warning(f"Invalid agent_urls parameter format: {type(agent_urls)}")
                self.agent_urls = []
        else:
            # Check for agent_urls in kwargs (from YAML config)
            yaml_urls = kwargs.get('agent_urls', [])
            if yaml_urls:
                if isinstance(yaml_urls, str):
                    # Handle comma-separated string from YAML
                    self.agent_urls = [url.strip() for url in yaml_urls.split(',') if url.strip()]
                    logger.info(f"Processed string config into {len(self.agent_urls)} URLs")
                elif isinstance(yaml_urls, list):
                    # Handle list from YAML
                    self.agent_urls = [str(url).strip() for url in yaml_urls if str(url).strip()]
                    logger.info(f"Processed list config into {len(self.agent_urls)} URLs")
                else:
                    logger.warning(f"Invalid agent_urls format in YAML config: {type(yaml_urls)}")
                    self.agent_urls = []
                
                if self.agent_urls:
                    logger.info(f"Using agent URLs from YAML config: {len(self.agent_urls)} URLs")
                    # Early return to avoid fallback logic
                else:
                    logger.warning("YAML config resulted in empty agent URLs list")
                
            if not hasattr(self, 'agent_urls') or not self.agent_urls:
                # Fall back to environment variable
                env_urls = os.getenv('SUPERVISOR_AGENT_URLS', '')
                if env_urls:
                    self.agent_urls = [url.strip() for url in env_urls.split(',') if url.strip()]
                    logger.info(f"Using agent URLs from environment: {len(self.agent_urls)} URLs")
                else:
                    # Default URLs for unified server setup
                    self.agent_urls = [
                        'http://localhost:8000/ibmcloud_base_agent',
                        'http://localhost:8000/ibmcloud_account_admin_agent',
                        'http://localhost:8000/ibmcloud_serverless_agent',
                        'http://localhost:8000/ibmcloud_guide_agent',
                        'http://localhost:8000/ibmcloud_cloud_automation_agent'
                    ]
                    logger.info(f"Using default agent URLs for unified server: {len(self.agent_urls)} URLs")
        
        # Initialize agent connections
        self.agent_connections: Dict[str, RemoteAgentConnection] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self._connections_initialized = False
    
    async def _ensure_connections(self):
        """Ensure agent connections are initialized."""
        if not self._connections_initialized:
            await self._connect_to_agents()
            self._connections_initialized = True
    
    async def _connect_to_agents(self):
        """Connect to all configured agents."""
        logger.info(f"Connecting to {len(self.agent_urls)} remote agents")
        
        for url in self.agent_urls:
            try:
                logger.info(f"Connecting to agent at {url}")
                connection = RemoteAgentConnection(url)
                
                if await connection.connect():
                    agent_name = connection.card.name
                    self.agent_connections[agent_name] = connection
                    self.agent_registry[agent_name] = {
                        'name': agent_name,
                        'description': connection.card.description,
                        'url': url,
                        'streaming': connection.supports_streaming
                    }
                    logger.info(f"Successfully connected to agent: {agent_name}")
                else:
                    logger.warning(f"Failed to connect to agent at {url}")
                    
            except Exception as e:
                logger.error(f"Error connecting to agent at {url}: {e}")
        
        if not self.agent_connections:
            logger.warning("No remote agents connected successfully")
        else:
            logger.info(f"Connected to {len(self.agent_connections)} agents: {list(self.agent_connections.keys())}")
    
    @property
    def streaming(self) -> bool:
        """Support streaming responses."""
        return True
    
    @property
    def supported_content_types(self) -> List[str]:
        """Supported content types."""
        return ["text/plain", "application/json"]
    
    async def process_task(
        self,
        task_id: str,
        message: Message,
        session_id: Optional[str] = None
    ) -> AsyncIterable[TaskStatusUpdateEvent | TaskArtifactUpdateEvent]:
        """
        Process a task by determining the best agent and delegating to it.
        
        Args:
            task_id: Unique task ID
            message: User message
            session_id: Optional session ID
            
        Yields:
            Task status and artifact events
        """
        try:
            # Ensure connections are initialized
            await self._ensure_connections()
            # Extract user message text
            user_text = self._extract_text_from_message(message)
            
            # Add to session if available
            if session_id:
                await self.add_user_message(session_id, user_text)
            
            # Yield initial status
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                status=TaskStatus(
                    state=TaskState.RUNNING,
                    message=Message(
                        role="assistant",
                        parts=[TextPart(text="Analyzing your request...")]
                    )
                )
            )
            
            # Get conversation history for context
            history = []
            if session_id:
                try:
                    ai_session = await self._get_ai_session_manager(session_id)
                    history = await ai_session.get_messages()
                except Exception as e:
                    logger.warning(f"Could not get session history: {e}")
            
            # Determine which agent to use
            selected_agent = await self._select_agent(user_text, history)
            
            if not selected_agent:
                yield TaskStatusUpdateEvent(
                    task_id=task_id,
                    status=TaskStatus(
                        state=TaskState.FAILED,
                        message=Message(
                            role="assistant",
                            parts=[TextPart(text="No suitable agent available to handle this request.")]
                        )
                    )
                )
                return
            
            # Notify user which agent is handling the request
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                status=TaskStatus(
                    state=TaskState.RUNNING,
                    message=Message(
                        role="assistant",
                        parts=[TextPart(text=f"Delegating to {selected_agent} agent...")]
                    )
                )
            )
            
            # Delegate to the selected agent
            async for event in self._delegate_to_agent(selected_agent, task_id, user_text, session_id):
                yield event
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                status=TaskStatus(
                    state=TaskState.FAILED,
                    message=Message(
                        role="assistant",
                        parts=[TextPart(text=f"Error: {str(e)}")]
                    )
                )
            )
    
    def _extract_text_from_message(self, message: Message) -> str:
        """Extract text content from a message."""
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'text'):
                text_parts.append(part.text)
        return ' '.join(text_parts)
    
    async def _select_agent(self, user_text: str, history: List[Dict]) -> Optional[str]:
        """
        Use LLM to select the best agent for the task.
        
        Args:
            user_text: The user's request
            history: Conversation history
            
        Returns:
            Name of the selected agent or None
        """
        await self._ensure_connections()
        
        if not self.agent_connections:
            return None
        
        # Build agent descriptions
        agent_list = []
        for name, info in self.agent_registry.items():
            agent_list.append(f"- {name}: {info['description']}")
        
        agents_description = "\n".join(agent_list)
        
        # Create prompt for agent selection
        system_prompt = f"""You are a supervisor agent that routes requests to specialized agents.

Available agents:
{agents_description}

Analyze the user's request and respond with ONLY the agent name that should handle it.
Do not include any explanation, just the agent name.

Guidelines:
- For IBM Cloud resource management, use ibmcloud_base_agent
- For account administration tasks, use ibmcloud_account_admin_agent  
- For serverless/functions tasks, use ibmcloud_serverless_agent
- For guidance and best practices, use ibmcloud_guide_agent
- For automation and scripting, use ibmcloud_cloud_automation_agent

If no agent is suitable, respond with 'none'."""
        
        try:
            # Use LLM to select agent
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
                    return agent_name
            
            if selected != 'none':
                logger.warning(f"LLM selected unknown agent: {selected}")
            
            # Default to base agent if available
            if 'ibmcloud_base_agent' in self.agent_connections:
                return 'ibmcloud_base_agent'
            
            # Return first available agent
            return list(self.agent_connections.keys())[0] if self.agent_connections else None
            
        except Exception as e:
            logger.error(f"Error selecting agent: {e}")
            # Default fallback
            return list(self.agent_connections.keys())[0] if self.agent_connections else None
    
    async def _delegate_to_agent(
        self,
        agent_name: str,
        task_id: str,
        user_text: str,
        session_id: Optional[str]
    ) -> AsyncIterable[TaskStatusUpdateEvent | TaskArtifactUpdateEvent]:
        """
        Delegate a task to a specific agent.
        
        Args:
            agent_name: Name of the agent to delegate to
            task_id: Task ID
            user_text: User's message text
            session_id: Optional session ID
            
        Yields:
            Events from the delegated agent
        """
        connection = self.agent_connections.get(agent_name)
        if not connection:
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                status=TaskStatus(
                    state=TaskState.FAILED,
                    message=Message(
                        role="assistant",
                        parts=[TextPart(text=f"Agent {agent_name} is not available")]
                    )
                )
            )
            return
        
        # Create task request
        request = TaskRequest(
            id=str(uuid.uuid4()),
            session_id=session_id,
            message=ClientMessage(
                role="user",
                content=user_text,
                metadata={"forwarded_by": "supervisor_agent"}
            )
        )
        
        try:
            if connection.supports_streaming:
                # Stream response from agent
                async for event in connection.send_task_streaming(request):
                    # Convert event to proper format
                    if 'result' in event:
                        result = event['result']
                        if 'status' in result:
                            status = result['status']
                            
                            # Convert message if present
                            message_obj = None
                            if 'message' in status and status['message']:
                                msg_content = status['message'].get('content', '')
                                if msg_content:
                                    message_obj = Message(
                                        role="assistant",
                                        parts=[TextPart(text=msg_content)]
                                    )
                            
                            yield TaskStatusUpdateEvent(
                                task_id=task_id,
                                status=TaskStatus(
                                    state=TaskState.RUNNING if not event.get('final') else TaskState.COMPLETED,
                                    message=message_obj
                                )
                            )
                    
                    if event.get('final'):
                        break
            else:
                # Non-streaming response
                response = await connection.send_task(request)
                
                if response.state == ClientTaskState.FAILED:
                    yield TaskStatusUpdateEvent(
                        task_id=task_id,
                        status=TaskStatus(
                            state=TaskState.FAILED,
                            message=Message(
                                role="assistant",
                                parts=[TextPart(text=response.error or "Task failed")]
                            )
                        )
                    )
                else:
                    message_obj = None
                    if response.message:
                        message_obj = Message(
                            role="assistant",
                            parts=[TextPart(text=response.message.content)]
                        )
                    
                    yield TaskStatusUpdateEvent(
                        task_id=task_id,
                        status=TaskStatus(
                            state=TaskState.COMPLETED,
                            message=message_obj
                        )
                    )
            
            # Add response to session
            if session_id and connection.card:
                final_response = f"[Handled by {agent_name}]"
                await self.add_ai_response(
                    session_id, 
                    final_response,
                    model=self.model,
                    provider="supervisor"
                )
                
        except Exception as e:
            logger.error(f"Error delegating to {agent_name}: {e}")
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                status=TaskStatus(
                    state=TaskState.FAILED,
                    message=Message(
                        role="assistant",
                        parts=[TextPart(text=f"Error delegating to {agent_name}: {str(e)}")]
                    )
                )
            )
    
    async def cleanup(self):
        """Clean up agent connections."""
        for connection in self.agent_connections.values():
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")


def create_supervisor_handler(**kwargs) -> SupervisorHandler:
    """
    Factory function to create a supervisor handler.
    
    Returns:
        Configured SupervisorHandler instance
    """
    return SupervisorHandler(
        name="supervisor_agent",
        infinite_context=True,
        token_threshold=4000,
        max_turns_per_segment=50,
        default_ttl_hours=24,
        **kwargs
    )