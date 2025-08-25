"""
Pytest configuration and fixtures for IBM Cloud agents tests.
"""
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_env_vars():
    """Fixture providing mock environment variables for testing."""
    return {
        "PROVIDER": "openai",
        "MODEL": "gpt-4o-mini",
        "OPENAI_API_KEY": "test-api-key",
        "IBMCLOUD_API_KEY": "test-ibm-api-key",
        "IBMCLOUD_REGION": "us-south",
        "IBMCLOUD_MONITORING_ENABLED": "false",
        "IBMCLOUD_LOGS_ENABLED": "false",
        "IBMCLOUD_COS_ENABLED": "false",
    }


@pytest.fixture
def clean_environment(mock_env_vars):
    """Fixture that provides a clean environment for each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clear environment and set test values
    os.environ.clear()
    os.environ.update(mock_env_vars)
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_requests():
    """Mock requests module for HTTP calls."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        mock_post.return_value.json.return_value = {"status": "success"}
        mock_post.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "success"}
        mock_get.return_value.status_code = 200
        yield {
            'post': mock_post,
            'get': mock_get
        }


@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp for async HTTP calls."""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        yield mock_session


@pytest.fixture
def mock_boto3():
    """Mock boto3 for AWS/COS operations."""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_s3.head_bucket.return_value = None
        mock_client.return_value = mock_s3
        yield mock_s3


@pytest.fixture
def sample_agent_card():
    """Sample agent card for testing."""
    return {
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "url": "http://localhost:8000",
        "version": "1.0.0",
        "provider": {
            "organization": "Test Org",
            "url": "http://test.com"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": False
        },
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "skills": [
            {
                "id": "test-skill",
                "name": "Test Skill", 
                "description": "A skill for testing",
                "inputModes": ["text"],
                "outputModes": ["text"]
            }
        ]
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": "test-task-123",
        "sessionId": "test-session-456",
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Hello, test message"
                }
            ]
        },
        "acceptedOutputModes": ["text"],
        "metadata": {"test": "data"}
    }


@pytest.fixture
def mock_chuk_llm():
    """Mock chuk_llm components."""
    with patch('chuk_llm.configuration.ProviderConfig') as mock_config:
        mock_config.return_value = MagicMock()
        yield mock_config


@pytest.fixture  
def mock_a2a_server():
    """Mock a2a_server components."""
    with patch('a2a_server.tasks.handlers.chuk.chuk_agent.ChukAgent') as mock_agent:
        mock_instance = MagicMock()
        mock_agent.return_value = mock_instance
        yield mock_instance