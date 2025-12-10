#!/usr/bin/env python3
"""
OpenCode Agent Tests
====================

Unit tests for the OpenCode agent session logic.
Run with: python -m pytest test_agent.py -v
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from agent import run_agent_session, run_autonomous_agent


class TestRunAgentSession:
    """Test cases for run_agent_session function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock OpenCode client."""
        return AsyncMock()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_run_agent_session_success(self, mock_client, temp_dir, capsys):
        """Test successful agent session execution."""
        session_id = "test-session"
        message = "Test message"
        
        # Mock response with content
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Agent response text"
        mock_response.content = [mock_content]
        
        with patch('agent.send_prompt', return_value=mock_response):
            status, response_text = await run_agent_session(
                mock_client, session_id, message, temp_dir
            )
        
        assert status == "continue"
        assert response_text == "Agent response text"
        
        # Check that output was printed
        captured = capsys.readouterr()
        assert "Agent response text" in captured.out

    async def test_run_agent_session_with_tool_use(self, mock_client, temp_dir, capsys):
        """Test agent session with tool use."""
        session_id = "test-session"
        message = "Test message"
        
        # Mock response with tool use
        mock_response = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = "Bash"
        mock_tool.input = {"command": "ls -la"}
        mock_response.content = [mock_tool]
        
        with patch('agent.send_prompt', return_value=mock_response):
            status, response_text = await run_agent_session(
                mock_client, session_id, message, temp_dir
            )
        
        assert status == "continue"
        
        # Check that tool use was printed
        captured = capsys.readouterr()
        assert "[Tool: Bash]" in captured.out
        assert "ls -la" in captured.out

    async def test_run_agent_session_with_long_tool_input(self, mock_client, temp_dir, capsys):
        """Test agent session with long tool input gets truncated."""
        session_id = "test-session"
        message = "Test message"
        
        # Mock response with tool use having long input
        mock_response = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = "Edit"
        long_input = "a" * 300  # Long input string
        mock_tool.input = {"content": long_input}
        mock_response.content = [mock_tool]
        
        with patch('agent.send_prompt', return_value=mock_response):
            status, response_text = await run_agent_session(
                mock_client, session_id, message, temp_dir
            )
        
        assert status == "continue"
        
        # Check that long input was truncated
        captured = capsys.readouterr()
        assert "..." in captured.out  # Should show truncation

    async def test_run_agent_session_exception(self, mock_client, temp_dir, capsys):
        """Test agent session handles exceptions."""
        session_id = "test-session"
        message = "Test message"
        
        with patch('agent.send_prompt', side_effect=Exception("Connection failed")):
            status, response_text = await run_agent_session(
                mock_client, session_id, message, temp_dir
            )
        
        assert status == "error"
        assert response_text == "Connection failed"
        
        # Check that error was printed
        captured = capsys.readouterr()
        assert "Error during agent session" in captured.out

    async def test_run_agent_session_mixed_content(self, mock_client, temp_dir, capsys):
        """Test agent session with mixed text and tool content."""
        session_id = "test-session"
        message = "Test message"
        
        # Mock response with mixed content
        mock_response = MagicMock()
        mock_text = MagicMock()
        mock_text.text = "Here's my response: "
        mock_tool = MagicMock()
        mock_tool.name = "Bash"
        mock_tool.input = {"command": "echo hello"}
        mock_response.content = [mock_text, mock_tool]
        
        with patch('agent.send_prompt', return_value=mock_response):
            status, response_text = await run_agent_session(
                mock_client, session_id, message, temp_dir
            )
        
        assert status == "continue"
        assert response_text == "Here's my response: "
        
        # Check both text and tool were printed
        captured = capsys.readouterr()
        assert "Here's my response:" in captured.out
        assert "[Tool: Bash]" in captured.out


class TestRunAutonomousAgent:
    """Test cases for run_autonomous_agent function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.get_coding_prompt')
    @patch('agent.print_progress_summary')
    async def test_fresh_start_first_run(
        self, 
        mock_progress_summary, 
        mock_coding_prompt, 
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test autonomous agent fresh start (first run)."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initializer prompt"
        mock_run_session.return_value = ("continue", "Response text")
        
        # Run agent
        await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Verify client creation
        mock_create_client.assert_called_once_with(temp_dir, "auto")
        
        # Verify session creation for initializer
        mock_create_session.assert_called_once_with(
            mock_client, "Initializer Agent - Project Setup", temp_dir
        )
        
        # Verify spec was copied
        mock_copy_spec.assert_called_once_with(temp_dir)
        
        # Verify initializer prompt was used
        mock_initializer_prompt.assert_called_once()
        
        # Verify session was run
        mock_run_session.assert_called_once()
        
        # Check output
        captured = capsys.readouterr()
        assert "Fresh start - will use initializer agent" in captured.out
        assert "NOTE: First session takes 10-20+ minutes" in captured.out

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.get_coding_prompt')
    @patch('agent.print_progress_summary')
    async def test_continuation_run(
        self, 
        mock_progress_summary, 
        mock_coding_prompt,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test autonomous agent continuation (existing project)."""
        # Create feature_list.json to simulate existing project
        feature_file = temp_dir / "feature_list.json"
        feature_file.write_text('{"features": []}')
        
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_coding_prompt.return_value = "Coding prompt"
        mock_run_session.return_value = ("continue", "Response text")
        
        # Run agent
        await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Verify client creation
        mock_create_client.assert_called_once_with(temp_dir, "auto")
        
        # Verify session creation for coding agent
        mock_create_session.assert_called_once_with(
            mock_client, "Coding Agent - Feature Implementation", temp_dir
        )
        
        # Verify coding prompt was used
        mock_coding_prompt.assert_called_once()
        
        # Check output
        captured = capsys.readouterr()
        assert "Continuing existing project" in captured.out

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_max_iterations_limit(
        self, 
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test autonomous agent respects max iterations limit."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initializer prompt"
        mock_run_session.return_value = ("continue", "Response text")
        
        # Run agent with max iterations
        await run_autonomous_agent(temp_dir, "auto", max_iterations=2)
        
        # Verify session was called twice
        assert mock_run_session.call_count == 2
        
        # Check output
        captured = capsys.readouterr()
        assert "Reached max iterations (2)" in captured.out

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_error_handling_retry(
        self, 
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test autonomous agent handles errors and retries."""
        # Setup mocks - first call fails, second succeeds
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initializer prompt"
        mock_run_session.side_effect = [
            ("error", "Connection failed"),
            ("continue", "Success")
        ]
        
        # Run agent
        await run_autonomous_agent(temp_dir, "auto", max_iterations=2)
        
        # Verify session was called twice (retry after error)
        assert mock_run_session.call_count == 2
        
        # Check error handling output
        captured = capsys.readouterr()
        assert "Session encountered an error" in captured.out
        assert "Will retry with a fresh session" in captured.out

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_unlimited_iterations(
        self, 
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test autonomous agent with unlimited iterations."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initializer prompt"
        mock_run_session.return_value = ("continue", "Response text")
        
        # Mock asyncio.sleep to speed up test
        with patch('asyncio.sleep', return_value=None):
            # Run agent with no max iterations (should continue until we break)
            task = asyncio.create_task(
                run_autonomous_agent(temp_dir, "auto", max_iterations=None)
            )
            
            # Let it run a few iterations then cancel
            await asyncio.sleep(0.01)
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Verify it was running
        assert mock_run_session.call_count > 0
        
        # Check output
        captured = capsys.readouterr()
        assert "Max iterations: Unlimited" in captured.out

    @patch('agent.create_client')
    async def test_project_directory_creation(self, mock_create_client, temp_dir):
        """Test that project directory is created if it doesn't exist."""
        # Remove the temp directory
        import shutil
        shutil.rmtree(temp_dir)
        
        # Setup mock
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        
        with patch('agent.create_session', return_value="test-session"), \
             patch('agent.run_agent_session', return_value=("continue", "response")), \
             patch('agent.copy_spec_to_project'), \
             patch('agent.get_initializer_prompt', return_value="prompt"):
            
            await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Verify directory was created
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.run_agent_session')
    @patch('agent.copy_spec_to_project')
    @patch('agent.get_initializer_prompt')
    @patch('agent.print_progress_summary')
    async def test_final_summary_output(
        self, 
        mock_progress_summary,
        mock_initializer_prompt,
        mock_copy_spec,
        mock_run_session,
        mock_create_session,
        mock_create_client,
        temp_dir,
        capsys
    ):
        """Test that final summary is printed correctly."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        mock_initializer_prompt.return_value = "Initializer prompt"
        mock_run_session.return_value = ("continue", "Response text")
        
        # Run agent
        await run_autonomous_agent(temp_dir, "auto", max_iterations=1)
        
        # Check final summary output
        captured = capsys.readouterr()
        assert "SESSION COMPLETE" in captured.out
        assert "TO RUN THE GENERATED APPLICATION" in captured.out
        assert "cd " in captured.out
        assert "./init.sh" in captured.out
        assert "npm install && npm run dev" in captured.out


class TestAgentIntegration:
    """Integration tests for agent functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch('agent.create_client')
    @patch('agent.create_session')
    @patch('agent.send_prompt')
    async def test_full_agent_workflow(self, mock_send_prompt, mock_create_session, mock_create_client, temp_dir):
        """Test full agent workflow from start to finish."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        mock_create_session.return_value = "test-session-id"
        
        # Mock response
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Task completed successfully"
        mock_response.content = [mock_content]
        mock_send_prompt.return_value = mock_response
        
        with patch('agent.copy_spec_to_project'), \
             patch('agent.get_initializer_prompt', return_value="Initialize project"), \
             patch('agent.print_progress_summary'):
            
            # Run agent session
            status, response = await run_agent_session(
                mock_client, "test-session", "Initialize project", temp_dir
            )
        
        # Verify workflow
        assert status == "continue"
        assert response == "Task completed successfully"
        mock_send_prompt.assert_called_once_with(
            mock_client, "test-session", "Initialize project"
        )


if __name__ == "__main__":
    # Run tests directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))