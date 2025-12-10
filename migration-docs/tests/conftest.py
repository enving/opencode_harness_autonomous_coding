"""
Test utilities and mock helpers for OpenCode SDK tests.
========================================================

Provides common fixtures, mocks, and utilities for testing OpenCode functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

# Mock classes for OpenCode SDK
class MockSession:
    """Mock OpenCode session object."""
    
    def __init__(self, session_id: str = "test-session-123"):
        self.id = session_id


class MockContent:
    """Mock content object for OpenCode responses."""
    
    def __init__(self, text: str = "Mock response"):
        self.text = text


class MockToolUse:
    """Mock tool use object for OpenCode responses."""
    
    def __init__(self, name: str = "Bash", input_data: Optional[Dict[str, Any]] = None):
        self.name = name
        self.type = "tool_use"
        self.input = input_data or {}


class MockResponse:
    """Mock OpenCode response object."""
    
    def __init__(self, content_text: str = "", tool_uses: Optional[list] = None):
        self.content = []
        
        if content_text:
            self.content.append(MockContent(content_text))
        
        if tool_uses:
            for tool_use in tool_uses:
                self.content.append(tool_use)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir(parents=True, exist_ok=True)
        yield project_dir


@pytest.fixture
def mock_opencode_client():
    """Create a mock OpenCode client."""
    client = AsyncMock()
    
    # Mock session operations
    client.session.create = AsyncMock(return_value=MockSession())
    client.session.list = AsyncMock(return_value=[])
    client.session.delete = AsyncMock()
    client.session.chat = AsyncMock(return_value=MockResponse("Test response"))
    
    return client


@pytest.fixture
def mock_session():
    """Create a mock session object."""
    return MockSession()


@pytest.fixture
def sample_opencode_config():
    """Sample OpenCode configuration for testing."""
    return {
        "model": "anthropic/claude-3-5-sonnet-20241022",
        "permissions": {
            "allow": [
                "Read(/test/project/**)",
                "Write(/test/project/**)",
                "Edit(/test/project/**)",
                "Glob(/test/project/**)",
                "Grep(/test/project/**)",
                "Bash(*)"
            ],
            "defaultMode": "acceptEdits"
        },
        "security": {
            "bash_allowlist": [
                "ls", "cat", "head", "tail", "wc", "grep",
                "npm", "node", "git", "ps", "lsof", "sleep", "pkill"
            ]
        }
    }


@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock API keys for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all API keys from environment for testing."""
    for key in ["ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "OPENCODE_API_KEY"]:
        monkeypatch.delenv(key, raising=False)


class AsyncContextManagerMock:
    """Mock for async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.enter_called = False
        self.exit_called = False
    
    async def __aenter__(self):
        self.enter_called = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exit_called = True


def create_mock_response_with_tools(
    content_text: str = "",
    tool_names: Optional[list] = None,
    tool_inputs: Optional[list] = None
) -> MockResponse:
    """Create a mock response with tool uses."""
    tool_uses = []
    
    if tool_names:
        tool_inputs = tool_inputs or [{}] * len(tool_names)
        for name, input_data in zip(tool_names, tool_inputs):
            tool_uses.append(MockToolUse(name, input_data))
    
    return MockResponse(content_text, tool_uses)


def create_test_file(project_dir: Path, filename: str, content: str = "test content") -> Path:
    """Create a test file in the project directory."""
    file_path = project_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path


def create_opencode_settings(project_dir: Path, config: Optional[Dict[str, Any]] = None) -> Path:
    """Create an OpenCode settings file."""
    if config is None:
        config = sample_opencode_config()
    
    settings_file = project_dir / ".opencode_settings.json"
    settings_file.write_text(json.dumps(config, indent=2))
    return settings_file


async def run_async_test(coro):
    """Helper to run async test functions."""
    return await coro


def assert_file_exists(project_dir: Path, filename: str):
    """Assert that a file exists in the project directory."""
    file_path = project_dir / filename
    assert file_path.exists(), f"File {filename} should exist in {project_dir}"


def assert_file_content(project_dir: Path, filename: str, expected_content: str):
    """Assert that a file contains expected content."""
    file_path = project_dir / filename
    assert file_path.exists(), f"File {filename} should exist"
    actual_content = file_path.read_text()
    assert expected_content in actual_content, f"File {filename} should contain '{expected_content}'"