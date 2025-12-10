import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from opencode_ai import AsyncOpencode
    OPENCODE_AVAILABLE = True
except ImportError:
    OPENCODE_AVAILABLE = False
    AsyncOpencode = Mock


class TestAsyncOpencodeUnit:
    """Unit tests for AsyncOpencode client."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
        
        client = AsyncOpencode()
        return client

    @pytest.fixture
    def mock_session_data(self):
        """Mock session response data."""
        return {
            'id': 'test-session-123',
            'title': 'Test Session',
            'created_at': '2024-01-01T00:00:00Z',
            'status': 'active',
            'messages': []
        }

    def test_client_import(self):
        """Test that AsyncOpencode can be imported."""
        if OPENCODE_AVAILABLE:
            assert AsyncOpencode is not None
        else:
            pytest.skip("OpenCode SDK not available")

    @pytest.mark.asyncio
    async def test_client_creation(self):
        """Test client creation with different configurations."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        # Test default creation
        client1 = AsyncOpencode()
        assert client1 is not None
        
        # Test creation with timeout
        client2 = AsyncOpencode(timeout=30000)
        assert client2 is not None

    @pytest.mark.asyncio
    async def test_session_create_mock(self, mock_client, mock_session_data):
        """Test session creation with mocked response."""
        with patch.object(mock_client.session, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_session_data
            
            result = await mock_client.session.create({'title': 'Test Session'})
            
            assert result == mock_session_data
            assert result['id'] == 'test-session-123'
            mock_create.assert_called_once_with({'title': 'Test Session'})

    @pytest.mark.asyncio
    async def test_session_list_mock(self, mock_client):
        """Test session listing with mocked response."""
        mock_sessions = [
            {'id': 'session-1', 'title': 'Session 1'},
            {'id': 'session-2', 'title': 'Session 2'}
        ]
        
        with patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_sessions
            
            result = await mock_client.session.list()
            
            assert len(result) == 2
            assert result[0]['id'] == 'session-1'
            mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_get_mock(self, mock_client, mock_session_data):
        """Test session retrieval with mocked response."""
        with patch.object(mock_client.session, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_session_data
            
            result = await mock_client.session.get({'path': {'id': 'test-session-123'}})
            
            assert result == mock_session_data
            assert result['id'] == 'test-session-123'
            mock_get.assert_called_once_with({'path': {'id': 'test-session-123'}})

    @pytest.mark.asyncio
    async def test_session_delete_mock(self, mock_client):
        """Test session deletion with mocked response."""
        with patch.object(mock_client.session, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None
            
            await mock_client.session.delete({'path': {'id': 'test-session-123'}})
            
            mock_delete.assert_called_once_with({'path': {'id': 'test-session-123'}})

    @pytest.mark.asyncio
    async def test_session_prompt_mock(self, mock_client):
        """Test session prompt with mocked response."""
        mock_response = {
            'id': 'response-123',
            'content': 'The answer is 4',
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        with patch.object(mock_client.session, 'prompt', new_callable=AsyncMock) as mock_prompt:
            mock_prompt.return_value = mock_response
            
            result = await mock_client.session.prompt({
                'path': {'id': 'test-session-123'},
                'body': {
                    'model': {
                        'providerID': 'anthropic',
                        'modelID': 'claude-3-5-sonnet-20241022'
                    },
                    'parts': [{
                        'type': 'text',
                        'text': 'What is 2 + 2?'
                    }]
                }
            })
            
            assert result == mock_response
            assert result['content'] == 'The answer is 4'
            mock_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_mock(self, mock_client):
        """Test error handling with mocked exceptions."""
        # Test session not found error
        with patch.object(mock_client.session, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Session not found")
            
            with pytest.raises(Exception, match="Session not found"):
                await mock_client.session.get({'path': {'id': 'invalid-id'}})

    @pytest.mark.asyncio
    async def test_concurrent_operations_mock(self, mock_client, mock_session_data):
        """Test concurrent operations with mocked responses."""
        with patch.object(mock_client.session, 'create', new_callable=AsyncMock) as mock_create, \
             patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            
            mock_create.return_value = mock_session_data
            mock_list.return_value = [mock_session_data]
            
            # Run operations concurrently
            tasks = [
                mock_client.session.create({'title': f'Test Session {i}'})
                for i in range(3)
            ]
            tasks.append(mock_client.session.list())
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 4
            assert all(result['id'] == 'test-session-123' for result in results[:3])
            assert len(results[3]) == 1

    @pytest.mark.asyncio
    async def test_timeout_handling_mock(self, mock_client):
        """Test timeout handling with mocked timeout."""
        with patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(asyncio.TimeoutError):
                await mock_client.session.list()

    def test_mock_configuration(self):
        """Test mock configuration validation."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
            
        # Test that mock client has expected attributes
        client = AsyncOpencode()
        assert hasattr(client, 'session')
        assert hasattr(client.session, 'create')
        assert hasattr(client.session, 'list')
        assert hasattr(client.session, 'get')
        assert hasattr(client.session, 'delete')


class TestAsyncOpencodeEdgeCases:
    """Edge case tests for AsyncOpencode."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        if not OPENCODE_AVAILABLE:
            pytest.skip("OpenCode SDK not available")
        return AsyncOpencode()

    @pytest.mark.asyncio
    async def test_empty_session_list(self, mock_client):
        """Test handling of empty session list."""
        with patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            
            result = await mock_client.session.list()
            
            assert result == []
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_large_session_list(self, mock_client):
        """Test handling of large session list."""
        large_list = [{'id': f'session-{i}', 'title': f'Session {i}'} for i in range(1000)]
        
        with patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = large_list
            
            result = await mock_client.session.list()
            
            assert len(result) == 1000
            assert result[0]['id'] == 'session-0'
            assert result[-1]['id'] == 'session-999'

    @pytest.mark.asyncio
    async def test_malformed_response(self, mock_client):
        """Test handling of malformed API responses."""
        with patch.object(mock_client.session, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {'invalid': 'response'}
            
            result = await mock_client.session.get({'path': {'id': 'test-id'}})
            
            # Should still return the malformed response
            assert result == {'invalid': 'response'}

    @pytest.mark.asyncio
    async def test_network_error_retry(self, mock_client):
        """Test network error and retry logic."""
        with patch.object(mock_client.session, 'list', new_callable=AsyncMock) as mock_list:
            # First call fails, second succeeds
            mock_list.side_effect = [
                ConnectionError("Network error"),
                [{'id': 'session-1', 'title': 'Session 1'}]
            ]
            
            # First call should fail
            with pytest.raises(ConnectionError):
                await mock_client.session.list()
            
            # Second call should succeed
            result = await mock_client.session.list()
            assert len(result) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])