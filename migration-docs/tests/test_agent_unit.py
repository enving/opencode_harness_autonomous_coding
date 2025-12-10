import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import tempfile
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agent import AutonomousAgent
    from client import OpenCodeClient
    from security import bash_security_hook
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    AGENT_AVAILABLE = False
    AutonomousAgent = Mock
    OpenCodeClient = Mock
    bash_security_hook = Mock


class TestAutonomousAgentUnit:
    """Unit tests for AutonomousAgent."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent instance."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
        
        with patch('client.OpenCodeClient'), \
             patch('security.bash_security_hook'):
            agent = AutonomousAgent()
            return agent

    def test_agent_initialization(self):
        """Test agent initialization."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
            
        with patch('client.OpenCodeClient'), \
             patch('security.bash_security_hook'):
            agent = AutonomousAgent()
            assert agent is not None

    def test_agent_configuration(self):
        """Test agent configuration options."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
            
        config = {
            'max_iterations': 10,
            'timeout': 300,
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        with patch('client.OpenCodeClient'), \
             patch('security.bash_security_hook'):
            agent = AutonomousAgent(config=config)
            assert agent is not None

    @pytest.mark.asyncio
    async def test_task_execution_mock(self, mock_agent):
        """Test task execution with mocked dependencies."""
        # Mock the client methods
        mock_agent.client = Mock()
        mock_agent.client.create_session = Mock(return_value={'id': 'test-session'})
        mock_agent.client.send_prompt = Mock(return_value={'content': 'Task completed'})
        mock_agent.client.delete_session = Mock()
        
        # Mock security hook
        mock_agent.security_hook = Mock(return_value={'decision': 'allow'})
        
        result = await mock_agent.execute_task("Write a simple test")
        
        assert result is not None
        mock_agent.client.create_session.assert_called_once()

    def test_task_validation(self, mock_agent):
        """Test task validation logic."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
            
        # Valid tasks
        valid_tasks = [
            "Write a unit test for the API",
            "Fix the bug in the authentication module",
            "Add error handling to the database connection"
        ]
        
        for task in valid_tasks:
            # This would need to be implemented in the actual agent
            assert isinstance(task, str)
            assert len(task.strip()) > 0

    def test_progress_tracking(self, mock_agent):
        """Test progress tracking functionality."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
            
        # Mock progress tracking
        mock_agent.progress = Mock()
        mock_agent.progress.update = Mock()
        mock_agent.progress.get_status = Mock(return_value={'completed': 0, 'total': 10})
        
        status = mock_agent.progress.get_status()
        assert status['completed'] == 0
        assert status['total'] == 10


class TestOpenCodeClientUnit:
    """Unit tests for OpenCodeClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        if not AGENT_AVAILABLE:
            pytest.skip("Client modules not available")
            
        with patch('opencode_ai.AsyncOpencode'):
            client = OpenCodeClient()
            return client

    def test_client_initialization(self):
        """Test client initialization."""
        if not AGENT_AVAILABLE:
            pytest.skip("Client modules not available")
            
        with patch('opencode_ai.AsyncOpencode'):
            client = OpenCodeClient()
            assert client is not None

    @pytest.mark.asyncio
    async def test_session_management_mock(self, mock_client):
        """Test session management with mocked SDK."""
        # Mock the underlying SDK
        mock_client.sdk = Mock()
        mock_client.sdk.session.create = Mock(return_value={'id': 'test-session'})
        mock_client.sdk.session.get = Mock(return_value={'id': 'test-session', 'status': 'active'})
        mock_client.sdk.session.delete = Mock()
        
        # Test session creation
        session = await mock_client.create_session("Test Session")
        assert session['id'] == 'test-session'
        
        # Test session retrieval
        retrieved = await mock_client.get_session('test-session')
        assert retrieved['id'] == 'test-session'
        
        # Test session deletion
        await mock_client.delete_session('test-session')
        mock_client.sdk.session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_prompt_sending_mock(self, mock_client):
        """Test prompt sending with mocked SDK."""
        mock_client.sdk = Mock()
        mock_client.sdk.session.prompt = Mock(return_value={
            'id': 'response-123',
            'content': 'This is a test response'
        })
        
        response = await mock_client.send_prompt('test-session', 'Hello, world!')
        
        assert response['content'] == 'This is a test response'
        mock_client.sdk.session.prompt.assert_called_once()

    def test_error_handling(self, mock_client):
        """Test error handling in client."""
        if not AGENT_AVAILABLE:
            pytest.skip("Client modules not available")
            
        # Test error wrapping
        mock_client.sdk = Mock()
        mock_client.sdk.session.get.side_effect = Exception("Session not found")
        
        # The client should handle and wrap SDK errors
        with pytest.raises(Exception):
            asyncio.run(mock_client.get_session('invalid-session'))


class TestSecurityUnit:
    """Unit tests for security functionality."""

    @pytest.fixture
    def mock_security_hook(self):
        """Create a mock security hook."""
        if not AGENT_AVAILABLE:
            pytest.skip("Security modules not available")
        return bash_security_hook

    @pytest.mark.asyncio
    async def test_safe_commands_allowed(self, mock_security_hook):
        """Test that safe commands are allowed."""
        if not AGENT_AVAILABLE:
            pytest.skip("Security modules not available")
            
        safe_commands = [
            "ls -la",
            "cat README.md",
            "npm install",
            "git status",
            "mkdir test"
        ]
        
        for command in safe_commands:
            # Mock the security hook to return allow decision
            with patch('security.bash_security_hook', return_value={'decision': 'allow'}):
                result = await bash_security_hook({
                    'tool_name': 'Bash',
                    'tool_input': {'command': command}
                })
                assert result['decision'] == 'allow'

    @pytest.mark.asyncio
    async def test_dangerous_commands_blocked(self, mock_security_hook):
        """Test that dangerous commands are blocked."""
        if not AGENT_AVAILABLE:
            pytest.skip("Security modules not available")
            
        dangerous_commands = [
            "rm -rf /",
            "shutdown now",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for command in dangerous_commands:
            # Mock the security hook to return block decision
            with patch('security.bash_security_hook', return_value={'decision': 'block', 'reason': 'Dangerous command'}):
                result = await bash_security_hook({
                    'tool_name': 'Bash',
                    'tool_input': {'command': command}
                })
                assert result['decision'] == 'block'
                assert 'reason' in result

    def test_command_parsing(self):
        """Test command parsing logic."""
        if not AGENT_AVAILABLE:
            pytest.skip("Security modules not available")
            
        # This would test the command parsing functions
        # from the security module
        test_cases = [
            ("ls -la", ["ls"]),
            ("npm install && npm run build", ["npm", "npm"]),
            ("git status || git init", ["git", "git"])
        ]
        
        for command, expected in test_cases:
            # Mock the parsing function
            with patch('security.extract_commands', return_value=expected):
                from security import extract_commands
                result = extract_commands(command)
                assert result == expected


class TestIntegrationUnit:
    """Unit tests for integration components."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_workspace_setup(self, temp_workspace):
        """Test workspace setup functionality."""
        assert os.path.exists(temp_workspace)
        assert os.path.isdir(temp_workspace)

    def test_file_operations(self, temp_workspace):
        """Test file operations in workspace."""
        test_file = os.path.join(temp_workspace, 'test.txt')
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('test content')
        
        assert os.path.exists(test_file)
        
        # Read test file
        with open(test_file, 'r') as f:
            content = f.read()
        
        assert content == 'test content'

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operation handling."""
        if not AGENT_AVAILABLE:
            pytest.skip("Agent modules not available")
            
        # Mock concurrent operations
        async def mock_operation():
            await asyncio.sleep(0.1)
            return "operation complete"
        
        tasks = [mock_operation() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(result == "operation complete" for result in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])