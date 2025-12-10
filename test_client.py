#!/usr/bin/env python3
"""
OpenCode Client Tests
====================

Unit tests for the OpenCode client configuration and session management.
Run with: python -m pytest test_client.py -v
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from client import create_client, create_session, send_prompt


class TestCreateClient:
    """Test cases for create_client function."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()

    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('client.AsyncOpencode')
    def test_create_client_with_anthropic_key(self, mock_opencode):
        """Test client creation with Anthropic API key."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "anthropic/claude-3-5-sonnet-20241022")
        
        assert client is not None
        mock_opencode.assert_called_once_with(base_url="http://localhost:4096")
        
        # Check config file creation
        config_file = self.temp_dir / ".opencode_settings.json"
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert config["model"] == "anthropic/claude-3-5-sonnet-20241022"
        assert "permissions" in config
        assert "security" in config

    @patch('client.AsyncOpencode')
    def test_create_client_with_openrouter_key(self, mock_opencode):
        """Test client creation with OpenRouter API key."""
        os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "openrouter/anthropic/claude-3.5-sonnet")
        
        assert client is not None
        mock_opencode.assert_called_once_with(base_url="http://localhost:4096")

    @patch('client.AsyncOpencode')
    def test_create_client_auto_mode_with_openrouter(self, mock_opencode):
        """Test auto model selection with OpenRouter key."""
        os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "auto")
        
        assert client is not None
        
        # Check config uses OpenRouter model
        config_file = self.temp_dir / ".opencode_settings.json"
        with open(config_file) as f:
            config = json.load(f)
        
        assert config["model"] == "openrouter/anthropic/claude-3.5-sonnet"

    @patch('client.AsyncOpencode')
    def test_create_client_auto_mode_with_anthropic(self, mock_opencode):
        """Test auto model selection with Anthropic key."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "auto")
        
        assert client is not None
        
        # Check config uses Anthropic model
        config_file = self.temp_dir / ".opencode_settings.json"
        with open(config_file) as f:
            config = json.load(f)
        
        assert config["model"] == "anthropic/claude-3-5-sonnet-20241022"

    def test_create_client_no_api_key(self):
        """Test client creation fails without API key."""
        # Remove all API keys
        for key in ['ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY', 'OPENCODE_API_KEY']:
            if key in os.environ:
                del os.environ[key]
        
        client = create_client(self.temp_dir, "auto")
        assert client is None

    @patch('client.AsyncOpencode')
    def test_create_client_with_custom_base_url(self, mock_opencode):
        """Test client creation with custom base URL."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        os.environ['OPENCODE_BASE_URL'] = 'http://custom-server:8080'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "auto")
        
        assert client is not None
        mock_opencode.assert_called_once_with(base_url="http://custom-server:8080")

    @patch('client.AsyncOpencode')
    def test_create_client_opencode_exception(self, mock_opencode):
        """Test client creation handles exceptions."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        mock_opencode.side_effect = Exception("Connection failed")
        
        client = create_client(self.temp_dir, "auto")
        assert client is None

    @patch('client.AsyncOpencode')
    def test_create_client_permissions_config(self, mock_opencode):
        """Test that permissions are correctly configured."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "auto")
        
        # Check permissions in config
        config_file = self.temp_dir / ".opencode_settings.json"
        with open(config_file) as f:
            config = json.load(f)
        
        permissions = config["permissions"]
        assert "allow" in permissions
        assert "defaultMode" in permissions
        assert permissions["defaultMode"] == "acceptEdits"
        
        # Check that project directory is in allowed paths
        allow_rules = permissions["allow"]
        project_path = self.temp_dir.resolve()
        assert any(str(project_path) in rule for rule in allow_rules)

    @patch('client.AsyncOpencode')
    def test_create_client_security_config(self, mock_opencode):
        """Test that security configuration is correctly set."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        client = create_client(self.temp_dir, "auto")
        
        # Check security config
        config_file = self.temp_dir / ".opencode_settings.json"
        with open(config_file) as f:
            config = json.load(f)
        
        security = config["security"]
        assert "bash_allowlist" in security
        
        allowed_commands = security["bash_allowlist"]
        expected_commands = [
            "ls", "cat", "head", "tail", "wc", "grep",
            "npm", "node", "git", "ps", "lsof", "sleep", "pkill"
        ]
        
        for cmd in expected_commands:
            assert cmd in allowed_commands


class TestCreateSession:
    """Test cases for create_session function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock OpenCode client."""
        client = AsyncMock()
        mock_session = MagicMock()
        mock_session.id = "test-session-id"
        client.session.create.return_value = mock_session
        return client

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_create_session_success(self, mock_client, temp_dir):
        """Test successful session creation."""
        session_id = await create_session(mock_client, "Test Session", temp_dir)
        
        assert session_id == "test-session-id"
        mock_client.session.create.assert_called_once_with(
            extra_body={
                "title": "Test Session",
                "cwd": str(temp_dir.resolve())
            }
        )

    async def test_create_session_failure(self, mock_client, temp_dir):
        """Test session creation failure."""
        mock_client.session.create.side_effect = Exception("Session creation failed")
        
        with pytest.raises(Exception, match="Session creation failed"):
            await create_session(mock_client, "Test Session", temp_dir)

    async def test_create_session_with_different_titles(self, mock_client, temp_dir):
        """Test session creation with different titles."""
        titles = [
            "Initializer Agent - Project Setup",
            "Coding Agent - Feature Implementation",
            "Custom Session Title"
        ]
        
        for title in titles:
            session_id = await create_session(mock_client, title, temp_dir)
            assert session_id == "test-session-id"
            
            # Check the call arguments
            call_args = mock_client.session.create.call_args
            assert call_args[1]["extra_body"]["title"] == title


class TestSendPrompt:
    """Test cases for send_prompt function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock OpenCode client."""
        client = AsyncMock()
        client.session.chat.return_value = MagicMock()
        return client

    async def test_send_prompt_auto_model(self, mock_client):
        """Test sending prompt with auto model selection."""
        session_id = "test-session"
        message = "Test message"
        
        await send_prompt(mock_client, session_id, message, "auto")
        
        mock_client.session.chat.assert_called_once_with(
            session_id,
            model_id="anthropic/claude-3.5-sonnet",
            provider_id="openrouter",
            parts=[{"type": "text", "text": message}]
        )

    async def test_send_prompt_specific_model_with_provider(self, mock_client):
        """Test sending prompt with specific model including provider."""
        session_id = "test-session"
        message = "Test message"
        model = "openrouter/anthropic/claude-3.5-sonnet"
        
        await send_prompt(mock_client, session_id, message, model)
        
        mock_client.session.chat.assert_called_once_with(
            session_id,
            model_id="anthropic/claude-3.5-sonnet",
            provider_id="openrouter",
            parts=[{"type": "text", "text": message}]
        )

    async def test_send_prompt_specific_model_no_provider(self, mock_client):
        """Test sending prompt with specific model without provider."""
        session_id = "test-session"
        message = "Test message"
        model = "claude-3-5-sonnet-20241022"
        
        await send_prompt(mock_client, session_id, message, model)
        
        mock_client.session.chat.assert_called_once_with(
            session_id,
            model_id="claude-3-5-sonnet-20241022",
            provider_id="openrouter",  # Default provider
            parts=[{"type": "text", "text": message}]
        )

    async def test_send_prompt_failure(self, mock_client):
        """Test send prompt failure."""
        session_id = "test-session"
        message = "Test message"
        
        mock_client.session.chat.side_effect = Exception("Chat failed")
        
        with pytest.raises(Exception, match="Chat failed"):
            await send_prompt(mock_client, session_id, message)

    async def test_send_prompt_response_structure(self, mock_client):
        """Test that send prompt returns the expected response structure."""
        session_id = "test-session"
        message = "Test message"
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response text")]
        mock_client.session.chat.return_value = mock_response
        
        response = await send_prompt(mock_client, session_id, message)
        
        assert response == mock_response
        mock_client.session.chat.assert_called_once()


class TestClientIntegration:
    """Integration tests for client functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('client.AsyncOpencode')
    def test_full_client_workflow(self, mock_opencode, temp_dir):
        """Test full client creation and configuration workflow."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        mock_client = AsyncMock()
        mock_session = MagicMock()
        mock_session.id = "workflow-session-id"
        mock_client.session.create.return_value = mock_session
        mock_opencode.return_value = mock_client
        
        # Create client
        client = create_client(temp_dir, "auto")
        assert client is not None
        
        # Verify config file exists and has correct structure
        config_file = temp_dir / ".opencode_settings.json"
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        required_keys = ["model", "permissions", "security"]
        for key in required_keys:
            assert key in config
        
        # Verify directory was created
        assert temp_dir.exists()
        assert temp_dir.is_dir()


if __name__ == "__main__":
    # Run tests directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))