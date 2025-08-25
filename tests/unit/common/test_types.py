"""
Unit tests for src.common.types module.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from uuid import UUID

from src.common.types import (
    TaskState,
    TextPart,
    FilePart,
    DataPart,
    FileContent,
    Message,
    TaskStatus,
    Artifact,
    Task,
    TaskSendParams,
    JSONRPCRequest,
    JSONRPCResponse,
    SendTaskRequest,
    GetTaskRequest,
    A2AClientError,
    A2AClientHTTPError,
    A2AClientJSONError,
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)


class TestTaskState:
    """Test TaskState enum."""
    
    def test_task_state_values(self):
        """Test that TaskState has expected values."""
        assert TaskState.SUBMITTED == 'submitted'
        assert TaskState.WORKING == 'working'
        assert TaskState.INPUT_REQUIRED == 'input-required'
        assert TaskState.COMPLETED == 'completed'
        assert TaskState.CANCELED == 'canceled'
        assert TaskState.FAILED == 'failed'
        assert TaskState.UNKNOWN == 'unknown'


class TestTextPart:
    """Test TextPart model."""
    
    def test_text_part_creation(self):
        """Test creating a TextPart."""
        part = TextPart(text="Hello world")
        assert part.type == "text"
        assert part.text == "Hello world"
        assert part.metadata is None
    
    def test_text_part_with_metadata(self):
        """Test TextPart with metadata."""
        metadata = {"source": "test"}
        part = TextPart(text="Hello", metadata=metadata)
        assert part.metadata == metadata


class TestFileContent:
    """Test FileContent model."""
    
    def test_file_content_with_bytes(self):
        """Test FileContent with bytes."""
        content = FileContent(name="test.txt", bytes="SGVsbG8gd29ybGQ=")
        assert content.name == "test.txt"
        assert content.bytes == "SGVsbG8gd29ybGQ="
        assert content.uri is None
    
    def test_file_content_with_uri(self):
        """Test FileContent with URI."""
        content = FileContent(name="test.txt", uri="https://example.com/file.txt")
        assert content.uri == "https://example.com/file.txt"
        assert content.bytes is None
    
    def test_file_content_validation_missing_both(self):
        """Test FileContent validation fails when both bytes and uri are missing."""
        with pytest.raises(ValidationError, match="Either 'bytes' or 'uri' must be present"):
            FileContent(name="test.txt")
    
    def test_file_content_validation_both_present(self):
        """Test FileContent validation fails when both bytes and uri are present."""
        with pytest.raises(ValidationError, match="Only one of 'bytes' or 'uri' can be present"):
            FileContent(name="test.txt", bytes="data", uri="https://example.com/file.txt")


class TestFilePart:
    """Test FilePart model."""
    
    def test_file_part_creation(self):
        """Test creating a FilePart."""
        file_content = FileContent(name="test.txt", bytes="data")
        part = FilePart(file=file_content)
        assert part.type == "file"
        assert part.file.name == "test.txt"


class TestDataPart:
    """Test DataPart model."""
    
    def test_data_part_creation(self):
        """Test creating a DataPart."""
        data = {"key": "value", "number": 42}
        part = DataPart(data=data)
        assert part.type == "data"
        assert part.data == data


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test creating a Message."""
        parts = [TextPart(text="Hello")]
        message = Message(role="user", parts=parts)
        assert message.role == "user"
        assert len(message.parts) == 1
        assert message.parts[0].text == "Hello"
    
    def test_message_with_multiple_parts(self):
        """Test Message with multiple parts."""
        parts = [
            TextPart(text="Hello"),
            DataPart(data={"key": "value"})
        ]
        message = Message(role="agent", parts=parts)
        assert len(message.parts) == 2
        assert message.parts[0].type == "text"
        assert message.parts[1].type == "data"


class TestTaskStatus:
    """Test TaskStatus model."""
    
    def test_task_status_creation(self):
        """Test creating a TaskStatus."""
        status = TaskStatus(state=TaskState.SUBMITTED)
        assert status.state == TaskState.SUBMITTED
        assert status.message is None
        assert isinstance(status.timestamp, datetime)
    
    def test_task_status_with_message(self):
        """Test TaskStatus with message."""
        parts = [TextPart(text="Status update")]
        message = Message(role="agent", parts=parts)
        status = TaskStatus(state=TaskState.WORKING, message=message)
        assert status.message.parts[0].text == "Status update"
    
    def test_timestamp_serialization(self):
        """Test timestamp serialization."""
        status = TaskStatus(state=TaskState.COMPLETED)
        data = status.model_dump()
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)


class TestArtifact:
    """Test Artifact model."""
    
    def test_artifact_creation(self):
        """Test creating an Artifact."""
        parts = [TextPart(text="Artifact content")]
        artifact = Artifact(name="test-artifact", parts=parts)
        assert artifact.name == "test-artifact"
        assert len(artifact.parts) == 1
        assert artifact.index == 0


class TestTask:
    """Test Task model."""
    
    def test_task_creation(self):
        """Test creating a Task."""
        status = TaskStatus(state=TaskState.SUBMITTED)
        task = Task(id="task-123", status=status)
        assert task.id == "task-123"
        assert task.status.state == TaskState.SUBMITTED
        assert task.artifacts is None
        assert task.history is None


class TestTaskSendParams:
    """Test TaskSendParams model."""
    
    def test_task_send_params_creation(self):
        """Test creating TaskSendParams."""
        parts = [TextPart(text="Hello")]
        message = Message(role="user", parts=parts)
        params = TaskSendParams(id="task-123", message=message)
        assert params.id == "task-123"
        assert params.message.parts[0].text == "Hello"
        assert params.sessionId is not None  # Auto-generated UUID
    
    def test_task_send_params_with_session_id(self):
        """Test TaskSendParams with explicit session ID."""
        parts = [TextPart(text="Hello")]
        message = Message(role="user", parts=parts)
        params = TaskSendParams(
            id="task-123", 
            sessionId="session-456", 
            message=message
        )
        assert params.sessionId == "session-456"


class TestJSONRPCRequest:
    """Test JSONRPCRequest model."""
    
    def test_jsonrpc_request_creation(self):
        """Test creating a JSONRPCRequest."""
        request = JSONRPCRequest(method="test/method", params={"key": "value"})
        assert request.jsonrpc == "2.0"
        assert request.method == "test/method"
        assert request.params == {"key": "value"}
        assert request.id is not None  # Auto-generated


class TestJSONRPCResponse:
    """Test JSONRPCResponse model."""
    
    def test_jsonrpc_response_success(self):
        """Test creating a successful JSONRPCResponse."""
        response = JSONRPCResponse(id="123", result={"status": "success"})
        assert response.id == "123"
        assert response.result == {"status": "success"}
        assert response.error is None
    
    def test_jsonrpc_response_error(self):
        """Test creating an error JSONRPCResponse."""
        from src.common.types import InternalError
        error = InternalError(message="Something went wrong")
        response = JSONRPCResponse(id="123", error=error)
        assert response.error.message == "Something went wrong"
        assert response.result is None


class TestSendTaskRequest:
    """Test SendTaskRequest model."""
    
    def test_send_task_request_creation(self):
        """Test creating a SendTaskRequest."""
        parts = [TextPart(text="Hello")]
        message = Message(role="user", parts=parts)
        params = TaskSendParams(id="task-123", message=message)
        request = SendTaskRequest(params=params)
        
        assert request.method == "tasks/send"
        assert request.params.id == "task-123"
        assert request.params.message.parts[0].text == "Hello"


class TestGetTaskRequest:
    """Test GetTaskRequest model."""
    
    def test_get_task_request_creation(self):
        """Test creating a GetTaskRequest."""
        from src.common.types import TaskQueryParams
        params = TaskQueryParams(id="task-123")
        request = GetTaskRequest(params=params)
        
        assert request.method == "tasks/get"
        assert request.params.id == "task-123"


class TestAgentSkill:
    """Test AgentSkill model."""
    
    def test_agent_skill_creation(self):
        """Test creating an AgentSkill."""
        skill = AgentSkill(
            id="test-skill",
            name="Test Skill",
            description="A test skill"
        )
        assert skill.id == "test-skill"
        assert skill.name == "Test Skill"
        assert skill.description == "A test skill"


class TestAgentCapabilities:
    """Test AgentCapabilities model."""
    
    def test_agent_capabilities_defaults(self):
        """Test AgentCapabilities default values."""
        caps = AgentCapabilities()
        assert caps.streaming is False
        assert caps.pushNotifications is False
        assert caps.stateTransitionHistory is False
    
    def test_agent_capabilities_custom(self):
        """Test AgentCapabilities with custom values."""
        caps = AgentCapabilities(
            streaming=True,
            pushNotifications=True
        )
        assert caps.streaming is True
        assert caps.pushNotifications is True
        assert caps.stateTransitionHistory is False


class TestAgentCard:
    """Test AgentCard model."""
    
    def test_agent_card_creation(self, sample_agent_card):
        """Test creating an AgentCard."""
        from src.common.types import AgentProvider
        
        card = AgentCard(
            name=sample_agent_card["name"],
            description=sample_agent_card["description"],
            url=sample_agent_card["url"],
            version=sample_agent_card["version"],
            capabilities=AgentCapabilities(**sample_agent_card["capabilities"]),
            skills=[AgentSkill(**skill) for skill in sample_agent_card["skills"]]
        )
        
        assert card.name == "Test Agent"
        assert card.url == "http://localhost:8000"
        assert card.version == "1.0.0"
        assert len(card.skills) == 1
        assert card.skills[0].name == "Test Skill"


class TestExceptions:
    """Test custom exception classes."""
    
    def test_a2a_client_error(self):
        """Test A2AClientError."""
        error = A2AClientError("Test error")
        assert str(error) == "Test error"
    
    def test_a2a_client_http_error(self):
        """Test A2AClientHTTPError."""
        error = A2AClientHTTPError(404, "Not found")
        assert error.status_code == 404
        assert error.message == "Not found"
        assert "HTTP Error 404" in str(error)
    
    def test_a2a_client_json_error(self):
        """Test A2AClientJSONError."""
        error = A2AClientJSONError("Invalid JSON")
        assert error.message == "Invalid JSON"
        assert "JSON Error" in str(error)


class TestErrorClasses:
    """Test JSONRPC error classes."""
    
    def test_json_parse_error(self):
        """Test JSONParseError."""
        from src.common.types import JSONParseError
        error = JSONParseError()
        assert error.code == -32700
        assert "Invalid JSON payload" in error.message
    
    def test_method_not_found_error(self):
        """Test MethodNotFoundError."""
        from src.common.types import MethodNotFoundError
        error = MethodNotFoundError()
        assert error.code == -32601
        assert "Method not found" in error.message
    
    def test_task_not_found_error(self):
        """Test TaskNotFoundError."""
        from src.common.types import TaskNotFoundError
        error = TaskNotFoundError()
        assert error.code == -32001
        assert "Task not found" in error.message