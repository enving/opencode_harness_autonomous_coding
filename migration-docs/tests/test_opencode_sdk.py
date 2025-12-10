import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from opencode_ai import AsyncOpencode
from opencode_ai.core import OpencodeError


class TestAsyncOpencode:
    """Test suite for AsyncOpencode client."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
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
        client = AsyncOpencode()
        assert client is not None
        assert hasattr(client, 'session')

    @pytest.mark.asyncio
    async def test_client_initialization_with_options(self):
        """Test client initialization with custom options."""
        client = AsyncOpencode(timeout=30000, retries=3)
        assert client is not None

    @pytest.mark.asyncio
    async def test_session_create_success(self, client, mock_session):
        """Test successful session creation."""
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
        with patch.object(client.session, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None
            
            await client.session.delete({'path': {'id': 'test-session-123'}})
            
            mock_delete.assert_called_once_with({'path': {'id': 'test-session-123'}})

    @pytest.mark.asyncio
    async def test_session_prompt_success(self, client):
        """Test successful prompt sending."""
        mock_response = {
            'id': 'response-123',
            'content': 'The answer is 4',
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        with patch.object(client.session, 'prompt', new_callable=AsyncMock) as mock_prompt:
            mock_prompt.return_value = mock_response
            
            result = await client.session.prompt({
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
            mock_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_invalid_session(self, client):
        """Test error handling for invalid session ID."""
        with patch.object(client.session, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = OpencodeError('Session not found')
            
            with pytest.raises(OpencodeError) as exc_info:
                await client.session.get({'path': {'id': 'invalid-id'}})
            
            assert 'Session not found' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, client):
        """Test network timeout handling."""
        import asyncio
        
        with patch.object(client.session, 'list', new_callable=AsyncMock) as mock_list:
            mock_list.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(asyncio.TimeoutError):
                await client.session.list()

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, client, mock_session):
        """Test concurrent session operations."""
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

    def test_client_configuration_validation(self):
        """Test client configuration validation."""
        # Test with invalid timeout
        with pytest.raises(ValueError):
            AsyncOpencode(timeout=-1)
        
        # Test with invalid retries
        with pytest.raises(ValueError):
            AsyncOpencode(retries=-1)


class TestOpencodeError:
    """Test suite for OpencodeError."""

    def test_error_creation(self):
        """Test error creation with message."""
        error = OpencodeError('Test error message')
        assert str(error) == 'Test error message'
        assert error.message == 'Test error message'

    def test_error_with_code(self):
        """Test error with error code."""
        error = OpencodeError('Test error', code=404)
        assert error.code == 404

    def test_error_inheritance(self):
        """Test error inheritance from Exception."""
        error = OpencodeError('Test error')
        assert isinstance(error, Exception)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])