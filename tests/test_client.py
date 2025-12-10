"""
Unit tests for client.py module.
===============================

Tests OpenCode client creation, session management, and prompt sending functionality.
"""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from client import create_client, create_session, send_prompt
from conftest import (
    MockSession, 
    MockResponse, 
    temp_project_dir, 
    mock_opencode_client,
    mock_api_keys,
    clean_env
)


class TestCreateClient:
    """Test cases for create_client function."""
    
    @pytest.mark.asyncio
    async def test_create_client_with_anthropic_key(self, temp_project_dir, mock_api_keys):
        """Test creating client with Anthropic API key."""
        with patch('client.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(temp_project_dir, "auto")
            
            assert client is not None
            mock_opencode.assert_called_once_with(base_url="http://localhost:4096")
            
            # Check that settings file was created
            settings_file = temp_project_dir / ".opencode_settings.json"
            assert settings_file.exists()
            
            config = json.loads(settings_file.read_text())
            assert "permissions" in config
            assert "security" in config
    
    @pytest.mark.asyncio
    async def test_create_client_with_openrouter_key(self, temp_project_dir, mock_api_keys):
        """Test creating client with OpenRouter API key."""
        with patch('client.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Remove Anthropic key to test OpenRouter preference
            with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}):
                client = create_client(temp_project_dir, "auto")
                
                assert client is not None
                
                # Check settings file
                settings_file = temp_project_dir / ".opencode_settings.json"
                config = json.loads(settings_file.read_text())
                assert "openrouter/anthropic/claude-3.5-sonnet" in config["model"]
    
    @pytest.mark.asyncio
    async def test_create_client_no_api_keys(self, temp_project_dir, clean_env):
        """Test creating client with no API keys returns None."""
        with patch('builtins.print') as mock_print:
            client = create_client(temp_project_dir, "auto")
            
            assert client is None
            mock_print.assert_any_call("🔑 No API key found!")
    
    @pytest.mark.asyncio
    async def test_create_client_custom_model(self, temp_project_dir, mock_api_keys):
        """Test creating client with custom model."""
        with patch('client.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(temp_project_dir, "custom/model")
            
            assert client is not None
            
            # Check settings file
            settings_file = temp_project_dir / ".opencode_settings.json"
            config = json.loads(settings_file.read_text())
            assert config["model"] == "custom/model"
    
    @pytest.mark.asyncio
    async def test_create_client_custom_base_url(self, temp_project_dir, mock_api_keys):
        """Test creating client with custom base URL."""
        with patch.dict(os.environ, {'OPENCODE_BASE_URL': 'http://custom:8080'}):
            with patch('client.AsyncOpencode') as mock_opencode:
                mock_client = AsyncMock()
                mock_opencode.return_value = mock_client
                
                client = create_client(temp_project_dir, "auto")
                
                assert client is not None
                mock_opencode.assert_called_once_with(base_url="http://custom:8080")
    
    @pytest.mark.asyncio
    async def test_create_client_exception_handling(self, temp_project_dir, mock_api_keys):
        """Test exception handling when creating client."""
        with patch('client.AsyncOpencode', side_effect=Exception("Connection failed")):
            with patch('builtins.print') as mock_print:
                client = create_client(temp_project_dir, "auto")
                
                assert client is None
                mock_print.assert_any_call("❌ Failed to create OpenCode client: Connection failed")


class TestCreateSession:
    """Test cases for create_session function."""
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, mock_opencode_client, temp_project_dir):
        """Test successful session creation."""
        session_id = await create_session(mock_opencode_client, "Test Session", temp_project_dir)
        
        assert session_id == "test-session-123"
        mock_opencode_client.session.create.assert_called_once_with(
            extra_body={
                "title": "Test Session",
                "cwd": str(temp_project_dir.resolve())
            }
        )
    
    @pytest.mark.asyncio
    async def test_create_session_failure(self, mock_opencode_client, temp_project_dir):
        """Test session creation failure."""
        mock_opencode_client.session.create.side_effect = Exception("Session creation failed")
        
        with pytest.raises(Exception, match="Session creation failed"):
            await create_session(mock_opencode_client, "Test Session", temp_project_dir)


class TestSendPrompt:
    """Test cases for send_prompt function."""
    
    @pytest.mark.asyncio
    async def test_send_prompt_auto_model(self, mock_opencode_client):
        """Test sending prompt with auto model selection."""
        session_id = "test-session"
        message = "Hello, world!"
        
        await send_prompt(mock_opencode_client, session_id, message, "auto")
        
        mock_opencode_client.session.chat.assert_called_once_with(
            session_id,
            model_id="anthropic/claude-3.5-sonnet",
            provider_id="openrouter",
            parts=[{"type": "text", "text": message}]
        )
    
    @pytest.mark.asyncio
    async def test_send_prompt_specific_model_with_provider(self, mock_opencode_client):
        """Test sending prompt with specific model including provider."""
        session_id = "test-session"
        message = "Hello, world!"
        
        await send_prompt(mock_opencode_client, session_id, message, "anthropic/claude-3-5-sonnet")
        
        mock_opencode_client.session.chat.assert_called_once_with(
            session_id,
            model_id="claude-3-5-sonnet",
            provider_id="anthropic",
            parts=[{"type": "text", "text": message}]
        )
    
    @pytest.mark.asyncio
    async def test_send_prompt_specific_model_no_provider(self, mock_opencode_client):
        """Test sending prompt with specific model without provider."""
        session_id = "test-session"
        message = "Hello, world!"
        
        await send_prompt(mock_opencode_client, session_id, message, "claude-3-5-sonnet")
        
        mock_opencode_client.session.chat.assert_called_once_with(
            session_id,
            model_id="claude-3-5-sonnet",
            provider_id="openrouter",
            parts=[{"type": "text", "text": message}]
        )
    
    @pytest.mark.asyncio
    async def test_send_prompt_failure(self, mock_opencode_client):
        """Test prompt sending failure."""
        mock_opencode_client.session.chat.side_effect = Exception("Chat failed")
        
        with pytest.raises(Exception, match="Chat failed"):
            await send_prompt(mock_opencode_client, "test-session", "Hello", "auto")


class TestClientIntegration:
    """Integration tests for client functions."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_project_dir, mock_api_keys):
        """Test full workflow: create client, create session, send prompt."""
        with patch('client.AsyncOpencode') as mock_opencode:
            # Setup mock client
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            mock_client.session.create.return_value = MockSession("workflow-test")
            mock_client.session.chat.return_value = MockResponse("Workflow response")
            
            # Create client
            client = create_client(temp_project_dir, "auto")
            assert client is not None
            
            # Create session
            session_id = await create_session(client, "Workflow Test", temp_project_dir)
            assert session_id == "workflow-test"
            
            # Send prompt
            result = await send_prompt(client, session_id, "Test message", "auto")
            assert result is not None
            
            # Verify all calls were made
            mock_client.session.create.assert_called_once()
            mock_client.session.chat.assert_called_once()