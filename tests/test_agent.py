"""
Unit tests for agent.py functionality.
===================================

Tests autonomous agent session logic, progress tracking, and workflow management.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from agent import run_agent_session, run_autonomous_agent
from conftest import (
    MockSession, 
    MockResponse, 
    MockContent,
    MockToolUse,
    create_mock_response_with_tools,
    create_test_file,
    temp_project_dir,
    mock_opencode_client,
    mock_api_keys
)


class TestRunAgentSession:
    """Test cases for run_agent_session function."""

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_agent_session_success(self, mock_opencode_client, temp_project_dir):
        """Test successful agent session execution."""
        # Mock response with text content
        mock_response = MockResponse("Agent response text")
        mock_opencode_client.session.chat.return_value = mock_response
        
        status, response_text = await run_agent_session(
            mock_opencode_client,
            "test-session-id",
            "Test prompt",
            temp_project_dir
        )
        
        assert status == "continue"
        assert response_text == "Agent response text"
        mock_opencode_client.session.chat.assert_called_once()

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_agent_session_with_tool_uses(self, mock_opencode_client, temp_project_dir):
        """Test agent session with tool uses in response."""
        # Mock response with tool uses
        tool_uses = [
            MockToolUse("Bash", {"command": "ls -la"}),
            MockToolUse("Read", {"filePath": "test.txt"})
        ]
        mock_response = create_mock_response_with_tools("Response with tools", ["Bash", "Read"], [{"command": "ls -la"}, {"filePath": "test.txt"}])
        mock_opencode_client.session.chat.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            status, response_text = await run_agent_session(
                mock_opencode_client,
                "test-session-id",
                "Test prompt",
                temp_project_dir
            )
            
            assert status == "continue"
            # Verify tool use output was printed
            mock_print.assert_any_call("[Tool: Bash]")

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_agent_session_exception(self, mock_opencode_client, temp_project_dir):
        """Test agent session handles exceptions."""
        mock_opencode_client.session.chat.side_effect = Exception("Session failed")
        
        with patch('builtins.print') as mock_print:
            status, response_text = await run_agent_session(
                mock_opencode_client,
                "test-session-id",
                "Test prompt",
                temp_project_dir
            )
            
            assert status == "error"
            assert response_text == "Session failed"
            mock_print.assert_any_call("Error during agent session: Session failed")

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_agent_session_long_tool_input(self, mock_opencode_client, temp_project_dir):
        """Test agent session with long tool input that gets truncated."""
        long_input = "x" * 300  # Long input that should be truncated
        tool_uses = [MockToolUse("Bash", {"command": long_input})]
        mock_response = create_mock_response_with_tools("Response", ["Bash"], [{"command": long_input}])
        mock_opencode_client.session.chat.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            status, response_text = await run_agent_session(
                mock_opencode_client,
                "test-session-id",
                "Test prompt",
                temp_project_dir
            )
            
            assert status == "continue"
            # Verify long input was truncated in output
            mock_print.assert_any_call(f"   Input: {long_input[:200]}...")


class TestRunAutonomousAgent:
    """Test cases for run_autonomous_agent function."""

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_first_run(self, temp_project_dir, mock_api_keys):
        """Test autonomous agent first run (initializer)."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            mock_send_prompt.return_value = MockResponse("Initializer response")
            mock_get_prompt.return_value = "Initializer prompt"
            
            # Run agent
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=1)
            
            # Verify first run behavior
            mock_copy_spec.assert_called_once_with(temp_project_dir)
            mock_create_session.assert_called_once_with(
                mock_client, "Initializer Agent - Project Setup", temp_project_dir
            )
            mock_get_prompt.assert_called_once()

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_continuation(self, temp_project_dir, mock_api_keys):
        """Test autonomous agent continuation (coding agent)."""
        # Create existing feature_list.json to simulate continuation
        feature_list = {
            "features": [{"id": "test", "status": "pending"}],
            "total": 1,
            "completed": 0,
            "pending": 1
        }
        create_test_file(temp_project_dir, "feature_list.json", json.dumps(feature_list))
        
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.get_coding_prompt') as mock_get_prompt, \
             patch('agent.print_progress_summary') as mock_print_summary:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            mock_send_prompt.return_value = MockResponse("Coding response")
            mock_get_prompt.return_value = "Coding prompt"
            
            # Run agent
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=1)
            
            # Verify continuation behavior
            mock_create_session.assert_called_once_with(
                mock_client, "Coding Agent - Feature Implementation", temp_project_dir
            )
            mock_get_prompt.assert_called_once()

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_max_iterations(self, temp_project_dir, mock_api_keys):
        """Test autonomous agent respects max iterations limit."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt, \
             patch('asyncio.sleep') as mock_sleep:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            mock_send_prompt.return_value = MockResponse("Response")
            mock_get_prompt.return_value = "Prompt"
            
            # Run agent with max iterations
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=2)
            
            # Verify session was called twice (2 iterations)
            assert mock_send_prompt.call_count == 2

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_unlimited_iterations(self, temp_project_dir, mock_api_keys):
        """Test autonomous agent with unlimited iterations stops on error."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt, \
             patch('asyncio.sleep') as mock_sleep:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            
            # First call succeeds, second raises exception to stop the loop
            mock_send_prompt.side_effect = [
                MockResponse("Response"),
                Exception("Stop execution")
            ]
            mock_get_prompt.return_value = "Prompt"
            
            # Run agent without max iterations (should stop on exception)
            with pytest.raises(Exception, match="Stop execution"):
                await run_autonomous_agent(temp_project_dir, "auto")

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_error_recovery(self, temp_project_dir, mock_api_keys):
        """Test autonomous agent error recovery with fresh session."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt, \
             patch('asyncio.sleep') as mock_sleep, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            
            # First call raises exception, second succeeds
            mock_send_prompt.side_effect = [
                Exception("Session error"),
                MockResponse("Recovery response")
            ]
            mock_get_prompt.return_value = "Prompt"
            
            # Run agent with max iterations to allow recovery
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=2)
            
            # Verify error recovery
            assert mock_send_prompt.call_count == 2
            mock_print.assert_any_call("Session encountered an error")
            mock_print.assert_any_call("Will retry with a fresh session...")

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_no_api_keys(self, temp_project_dir):
        """Test autonomous agent handles missing API keys gracefully."""
        with patch('agent.create_client') as mock_create_client, \
             patch('builtins.print') as mock_print:
            
            # Mock create_client returning None (no API keys)
            mock_create_client.return_value = None
            
            # Run agent should handle this gracefully
            try:
                await run_autonomous_agent(temp_project_dir, "auto", max_iterations=1)
            except Exception as e:
                # Should fail early, not continue
                assert "client" in str(e).lower() or "api" in str(e).lower()

    @pytest.mark.agent
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_autonomous_agent_project_dir_creation(self, mock_api_keys):
        """Test autonomous agent creates project directory if needed."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "test-session-id"
            mock_send_prompt.return_value = MockResponse("Response")
            mock_get_prompt.return_value = "Prompt"
            
            # Use non-existent directory
            non_existent_dir = Path("/tmp/test_autonomous_agent/project")
            
            try:
                await run_autonomous_agent(non_existent_dir, "auto", max_iterations=1)
                
                # Verify directory was created
                assert non_existent_dir.exists()
            finally:
                # Clean up
                if non_existent_dir.exists():
                    import shutil
                    shutil.rmtree(non_existent_dir.parent)


class TestAgentIntegration:
    """Integration tests for agent functionality."""

    @pytest.mark.agent
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_agent_workflow_simulation(self, temp_project_dir, mock_api_keys):
        """Test simulated full agent workflow."""
        with patch('agent.create_client') as mock_create_client, \
             patch('agent.create_session') as mock_create_session, \
             patch('agent.send_prompt') as mock_send_prompt, \
             patch('agent.copy_spec_to_project') as mock_copy_spec, \
             patch('agent.get_initializer_prompt') as mock_get_prompt, \
             patch('agent.get_coding_prompt') as mock_get_coding_prompt, \
             patch('agent.print_progress_summary') as mock_print_summary:
            
            # Setup mocks
            mock_client = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_create_session.return_value = "workflow-session-id"
            
            # Mock different responses for different phases
            mock_send_prompt.side_effect = [
                MockResponse("Initializer complete - created feature_list.json"),
                MockResponse("Coding complete - implemented feature")
            ]
            mock_get_prompt.return_value = "Test prompt"
            mock_get_coding_prompt.return_value = "Coding prompt"
            
            # First run (initializer)
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=1)
            
            # Verify initializer was called
            mock_copy_spec.assert_called_once()
            mock_get_prompt.assert_called_once()
            
            # Reset mocks for second phase
            mock_create_session.reset_mock()
            mock_send_prompt.reset_mock()
            mock_get_prompt.reset_mock()
            
            # Create feature_list.json to simulate continuation
            feature_list = {
                "features": [{"id": "test", "status": "pending"}],
                "total": 1,
                "completed": 0,
                "pending": 1
            }
            create_test_file(temp_project_dir, "feature_list.json", json.dumps(feature_list))
            
            # Second run (coding agent)
            await run_autonomous_agent(temp_project_dir, "auto", max_iterations=1)
            
            # Verify coding agent was called
            mock_get_coding_prompt.assert_called_once()
            mock_create_session.assert_called_once_with(
                mock_client, "Coding Agent - Feature Implementation", temp_project_dir
            )