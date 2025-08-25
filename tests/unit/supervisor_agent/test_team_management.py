"""
Unit tests for supervisor agent team management functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.supervisor_agent.supervisor_handler import SupervisorHandler
from src.common.simple_a2a_client import AgentCard


class TestTeamManagement:
    """Test team member management functionality."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a supervisor handler for testing."""
        return SupervisorHandler(
            agent_urls=["http://localhost:8000/test_agent"]
        )
    
    @pytest.fixture
    def mock_agent_card(self):
        """Mock agent card for testing."""
        return AgentCard(
            name="Test Agent",
            description="A test agent for unit testing",
            version="1.0.0",
            capabilities={"streaming": True}
        )
    
    @pytest.mark.asyncio
    async def test_add_team_member_success(self, supervisor, mock_agent_card):
        """Test successful team member addition."""
        # Mock RemoteAgentConnection
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = True
            mock_connection.card = mock_agent_card
            mock_connection.supports_streaming = True
            mock_connection_class.return_value = mock_connection
            
            result = await supervisor.add_team_member(
                agent_url="http://localhost:9000/new_agent",
                agent_name="Custom Agent"
            )
            
            assert result['success'] is True
            assert result['agent_name'] == "Custom Agent"
            assert result['description'] == "A test agent for unit testing"
            assert result['streaming'] is True
            
            # Verify agent was added to connections
            assert "Custom Agent" in supervisor.agent_connections
            assert "Custom Agent" in supervisor.agent_registry
            assert "Custom Agent" in supervisor._dynamic_agents
    
    @pytest.mark.asyncio
    async def test_add_team_member_duplicate_url(self, supervisor):
        """Test adding team member with duplicate URL."""
        # Add initial agent to registry
        supervisor.agent_registry["Existing Agent"] = {
            'name': 'Existing Agent',
            'url': 'http://localhost:9000/agent',
            'description': 'Existing agent'
        }
        
        result = await supervisor.add_team_member(
            agent_url="http://localhost:9000/agent"
        )
        
        assert result['success'] is False
        assert "already connected" in result['error']
        assert result['agent_name'] == "Existing Agent"
    
    @pytest.mark.asyncio
    async def test_add_team_member_connection_failed(self, supervisor):
        """Test adding team member when connection fails."""
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = False
            mock_connection_class.return_value = mock_connection
            
            result = await supervisor.add_team_member(
                agent_url="http://localhost:9000/broken_agent"
            )
            
            assert result['success'] is False
            assert "Failed to connect" in result['error']
    
    @pytest.mark.asyncio
    async def test_add_team_member_name_conflict_resolution(self, supervisor, mock_agent_card):
        """Test name conflict resolution when adding team members."""
        # Add initial agent
        supervisor.agent_connections["Test Agent"] = MagicMock()
        supervisor.agent_registry["Test Agent"] = {'name': 'Test Agent'}
        
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = True
            mock_connection.card = mock_agent_card
            mock_connection.supports_streaming = False
            mock_connection_class.return_value = mock_connection
            
            result = await supervisor.add_team_member(
                agent_url="http://localhost:9000/another_test_agent"
            )
            
            assert result['success'] is True
            # Should resolve name conflict by appending _1
            assert result['agent_name'] == "Test Agent_1"
            assert "Test Agent_1" in supervisor.agent_connections
    
    @pytest.mark.asyncio
    async def test_remove_team_member_success(self, supervisor):
        """Test successful team member removal."""
        # Add a dynamic agent
        mock_connection = AsyncMock()
        supervisor.agent_connections["Dynamic Agent"] = mock_connection
        supervisor.agent_registry["Dynamic Agent"] = {
            'name': 'Dynamic Agent',
            'description': 'A dynamic test agent'
        }
        supervisor._dynamic_agents.add("Dynamic Agent")
        
        result = await supervisor.remove_team_member("Dynamic Agent")
        
        assert result['success'] is True
        assert result['agent_name'] == "Dynamic Agent"
        assert "Dynamic Agent" not in supervisor.agent_connections
        assert "Dynamic Agent" not in supervisor.agent_registry
        assert "Dynamic Agent" not in supervisor._dynamic_agents
        
        # Verify connection was closed
        mock_connection.client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_remove_team_member_not_found(self, supervisor):
        """Test removing non-existent team member."""
        result = await supervisor.remove_team_member("NonExistent Agent")
        
        assert result['success'] is False
        assert "not found" in result['error']
    
    @pytest.mark.asyncio
    async def test_remove_configured_agent_blocked(self, supervisor):
        """Test that configured agents cannot be removed."""
        # Add a configured agent (not in _dynamic_agents)
        supervisor.agent_connections["Configured Agent"] = MagicMock()
        supervisor.agent_registry["Configured Agent"] = {
            'name': 'Configured Agent'
        }
        # Note: not adding to _dynamic_agents
        
        result = await supervisor.remove_team_member("Configured Agent")
        
        assert result['success'] is False
        assert "configured agent" in result['error']
        assert "cannot be removed dynamically" in result['error']
    
    @pytest.mark.asyncio
    async def test_list_team_members(self, supervisor):
        """Test listing team members."""
        # Add configured agent
        supervisor.agent_connections["Base Agent"] = MagicMock()
        supervisor.agent_registry["Base Agent"] = {
            'name': 'Base Agent',
            'description': 'Base configured agent',
            'url': 'http://localhost:8000/base_agent',
            'streaming': True
        }
        
        # Add dynamic agent
        supervisor.agent_connections["Dynamic Agent"] = MagicMock()
        supervisor.agent_registry["Dynamic Agent"] = {
            'name': 'Dynamic Agent',
            'description': 'Dynamic test agent',
            'url': 'http://localhost:9000/dynamic_agent',
            'streaming': False,
            'added_at': '2024-01-01T12:00:00'
        }
        supervisor._dynamic_agents.add("Dynamic Agent")
        
        result = await supervisor.list_team_members()
        
        assert result['total_agents'] == 2
        assert result['configured_agents'] == 1
        assert result['dynamic_agents'] == 1
        assert result['connected_agents'] == 2
        
        team_members = result['team_members']
        assert len(team_members) == 2
        
        # Find the configured agent
        configured = next(m for m in team_members if m['name'] == 'Base Agent')
        assert configured['type'] == 'configured'
        assert configured['status'] == 'connected'
        assert 'added_at' not in configured
        
        # Find the dynamic agent
        dynamic = next(m for m in team_members if m['name'] == 'Dynamic Agent')
        assert dynamic['type'] == 'dynamic'
        assert dynamic['status'] == 'connected'
        assert dynamic['added_at'] == '2024-01-01T12:00:00'
    
    @pytest.mark.asyncio
    async def test_reconnect_team_member_success(self, supervisor, mock_agent_card):
        """Test successful team member reconnection."""
        # Add agent to registry
        supervisor.agent_registry["Test Agent"] = {
            'name': 'Test Agent',
            'url': 'http://localhost:9000/test_agent',
            'description': 'Old description'
        }
        
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = True
            mock_connection.card = mock_agent_card
            mock_connection.supports_streaming = True
            mock_connection_class.return_value = mock_connection
            
            result = await supervisor.reconnect_team_member("Test Agent")
            
            assert result['success'] is True
            assert result['agent_name'] == "Test Agent"
            
            # Verify connection was updated
            assert supervisor.agent_connections["Test Agent"] == mock_connection
            assert supervisor.agent_registry["Test Agent"]["description"] == "A test agent for unit testing"
            assert supervisor.agent_registry["Test Agent"]["streaming"] is True
            assert "reconnected_at" in supervisor.agent_registry["Test Agent"]
    
    @pytest.mark.asyncio
    async def test_reconnect_team_member_not_found(self, supervisor):
        """Test reconnecting to non-existent team member."""
        result = await supervisor.reconnect_team_member("NonExistent Agent")
        
        assert result['success'] is False
        assert "not found in registry" in result['error']
    
    @pytest.mark.asyncio
    async def test_reconnect_team_member_failed(self, supervisor):
        """Test failed team member reconnection."""
        supervisor.agent_registry["Test Agent"] = {
            'name': 'Test Agent',
            'url': 'http://localhost:9000/broken_agent'
        }
        
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = False
            mock_connection_class.return_value = mock_connection
            
            result = await supervisor.reconnect_team_member("Test Agent")
            
            assert result['success'] is False
            assert "Failed to reconnect" in result['error']
    
    @pytest.mark.asyncio
    async def test_get_team_member_info_success(self, supervisor):
        """Test getting team member info."""
        # Add agent
        mock_connection = AsyncMock()
        mock_connection.card = AgentCard(
            name="Test Agent",
            description="Test description",
            version="2.0.0",
            capabilities={"streaming": True, "custom": True}
        )
        
        supervisor.agent_connections["Test Agent"] = mock_connection
        supervisor.agent_registry["Test Agent"] = {
            'name': 'Test Agent',
            'description': 'Test description',
            'url': 'http://localhost:9000/test_agent',
            'streaming': True
        }
        supervisor._dynamic_agents.add("Test Agent")
        
        result = await supervisor.get_team_member_info("Test Agent")
        
        assert result['success'] is True
        assert result['name'] == "Test Agent"
        assert result['type'] == 'dynamic'
        assert result['status'] == 'connected'
        assert 'agent_card' in result
        assert result['agent_card']['name'] == "Test Agent"
        assert result['agent_card']['version'] == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_get_team_member_info_not_found(self, supervisor):
        """Test getting info for non-existent team member."""
        result = await supervisor.get_team_member_info("NonExistent Agent")
        
        assert result['success'] is False
        assert "not found" in result['error']
    
    @pytest.mark.asyncio
    async def test_cleanup_closes_connections(self, supervisor):
        """Test that cleanup properly closes all connections."""
        # Add mock connections
        mock_conn1 = AsyncMock()
        mock_conn2 = AsyncMock()
        
        supervisor.agent_connections = {
            "Agent 1": mock_conn1,
            "Agent 2": mock_conn2
        }
        
        await supervisor.cleanup()
        
        mock_conn1.client.close.assert_called_once()
        mock_conn2.client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_team_member_url_normalization(self, supervisor, mock_agent_card):
        """Test that URLs are properly normalized when adding team members."""
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = True
            mock_connection.card = mock_agent_card
            mock_connection.supports_streaming = True
            mock_connection_class.return_value = mock_connection
            
            # Test URL without http prefix
            result = await supervisor.add_team_member(
                agent_url="localhost:9000/agent"
            )
            
            assert result['success'] is True
            # Should have normalized the URL
            mock_connection_class.assert_called_with("http://localhost:9000/agent")
            
            # Verify URL is stored correctly
            agent_info = supervisor.agent_registry["Test Agent"]
            assert agent_info['url'] == "http://localhost:9000/agent"


class TestTeamManagementEdgeCases:
    """Test edge cases for team management."""
    
    @pytest.mark.asyncio
    async def test_add_team_member_exception_handling(self):
        """Test exception handling during team member addition."""
        supervisor = SupervisorHandler(agent_urls=[])
        
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection', side_effect=Exception("Connection error")):
            result = await supervisor.add_team_member("http://localhost:9000/agent")
            
            assert result['success'] is False
            assert "Connection error" in result['error']
    
    @pytest.mark.asyncio
    async def test_remove_team_member_exception_handling(self):
        """Test exception handling during team member removal."""
        supervisor = SupervisorHandler(agent_urls=[])
        
        # Add agent with mock connection that throws exception
        mock_connection = AsyncMock()
        mock_connection.client.close.side_effect = Exception("Close error")
        
        supervisor.agent_connections["Test Agent"] = mock_connection
        supervisor.agent_registry["Test Agent"] = {'name': 'Test Agent'}
        supervisor._dynamic_agents.add("Test Agent")
        
        # Should handle exception gracefully and still remove agent
        result = await supervisor.remove_team_member("Test Agent")
        
        assert result['success'] is True
        assert "Test Agent" not in supervisor.agent_connections
    
    @pytest.mark.asyncio
    async def test_dynamic_agents_tracking(self):
        """Test that dynamic agents are properly tracked separately from configured ones."""
        supervisor = SupervisorHandler(
            agent_urls=["http://localhost:8000/configured_agent"]
        )
        
        # Simulate configured agent initialization
        supervisor.agent_connections["Configured Agent"] = MagicMock()
        supervisor.agent_registry["Configured Agent"] = {
            'name': 'Configured Agent',
            'url': 'http://localhost:8000/configured_agent'
        }
        # Note: configured agents are NOT in _dynamic_agents
        
        # Add dynamic agent
        with patch('src.supervisor_agent.supervisor_handler.RemoteAgentConnection') as mock_conn_class:
            mock_connection = AsyncMock()
            mock_connection.connect.return_value = True
            mock_connection.card = AgentCard(name="Dynamic Agent", description="Test", version="1.0.0")
            mock_connection.supports_streaming = False
            mock_conn_class.return_value = mock_connection
            
            await supervisor.add_team_member("http://localhost:9000/dynamic_agent")
        
        # Verify tracking
        assert "Configured Agent" not in supervisor._dynamic_agents
        assert "Dynamic Agent" in supervisor._dynamic_agents
        
        # Should be able to remove dynamic agent but not configured one
        result1 = await supervisor.remove_team_member("Dynamic Agent")
        assert result1['success'] is True
        
        result2 = await supervisor.remove_team_member("Configured Agent")
        assert result2['success'] is False
        assert "configured agent" in result2['error']