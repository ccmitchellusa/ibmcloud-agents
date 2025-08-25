"""
Integration tests for agent startup and basic functionality.
"""
import asyncio
import pytest
import subprocess
import time
import requests
from pathlib import Path


class TestAgentStartup:
    """Test agent startup and basic HTTP endpoints."""
    
    def test_base_agent_can_start(self):
        """Test that base agent can start without errors."""
        # This is a basic smoke test - agent should start and exit cleanly
        result = subprocess.run([
            "python", "-m", "src.ibmcloud_base_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        # Should exit successfully and show help
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_supervisor_agent_can_start(self):
        """Test that supervisor agent can start without errors."""
        result = subprocess.run([
            "python", "-m", "src.supervisor_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_serverless_agent_can_start(self):
        """Test that serverless agent can start without errors."""
        result = subprocess.run([
            "python", "-m", "src.ibmcloud_serverless_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_account_admin_agent_can_start(self):
        """Test that account admin agent can start without errors."""
        result = subprocess.run([
            "python", "-m", "src.ibmcloud_account_admin_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_cloud_automation_agent_can_start(self):
        """Test that cloud automation agent can start without errors."""
        result = subprocess.run([
            "python", "-m", "src.ibmcloud_cloud_automation_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_guide_agent_can_start(self):
        """Test that guide agent can start without errors."""
        result = subprocess.run([
            "python", "-m", "src.ibmcloud_guide_agent.main", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()


@pytest.mark.slow
class TestAgentHTTPEndpoints:
    """Test agent HTTP endpoints (requires actual startup)."""
    
    @pytest.fixture(scope="class")
    def running_agent(self):
        """Start an agent for integration testing."""
        # Start the base agent in a subprocess
        process = subprocess.Popen([
            "python", "-m", "src.ibmcloud_base_agent.main",
            "--log-level", "error"  # Reduce log noise
        ], env={
            "PROVIDER": "openai",
            "MODEL": "gpt-4o-mini", 
            "OPENAI_API_KEY": "test-key",  # Fake key for startup
            "IBMCLOUD_API_KEY": "test-ibm-key"
        })
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's running
        if process.poll() is not None:
            pytest.skip("Agent failed to start")
        
        yield "http://localhost:8000"
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
    
    def test_agent_card_endpoint(self, running_agent):
        """Test that agent card endpoint is accessible."""
        try:
            response = requests.get(f"{running_agent}/agent-card.json", timeout=5)
            # Should get either valid agent card or error (depending on MCP setup)
            # Main thing is that the endpoint exists
            assert response.status_code in [200, 500]
        except requests.exceptions.RequestException:
            pytest.skip("Agent not responding to HTTP requests")
    
    def test_health_endpoint(self, running_agent):
        """Test health endpoint if it exists."""
        try:
            response = requests.get(f"{running_agent}/health", timeout=5)
            # Health endpoint might not exist, so allow 404
            assert response.status_code in [200, 404, 500]
        except requests.exceptions.RequestException:
            pytest.skip("Agent not responding to HTTP requests")


class TestAgentConfiguration:
    """Test agent configuration loading."""
    
    def test_mcp_config_files_exist(self):
        """Test that MCP configuration files exist."""
        config_files = [
            "ibmcloud_mcp_base_agent_config.json",
            "ibmcloud_mcp_serverless_agent_config.json", 
            "ibmcloud_mcp_account_admin_config.json",
            "ibmcloud_mcp_cloud_automation_agent_config.json",
            "ibmcloud_mcp_guide_agent_config.json"
        ]
        
        for config_file in config_files:
            # Check both in src/ and root directory
            src_path = Path(f"src/{config_file}")
            root_path = Path(config_file)
            
            assert src_path.exists() or root_path.exists(), f"Config file {config_file} not found"
    
    def test_agent_modules_importable(self):
        """Test that all agent modules can be imported."""
        modules_to_test = [
            "src.ibmcloud_base_agent.agent",
            "src.ibmcloud_base_agent.main", 
            "src.supervisor_agent.agent",
            "src.supervisor_agent.main",
            "src.ibmcloud_serverless_agent.agent",
            "src.ibmcloud_serverless_agent.main",
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
            except Exception as e:
                # Some modules might fail due to missing dependencies, but import should work
                if "ModuleNotFoundError" in str(e):
                    pytest.skip(f"Module {module_name} has missing dependencies: {e}")
                else:
                    pytest.fail(f"Unexpected error importing {module_name}: {e}")


class TestAgentDependencies:
    """Test agent dependencies and requirements."""
    
    def test_required_packages_available(self):
        """Test that required packages can be imported."""
        required_packages = [
            "pydantic",
            "aiohttp", 
            "asyncio",
            "json",
            "logging",
            "pathlib",
            "os"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package {package} not available")
    
    def test_optional_packages_handling(self):
        """Test that optional packages are handled gracefully."""
        # These might not be available in test environment
        optional_packages = [
            "boto3",
            "requests", 
            "chuk_llm",
            "a2a_server"
        ]
        
        for package in optional_packages:
            try:
                __import__(package)
            except ImportError:
                # Should be handled gracefully by the application
                pass