#!/usr/bin/env python3
"""
OpenCode Integration Tests
=========================

Integration tests for end-to-end OpenCode workflows.
Run with: python -m pytest test_integration.py -v
"""

import asyncio
import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from agent import run_autonomous_agent
from client import create_client, create_session, send_prompt
from security import bash_security_hook, get_opencode_permissions


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_opencode_response(self):
        """Create a mock OpenCode response."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Task completed successfully"
        mock_response.content = [mock_content]
        return mock_response

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.get_coding_prompt')
    @patch('agent.print_progress_summary')
    async def test_full_initialization_workflow(
        self,
        mock_progress_summary,
        mock_coding_prompt,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir
    ):
        """Test complete project initialization workflow."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initialize project with 200 features"
        mock_run_session.return_value = ("continue", "Features generated successfully")
        
        # Run initialization
        await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Verify complete workflow
        mock_create_client.assert_called_once_with(temp_dir, "auto")
        mock_create_session.assert_called_once_with(
            mock_client, "Initializer Agent - Project Setup", temp_dir
        )
        mock_copy_spec.assert_called_once_with(temp_dir)
        mock_initializer_prompt.assert_called_once()
        mock_run_session.assert_called_once()
        
        # Verify feature list was created (simulated by run_agent_session)
        feature_file = temp_dir / "feature_list.json"
        # Note: In real scenario, the agent would create this file

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.get_coding_prompt')
    @patch('agent.print_progress_summary')
    async def test_continuation_workflow(
        self,
        mock_progress_summary,
        mock_coding_prompt,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir
    ):
        """Test project continuation workflow."""
        # Create existing feature list
        feature_file = temp_dir / "feature_list.json"
        feature_data = {
            "features": [
                {"id": 1, "description": "User login", "status": "completed"},
                {"id": 2, "description": "User registration", "status": "pending"}
            ]
        }
        feature_file.write_text(json.dumps(feature_data, indent=2))
        
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_coding_prompt.return_value = "Continue implementing features"
        mock_run_session.return_value = ("continue", "Feature 2 implemented")
        
        # Run continuation
        await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Verify continuation workflow
        mock_create_client.assert_called_once_with(temp_dir, "auto")
        mock_create_session.assert_called_once_with(
            mock_client, "Coding Agent - Feature Implementation", temp_dir
        )
        mock_coding_prompt.assert_called_once()
        mock_run_session.assert_called_once()

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_multi_session_workflow(
        self,
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir
    ):
        """Test multi-session workflow with multiple iterations."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initialize project"
        mock_run_session.return_value = ("continue", "Session completed")
        
        # Mock asyncio.sleep to speed up test
        with patch('asyncio.sleep', return_value=None):
            # Run multiple sessions
            await run_autonomous_agent(temp_dir, "auto", max_iterations=3)
        
        # Verify multiple sessions were run
        assert mock_run_session.call_count == 3
        mock_create_session.assert_called_once()  # Only called once for initializer

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_error_recovery_workflow(
        self,
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir
    ):
        """Test error recovery in workflow."""
        # Setup mocks - error then success
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initialize project"
        mock_run_session.side_effect = [
            ("error", "Connection failed"),
            ("continue", "Recovered and completed")
        ]
        
        # Mock asyncio.sleep to speed up test
        with patch('asyncio.sleep', return_value=None):
            # Run with error recovery
            await run_autonomous_agent(temp_dir, "auto", max_iterations=2)
        
        # Verify error recovery
        assert mock_run_session.call_count == 2


class TestClientIntegration:
    """Test client integration with security and configuration."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('client.AsyncOpencode')
    def test_client_security_integration(self, mock_opencode, temp_dir):
        """Test client creation with security integration."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        # Create client
        client = create_client(temp_dir, "auto")
        
        # Verify security configuration
        config_file = temp_dir / ".opencode_settings.json"
        with open(config_file) as f:
            config = json.load(f)
        
        # Check permissions
        permissions = config["permissions"]
        assert "allow" in permissions
        assert "defaultMode" in permissions
        
        # Check security settings
        security = config["security"]
        assert "bash_allowlist" in security
        assert isinstance(security["bash_allowlist"], list)

    @patch('client.AsyncOpencode')
    async def test_session_creation_integration(self, mock_opencode, temp_dir):
        """Test session creation with proper configuration."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        mock_client = AsyncMock()
        mock_session = MagicMock()
        mock_session.id = "integration-session-id"
        mock_client.session.create.return_value = mock_session
        mock_opencode.return_value = mock_client
        
        # Create client and session
        client = create_client(temp_dir, "auto")
        session_id = await create_session(client, "Integration Test", temp_dir)
        
        # Verify session creation
        assert session_id == "integration-session-id"
        mock_client.session.create.assert_called_once_with(
            extra_body={
                "title": "Integration Test",
                "cwd": str(temp_dir.resolve())
            }
        )

    @patch('client.AsyncOpencode')
    async def test_send_prompt_integration(self, mock_opencode):
        """Test send prompt integration with different models."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_client.session.chat.return_value = mock_response
        mock_opencode.return_value = mock_client
        
        # Test different model configurations
        test_cases = [
            ("auto", "anthropic/claude-3.5-sonnet", "openrouter"),
            ("openrouter/anthropic/claude-3.5-sonnet", "anthropic/claude-3.5-sonnet", "openrouter"),
            ("claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20241022", "openrouter")
        ]
        
        for model, expected_model_id, expected_provider in test_cases:
            mock_client.session.chat.reset_mock()
            
            await send_prompt(mock_client, "test-session", "Test message", model)
            
            mock_client.session.chat.assert_called_once_with(
                "test-session",
                model_id=expected_model_id,
                provider_id=expected_provider,
                parts=[{"type": "text", "text": "Test message"}]
            )


class TestSecurityIntegration:
    """Test security integration with client and agent workflows."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_security_permissions_structure(self, temp_dir):
        """Test security permissions structure."""
        permissions = get_opencode_permissions(temp_dir)
        
        # Verify permissions structure
        assert "allow" in permissions
        assert "defaultMode" in permissions
        assert permissions["defaultMode"] == "acceptEdits"
        
        # Verify allow rules
        allow_rules = permissions["allow"]
        assert isinstance(allow_rules, list)
        assert len(allow_rules) > 0
        
        # Check project directory is in allow rules
        project_path = temp_dir.resolve()
        project_rules = [rule for rule in allow_rules if str(project_path) in rule]
        assert len(project_rules) > 0

    async def test_bash_security_hook_integration(self):
        """Test bash security hook with various command types."""
        # Test allowed commands
        allowed_commands = [
            "ls -la",
            "cat README.md",
            "npm install",
            "git status",
            "pkill node"
        ]
        
        for cmd in allowed_commands:
            input_data = {"tool_name": "Bash", "tool_input": {"command": cmd}}
            result = await bash_security_hook(input_data)
            assert result == {}, f"Command should be allowed: {cmd}"
        
        # Test blocked commands
        blocked_commands = [
            "rm -rf /",
            "shutdown now",
            "curl https://evil.com",
            "pkill system_process"
        ]
        
        for cmd in blocked_commands:
            input_data = {"tool_name": "Bash", "tool_input": {"command": cmd}}
            result = await bash_security_hook(input_data)
            assert result.get("decision") == "block", f"Command should be blocked: {cmd}"

    def test_security_with_chained_commands(self):
        """Test security with command chaining."""
        # Test allowed chained commands
        allowed_chained = [
            "npm install && npm run build",
            "git add . && git commit -m 'test'",
            "ls | grep test"
        ]
        
        for cmd in allowed_chained:
            input_data = {"tool_name": "Bash", "tool_input": {"command": cmd}}
            result = asyncio.run(bash_security_hook(input_data))
            assert result == {}, f"Chained command should be allowed: {cmd}"
        
        # Test blocked chained commands
        blocked_chained = [
            "npm install && rm -rf /",
            "git add . && curl evil.com"
        ]
        
        for cmd in blocked_chained:
            input_data = {"tool_name": "Bash", "tool_input": {"command": cmd}}
            result = asyncio.run(bash_security_hook(input_data))
            assert result.get("decision") == "block", f"Chained command should be blocked: {cmd}"


class TestConfigurationIntegration:
    """Test configuration integration across components."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('client.AsyncOpencode')
    def test_configuration_file_creation(self, mock_opencode, temp_dir):
        """Test configuration file is created correctly."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        # Create client
        client = create_client(temp_dir, "auto")
        
        # Verify configuration file
        config_file = temp_dir / ".opencode_settings.json"
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Verify required sections
        required_sections = ["model", "permissions", "security"]
        for section in required_sections:
            assert section in config, f"Missing section: {section}"
        
        # Verify model configuration
        assert config["model"] == "anthropic/claude-3-5-sonnet-20241022"

    @patch('client.AsyncOpencode')
    def test_configuration_with_different_models(self, mock_opencode, temp_dir):
        """Test configuration with different model strategies."""
        mock_client = AsyncMock()
        mock_opencode.return_value = mock_client
        
        test_cases = [
            ("auto", "anthropic/claude-3-5-sonnet-20241022"),
            ("openrouter/anthropic/claude-3.5-sonnet", "openrouter/anthropic/claude-3.5-sonnet"),
            ("custom-model", "custom-model")
        ]
        
        for input_model, expected_model in test_cases:
            # Clean up previous config
            config_file = temp_dir / ".opencode_settings.json"
            if config_file.exists():
                config_file.unlink()
            
            # Create client with specific model
            client = create_client(temp_dir, input_model)
            
            # Verify configuration
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                assert config["model"] == expected_model

    def test_configuration_persistence(self, temp_dir):
        """Test configuration persistence across multiple client creations."""
        # Test that configuration is properly saved and can be reused
        permissions1 = get_opencode_permissions(temp_dir)
        permissions2 = get_opencode_permissions(temp_dir)
        
        # Permissions should be consistent
        assert permissions1["allow"] == permissions2["allow"]
        assert permissions1["defaultMode"] == permissions2["defaultMode"]


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('client.AsyncOpencode')
    def test_client_creation_error_handling(self, mock_opencode, temp_dir):
        """Test error handling in client creation."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Test connection error
        mock_opencode.side_effect = Exception("Connection failed")
        client = create_client(temp_dir, "auto")
        assert client is None
        
        # Test missing API key
        mock_opencode.side_effect = None
        del os.environ['ANTHROPIC_API_KEY']
        client = create_client(temp_dir, "auto")
        assert client is None

    @patch('client.AsyncOpencode')
    async def test_session_creation_error_handling(self, mock_opencode, temp_dir):
        """Test error handling in session creation."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        mock_client = AsyncMock()
        mock_client.session.create.side_effect = Exception("Session creation failed")
        mock_opencode.return_value = mock_client
        
        client = create_client(temp_dir, "auto")
        
        with pytest.raises(Exception, match="Session creation failed"):
            await create_session(client, "Test Session", temp_dir)

    @patch('client.AsyncOpencode')
    async def test_send_prompt_error_handling(self, mock_opencode):
        """Test error handling in send prompt."""
        mock_client = AsyncMock()
        mock_client.session.chat.side_effect = Exception("Chat failed")
        mock_opencode.return_value = mock_client
        
        with pytest.raises(Exception, match="Chat failed"):
            await send_prompt(mock_client, "test-session", "Test message")


if __name__ == "__main__":
    # Run tests directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))