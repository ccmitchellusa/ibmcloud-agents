"""
Unit tests for src.ibmcloud_base_agent.agent module.
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from src.ibmcloud_base_agent.agent import IBMCloudBaseAgent


class TestIBMCloudBaseAgent:
    """Test IBMCloudBaseAgent class."""
    
    def test_init_default_values(self, clean_environment):
        """Test IBMCloudBaseAgent initialization with default values."""
        agent = IBMCloudBaseAgent()
        
        assert agent.provider == "openai"
        assert agent.model == "gpt-4o-mini"
        assert agent.provider_config is not None
    
    def test_init_custom_values(self, clean_environment):
        """Test IBMCloudBaseAgent initialization with custom values."""
        os.environ.update({
            "PROVIDER": "anthropic",
            "MODEL": "claude-3-sonnet"
        })
        
        agent = IBMCloudBaseAgent()
        
        assert agent.provider == "anthropic"
        assert agent.model == "claude-3-sonnet"
    
    @patch('src.ibmcloud_base_agent.agent.ProviderConfig')
    def test_create_provider_config(self, mock_provider_config, clean_environment):
        """Test _create_provider_config method."""
        os.environ.update({
            "MODEL": "gpt-4",
            "LITELLM_PROXY_URL": "https://proxy.test.com",
            "LITELLM_PROXY_API_KEY": "test-proxy-key"
        })
        
        agent = IBMCloudBaseAgent()
        
        # Verify ProviderConfig was called with correct runtime overlay
        mock_provider_config.assert_called_once()
        call_args = mock_provider_config.call_args[0][0]
        
        assert "litellm" in call_args
        assert call_args["litellm"]["default_model"] == "gpt-4"
        assert call_args["litellm"]["api_base"] == "https://proxy.test.com"
        assert call_args["litellm"]["api_key_env"] == "LITELLM_PROXY_API_KEY"
    
    def test_create_mcp_config_basic(self, clean_environment, temp_dir):
        """Test _create_mcp_config method with basic parameters."""
        agent = IBMCloudBaseAgent()
        
        config_file = temp_dir / "test_config.json"
        
        with patch('pathlib.Path.write_text') as mock_write_text:
            agent._create_mcp_config(
                config_file=str(config_file),
                mcp_tools="basic,advanced",
                server_name="test-server",
                allow_write=False
            )
        
        # Verify write_text was called
        mock_write_text.assert_called_once()
        
        # Get the written content (first argument to write_text)
        written_content = mock_write_text.call_args[0][0]
        
        # Parse the JSON to verify structure
        config_data = json.loads(written_content)
        
        assert "mcpServers" in config_data
        assert "test-server" in config_data["mcpServers"]
        
        server_config = config_data["mcpServers"]["test-server"]
        assert server_config["command"] == "ibmcloud"
        assert "--mcp-transport" in server_config["args"]
        assert "stdio" in server_config["args"]
        assert "--mcp-tools" in server_config["args"]
        assert "basic,advanced" in server_config["args"]
    
    def test_create_mcp_config_with_write_permission(self, clean_environment, temp_dir):
        """Test _create_mcp_config method with write permission enabled."""
        agent = IBMCloudBaseAgent()
        
        config_file = temp_dir / "test_config.json"
        
        with patch('pathlib.Path.write_text') as mock_write_text:
            agent._create_mcp_config(
                config_file=str(config_file),
                mcp_tools="file-operations",
                server_name="write-server",
                allow_write=True
            )
        
        # Get the written content
        written_content = mock_write_text.call_args[0][0]
        
        # Parse the JSON to verify --mcp-allow-write is included
        config_data = json.loads(written_content)
        server_config = config_data["mcpServers"]["write-server"]
        
        assert "--mcp-allow-write" in server_config["args"]
    
    @patch('pathlib.Path.write_text')
    def test_create_mcp_config_file_error(self, mock_write_text, clean_environment):
        """Test _create_mcp_config method with file writing error."""
        mock_write_text.side_effect = IOError("Permission denied")
        
        agent = IBMCloudBaseAgent()
        
        # Should not raise an exception, but may log error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                agent._create_mcp_config(
                    config_file="/invalid/path/config.json",
                    mcp_tools="basic",
                    server_name="test-server"
                )
    
    def test_provider_config_with_missing_env_vars(self, clean_environment):
        """Test provider config creation with missing environment variables."""
        # Don't set LITELLM_PROXY_URL
        os.environ.pop("LITELLM_PROXY_URL", None)
        
        agent = IBMCloudBaseAgent()
        
        # Should still create config without proxy URL
        assert agent.provider_config is not None
    
    @patch('src.ibmcloud_base_agent.agent.ProviderConfig')
    def test_provider_config_exception_handling(self, mock_provider_config, clean_environment):
        """Test provider config creation with exception."""
        mock_provider_config.side_effect = Exception("Config error")
        
        with pytest.raises(Exception, match="Config error"):
            IBMCloudBaseAgent()
    
    def test_mcp_config_json_structure(self, clean_environment, temp_dir):
        """Test that MCP config creates valid JSON structure."""
        agent = IBMCloudBaseAgent()
        config_file = temp_dir / "test_config.json"
        
        with patch('pathlib.Path.write_text') as mock_write_text:
            agent._create_mcp_config(
                config_file=str(config_file),
                mcp_tools="ibmcloud-basic,ibmcloud-advanced",
                server_name="ibmcloud-mcp-server",
                allow_write=True
            )
        
        written_content = mock_write_text.call_args[0][0]
        
        # Should be valid JSON
        config_data = json.loads(written_content)
        
        # Verify required structure
        assert isinstance(config_data, dict)
        assert "mcpServers" in config_data
        assert isinstance(config_data["mcpServers"], dict)
        assert "ibmcloud-mcp-server" in config_data["mcpServers"]
        
        server_config = config_data["mcpServers"]["ibmcloud-mcp-server"]
        assert "command" in server_config
        assert "args" in server_config
        assert isinstance(server_config["args"], list)
    
    def test_mcp_config_args_validation(self, clean_environment, temp_dir):
        """Test that MCP config generates correct arguments."""
        agent = IBMCloudBaseAgent()
        config_file = temp_dir / "test_config.json"
        
        with patch('pathlib.Path.write_text') as mock_write_text:
            agent._create_mcp_config(
                config_file=str(config_file),
                mcp_tools="custom-tools",
                server_name="custom-server",
                allow_write=False
            )
        
        written_content = mock_write_text.call_args[0][0]
        config_data = json.loads(written_content)
        args = config_data["mcpServers"]["custom-server"]["args"]
        
        # Check for required arguments
        assert "ibmcloud" == config_data["mcpServers"]["custom-server"]["command"]
        assert "--mcp-transport" in args
        assert "stdio" in args
        assert "--mcp-tools" in args
        assert "custom-tools" in args
        
        # Should not contain --mcp-allow-write when allow_write=False
        assert "--mcp-allow-write" not in args
    
    def test_multiple_mcp_config_calls(self, clean_environment, temp_dir):
        """Test calling _create_mcp_config multiple times."""
        agent = IBMCloudBaseAgent()
        
        config_file1 = temp_dir / "config1.json"
        config_file2 = temp_dir / "config2.json"
        
        with patch('pathlib.Path.write_text') as mock_write_text:
            # First call
            agent._create_mcp_config(
                config_file=str(config_file1),
                mcp_tools="tools1",
                server_name="server1"
            )
            
            # Second call  
            agent._create_mcp_config(
                config_file=str(config_file2),
                mcp_tools="tools2",
                server_name="server2"
            )
        
        # Should have been called twice
        assert mock_write_text.call_count == 2
    
    def test_environment_variable_integration(self, clean_environment):
        """Test that environment variables are properly integrated."""
        # Set up test environment
        test_env = {
            "PROVIDER": "litellm",
            "MODEL": "gpt-4-turbo",
            "LITELLM_PROXY_URL": "https://custom-proxy.test.com",
            "LITELLM_PROXY_API_KEY": "custom-api-key"
        }
        
        os.environ.update(test_env)
        
        agent = IBMCloudBaseAgent()
        
        assert agent.provider == "litellm"
        assert agent.model == "gpt-4-turbo"
        
        # The provider_config should have been created with these values
        assert agent.provider_config is not None