"""
Unit tests for src.common.simple_a2a_client module.
"""
import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

from src.common.simple_a2a_client import (
    TaskState,
    AgentCard,
    Message,
    TaskRequest,
    TaskResponse,
    RemoteAgentConnection,
    SimpleA2AClient,
)


class TestTaskState:
    """Test TaskState enum."""
    
    def test_task_state_values(self):
        """Test that TaskState has expected values."""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.RUNNING.value == "running"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.FAILED.value == "failed"
        assert TaskState.CANCELLED.value == "cancelled"
        assert TaskState.INPUT_REQUIRED.value == "input_required"


class TestAgentCard:
    """Test AgentCard dataclass."""
    
    def test_agent_card_creation(self):
        """Test creating an AgentCard."""
        card = AgentCard(
            name="Test Agent",
            description="A test agent",
            version="1.0.0"
        )
        assert card.name == "Test Agent"
        assert card.description == "A test agent"
        assert card.version == "1.0.0"
        assert card.capabilities == {"streaming": False}
    
    def test_agent_card_with_custom_capabilities(self):
        """Test AgentCard with custom capabilities."""
        capabilities = {"streaming": True, "custom": "value"}
        card = AgentCard(
            name="Test Agent",
            description="A test agent",
            capabilities=capabilities
        )
        assert card.capabilities == capabilities


class TestMessage:
    """Test Message dataclass."""
    
    def test_message_creation(self):
        """Test creating a Message."""
        message = Message(
            role="user",
            content="Hello, world!",
            metadata={"source": "test"}
        )
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.metadata == {"source": "test"}
    
    def test_message_without_metadata(self):
        """Test creating a Message without metadata."""
        message = Message(role="agent", content="Response")
        assert message.role == "agent"
        assert message.content == "Response"
        assert message.metadata is None


class TestTaskRequest:
    """Test TaskRequest dataclass."""
    
    def test_task_request_creation(self):
        """Test creating a TaskRequest."""
        message = Message(role="user", content="Test message")
        request = TaskRequest(
            task_id="test-123",
            agent_url="https://test.com",
            message=message
        )
        assert request.task_id == "test-123"
        assert request.agent_url == "https://test.com"
        assert request.message.content == "Test message"
        assert request.timeout == 30.0
        assert request.metadata is None


class TestRemoteAgentConnection:
    """Test RemoteAgentConnection class."""
    
    def test_remote_agent_connection_creation(self):
        """Test creating a RemoteAgentConnection."""
        connection = RemoteAgentConnection(
            agent_url="https://test.com"
        )
        assert connection.agent_url == "https://test.com"
        assert connection.client is not None
        assert connection._connected is False
    
    @pytest.mark.asyncio
    async def test_get_agent_card_success(self, mock_aiohttp):
        """Test successful agent card retrieval."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "name": "Test Agent",
            "description": "Test description",
            "version": "1.0.0"
        }
        
        # Configure the mock session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        connection = RemoteAgentConnection(
            agent_url="https://test.com",
            agent_name="Test Agent"
        )
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            card = await connection.get_agent_card()
            
        assert isinstance(card, AgentCard)
        assert card.name == "Test Agent"
        assert card.description == "Test description"
        assert card.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_get_agent_card_http_error(self, mock_aiohttp):
        """Test agent card retrieval with HTTP error."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text.return_value = "Not Found"
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        connection = RemoteAgentConnection(
            agent_url="https://test.com",
            agent_name="Test Agent"
        )
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            with pytest.raises(Exception):
                await connection.get_agent_card()
    
    @pytest.mark.asyncio
    async def test_get_agent_card_exception(self):
        """Test agent card retrieval with exception."""
        connection = RemoteAgentConnection(
            agent_url="https://test.com",
            agent_name="Test Agent"
        )
        
        with patch('aiohttp.ClientSession', side_effect=Exception("Network error")):
            with pytest.raises(Exception):
                await connection.get_agent_card()
    
    @pytest.mark.asyncio
    async def test_send_task_success(self, mock_aiohttp):
        """Test successful task sending."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "id": "task-123",
            "state": "pending",
            "result": None
        }
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        connection = RemoteAgentConnection(
            agent_url="https://test.com",
            agent_name="Test Agent"
        )
        
        message = Message(role="user", content="Test message")
        request = TaskRequest(
            task_id="test-123",
            agent_url="https://test.com",
            message=message
        )
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            response = await connection.send_task(request)
            
        assert response["id"] == "task-123"
        assert response["state"] == "pending"
    
    @pytest.mark.asyncio
    async def test_send_task_http_error(self, mock_aiohttp):
        """Test task sending with HTTP error."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        connection = RemoteAgentConnection(
            agent_url="https://test.com",
            agent_name="Test Agent"
        )
        
        message = Message(role="user", content="Test message")
        request = TaskRequest(
            task_id="test-123",
            agent_url="https://test.com",
            message=message
        )
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            with pytest.raises(Exception):
                await connection.send_task(request)


class TestSimpleA2AClient:
    """Test SimpleA2AClient class."""
    
    def test_simple_a2a_client_creation(self):
        """Test creating a SimpleA2AClient."""
        client = SimpleA2AClient(timeout=60.0)
        assert client.timeout == 60.0
        assert len(client.connections) == 0
    
    def test_add_agent(self):
        """Test adding an agent to the client."""
        client = SimpleA2AClient()
        client.add_agent("https://test.com", "Test Agent")
        
        assert len(client.connections) == 1
        assert "Test Agent" in client.connections
        
        connection = client.connections["Test Agent"]
        assert connection.agent_url == "https://test.com"
        assert connection.agent_name == "Test Agent"
    
    def test_add_duplicate_agent(self):
        """Test adding a duplicate agent (should replace)."""
        client = SimpleA2AClient()
        client.add_agent("https://test1.com", "Test Agent")
        client.add_agent("https://test2.com", "Test Agent")
        
        assert len(client.connections) == 1
        connection = client.connections["Test Agent"]
        assert connection.agent_url == "https://test2.com"
    
    def test_get_connection_exists(self):
        """Test getting an existing connection."""
        client = SimpleA2AClient()
        client.add_agent("https://test.com", "Test Agent")
        
        connection = client.get_connection("Test Agent")
        assert connection is not None
        assert connection.agent_name == "Test Agent"
    
    def test_get_connection_not_exists(self):
        """Test getting a non-existing connection."""
        client = SimpleA2AClient()
        connection = client.get_connection("NonExistent Agent")
        assert connection is None
    
    @pytest.mark.asyncio
    async def test_get_agent_card_success(self):
        """Test successful agent card retrieval through client."""
        client = SimpleA2AClient()
        client.add_agent("https://test.com", "Test Agent")
        
        # Mock the connection's get_agent_card method
        mock_card = AgentCard(name="Test Agent", description="Test", version="1.0.0")
        connection = client.connections["Test Agent"]
        connection.get_agent_card = AsyncMock(return_value=mock_card)
        
        card = await client.get_agent_card("Test Agent")
        assert card == mock_card
        connection.get_agent_card.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_agent_card_no_connection(self):
        """Test agent card retrieval with no connection."""
        client = SimpleA2AClient()
        
        with pytest.raises(Exception):
            await client.get_agent_card("NonExistent Agent")
    
    @pytest.mark.asyncio
    async def test_send_task_success(self):
        """Test successful task sending through client."""
        client = SimpleA2AClient()
        client.add_agent("https://test.com", "Test Agent")
        
        # Mock the connection's send_task method
        mock_response = {"id": "task-123", "state": "pending"}
        connection = client.connections["Test Agent"]
        connection.send_task = AsyncMock(return_value=mock_response)
        
        message = Message(role="user", content="Test message")
        request = TaskRequest(
            task_id="test-123",
            agent_url="https://test.com",
            message=message
        )
        
        response = await client.send_task("Test Agent", request)
        assert response == mock_response
        connection.send_task.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_send_task_no_connection(self):
        """Test task sending with no connection."""
        client = SimpleA2AClient()
        
        message = Message(role="user", content="Test message")
        request = TaskRequest(
            task_id="test-123",
            agent_url="https://test.com",
            message=message
        )
        
        with pytest.raises(Exception):
            await client.send_task("NonExistent Agent", request)
    
    def test_list_agents(self):
        """Test listing agents."""
        client = SimpleA2AClient()
        client.add_agent("https://test1.com", "Agent 1")
        client.add_agent("https://test2.com", "Agent 2")
        
        agents = client.list_agents()
        assert len(agents) == 2
        assert "Agent 1" in agents
        assert "Agent 2" in agents
    
    def test_remove_agent(self):
        """Test removing an agent."""
        client = SimpleA2AClient()
        client.add_agent("https://test.com", "Test Agent")
        
        assert len(client.connections) == 1
        
        removed = client.remove_agent("Test Agent")
        assert removed is True
        assert len(client.connections) == 0
    
    def test_remove_nonexistent_agent(self):
        """Test removing a non-existent agent."""
        client = SimpleA2AClient()
        
        removed = client.remove_agent("NonExistent Agent")
        assert removed is False


class TestDataclassHelpers:
    """Test dataclass helper functionality."""
    
    def test_asdict_message(self):
        """Test converting Message to dict."""
        message = Message(
            role="user",
            content="Test message",
            metadata={"key": "value"}
        )
        
        data = asdict(message)
        assert data["role"] == "user"
        assert data["content"] == "Test message"
        assert data["metadata"]["key"] == "value"
    
    def test_asdict_agent_card(self):
        """Test converting AgentCard to dict."""
        card = AgentCard(
            name="Test Agent",
            description="Test description",
            version="1.0.0",
            capabilities={"streaming": True}
        )
        
        data = asdict(card)
        assert data["name"] == "Test Agent"
        assert data["description"] == "Test description"
        assert data["capabilities"]["streaming"] is True