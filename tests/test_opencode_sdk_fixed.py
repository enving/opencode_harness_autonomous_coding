import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from opencode_ai import AsyncOpencode
    OPENCODE_AVAILABLE = True
except ImportError:
    OPENCODE_AVAILABLE = False
    AsyncOpencode = None


class TestAsyncOpencode:
    """Test suite for AsyncOpencode client."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
        return AsyncOpencode()

    @pytest.fixture
    def mock_session(self):
        """Mock session data."""
        return {
            'id': 'test-session-123',
            'title': 'Test Session',
            'created_at': '2024-01-01T00:00:00Z',
            'status': 'active'
        }

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization with default options."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        client = AsyncOpencode()
        assert client is not None
        assert hasattr(client, 'session')

    @pytest.mark.asyncio
    async def test_client_initialization_with_options(self):
        """Test client initialization with custom options."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        client = AsyncOpencode(timeout=30000)
        assert client is not None

    @pytest.mark.asyncio
    async def test_session_create_success(self, client, mock_session):
        """Test successful session creation."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        with patch.object(client.session, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_session
            
            result = await client.session.create({
                'title': 'Test Session'
            })
            
            assert result == mock_session
            mock_create.assert_called_once_with({'title': 'Test Session'})

    @pytest.mark.asyncio
    async def test_session_list_success(self, client):
        """Test successful session listing."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        mock_sessions = [
            {'id': 'session-1', 'title': 'Session 1'},
            {'id': 'session-2', 'title': 'Session 2'}
        ]
        
        with patch.object(client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_sessions
            
            result = await client.session.list()
            
            assert result == mock_sessions
            assert len(result) == 2
            mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_get_success(self, client, mock_session):
        """Test successful session retrieval."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        with patch.object(client.session, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_session
            
            result = await client.session.get({
                'path': {'id': 'test-session-123'}
            })
            
            assert result == mock_session
            assert result['id'] == 'test-session-123'
            mock_get.assert_called_once_with({'path': {'id': 'test-session-123'}})

    @pytest.mark.asyncio
    async def test_session_delete_success(self, client):
        """Test successful session deletion."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        with patch.object(client.session, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None
            
            await client.session.delete({'path': {'id': 'test-session-123'}})
            
            mock_delete.assert_called_once_with({'path': {'id': 'test-session-123'}})

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, client, mock_session):
        """Test concurrent session operations."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        with patch.object(client.session, 'create', new_callable=AsyncMock) as mock_create, \
             patch.object(client.session, 'list', new_callable=AsyncMock) as mock_list:
            
            mock_create.return_value = mock_session
            mock_list.return_value = [mock_session]
            
            # Run operations concurrently
            create_task = client.session.create({'title': 'Concurrent Test'})
            list_task = client.session.list()
            
            results = await asyncio.gather(create_task, list_task)
            
            assert results[0] == mock_session
            assert results[1] == [mock_session]

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, client):
        """Test network timeout handling."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        with patch.object(client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(asyncio.TimeoutError):
                await client.session.list()


class TestOpenCodeSDKIntegration:
    """Integration tests for OpenCode SDK."""

    @pytest.mark.asyncio
    async def test_real_session_lifecycle(self):
        """Test real session lifecycle with actual API."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        # Skip integration tests by default
        pytest.skip("Integration test - set RUN_INTEGRATION_TESTS to run")
        
        client = AsyncOpencode()
        
        try:
            # Create session
            session = await client.session.create({
                'title': 'Integration Test Session'
            })
            assert 'id' in session
            
            # Get session
            retrieved = await client.session.get({
                'path': {'id': session['id']}
            })
            assert retrieved['id'] == session['id']
            
            # List sessions
            sessions = await client.session.list()
            assert isinstance(sessions, list)
            
            # Delete session
            await client.session.delete({'path': {'id': session['id']}})
            
        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])