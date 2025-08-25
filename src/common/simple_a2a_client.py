"""
Simple A2A client for communicating with A2A agents.
This replaces the Google A2A client library with a lightweight implementation.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass, asdict
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """Task state enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INPUT_REQUIRED = "input_required"


@dataclass
class AgentCard:
    """Agent card containing agent metadata."""
    name: str
    description: str
    version: str = "1.0.0"
    capabilities: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = {"streaming": False}


@dataclass
class Message:
    """Message structure for A2A communication."""
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TaskRequest:
    """Task request structure."""
    id: str
    session_id: Optional[str]
    message: Message
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TaskResponse:
    """Task response structure."""
    id: str
    state: TaskState
    message: Optional[Message] = None
    error: Optional[str] = None
    artifacts: Optional[list] = None


class SimpleA2AClient:
    """Simple A2A client for agent communication."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the A2A client.
        
        Args:
            base_url: Base URL of the agent (e.g., http://localhost:8000/agent_name)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_agent_card(self) -> AgentCard:
        """
        Get the agent card from the well-known endpoint.
        
        Returns:
            AgentCard object containing agent metadata
        """
        url = f"{self.base_url}/.well-known/agent.json"
        
        try:
            session = await self._ensure_session()
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                return AgentCard(
                    name=data.get("name", "unknown"),
                    description=data.get("description", ""),
                    version=data.get("version", "1.0.0"),
                    capabilities=data.get("capabilities", {"streaming": False})
                )
        except aiohttp.ClientError as e:
            logger.error(f"Failed to get agent card from {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting agent card: {e}")
            raise
    
    async def send_task(self, task_request: TaskRequest) -> TaskResponse:
        """
        Send a task to the agent (non-streaming).
        
        Args:
            task_request: The task request to send
            
        Returns:
            TaskResponse with the result
        """
        url = f"{self.base_url}/task"
        
        try:
            session = await self._ensure_session()
            
            # Convert the request to dict
            request_data = {
                "id": task_request.id,
                "sessionId": task_request.session_id,
                "message": {
                    "role": task_request.message.role,
                    "parts": [{"text": task_request.message.content}]
                },
                "metadata": task_request.metadata or {}
            }
            
            async with session.post(url, json=request_data) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Parse the response
                result = data.get("result", {})
                status = result.get("status", {})
                
                # Extract message if present
                response_message = None
                if status.get("message"):
                    msg = status["message"]
                    # Extract text from parts
                    content = ""
                    for part in msg.get("parts", []):
                        if "text" in part:
                            content += part["text"]
                    
                    if content:
                        response_message = Message(
                            role=msg.get("role", "assistant"),
                            content=content,
                            metadata=msg.get("metadata")
                        )
                
                return TaskResponse(
                    id=result.get("id", task_request.id),
                    state=TaskState(status.get("state", "completed")),
                    message=response_message,
                    error=status.get("error"),
                    artifacts=result.get("artifacts", [])
                )
                
        except aiohttp.ClientError as e:
            logger.error(f"Failed to send task to {url}: {e}")
            return TaskResponse(
                id=task_request.id,
                state=TaskState.FAILED,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error sending task: {e}")
            return TaskResponse(
                id=task_request.id,
                state=TaskState.FAILED,
                error=str(e)
            )
    
    async def send_task_streaming(self, task_request: TaskRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a task to the agent with streaming response.
        
        Args:
            task_request: The task request to send
            
        Yields:
            Streaming response events
        """
        url = f"{self.base_url}/task/stream"
        
        try:
            session = await self._ensure_session()
            
            # Convert the request to dict
            request_data = {
                "id": task_request.id,
                "sessionId": task_request.session_id,
                "message": {
                    "role": task_request.message.role,
                    "parts": [{"text": task_request.message.content}]
                },
                "metadata": task_request.metadata or {}
            }
            
            async with session.post(url, json=request_data) as response:
                response.raise_for_status()
                
                # Process streaming response
                async for line in response.content:
                    if line:
                        try:
                            # Handle SSE format
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                json_str = line_str[6:]
                                if json_str != '[DONE]':
                                    event = json.loads(json_str)
                                    yield event
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming response: {line}")
                        except Exception as e:
                            logger.error(f"Error processing stream: {e}")
                            
        except aiohttp.ClientError as e:
            logger.error(f"Failed to send streaming task to {url}: {e}")
            yield {
                "error": str(e),
                "state": "failed"
            }
        except Exception as e:
            logger.error(f"Unexpected error in streaming task: {e}")
            yield {
                "error": str(e),
                "state": "failed"
            }


class RemoteAgentConnection:
    """Connection to a remote A2A agent."""
    
    def __init__(self, agent_url: str):
        """
        Initialize connection to a remote agent.
        
        Args:
            agent_url: Full URL to the agent
        """
        self.agent_url = agent_url
        self.client = SimpleA2AClient(agent_url)
        self.card: Optional[AgentCard] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """
        Connect to the remote agent and retrieve its card.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.card = await self.client.get_agent_card()
            self._connected = True
            logger.info(f"Connected to agent '{self.card.name}' at {self.agent_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to agent at {self.agent_url}: {e}")
            self._connected = False
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to the agent."""
        return self._connected
    
    @property
    def supports_streaming(self) -> bool:
        """Check if the agent supports streaming."""
        return self.card and self.card.capabilities.get("streaming", False)
    
    async def send_task(self, task_request: TaskRequest) -> TaskResponse:
        """Send a task to the remote agent."""
        if not self._connected:
            return TaskResponse(
                id=task_request.id,
                state=TaskState.FAILED,
                error="Not connected to agent"
            )
        
        return await self.client.send_task(task_request)
    
    async def send_task_streaming(self, task_request: TaskRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """Send a task with streaming response."""
        if not self._connected:
            yield {
                "error": "Not connected to agent",
                "state": "failed"
            }
            return
        
        if not self.supports_streaming:
            # Fall back to non-streaming
            response = await self.send_task(task_request)
            yield {
                "result": asdict(response),
                "final": True
            }
        else:
            async for event in self.client.send_task_streaming(task_request):
                yield event
    
    async def close(self):
        """Close the connection."""
        await self.client.close()
        self._connected = False