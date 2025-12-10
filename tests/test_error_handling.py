#!/usr/bin/env python3
"""
OpenCode SDK Error Handling Tests
=================================

Tests for error handling and edge cases in the OpenCode SDK
"""

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

sys.path.append(str(Path(__file__).parent.parent))

from opencode_ai import AsyncOpencode
from client import create_client, create_session, send_prompt
from security import bash_security_hook, extract_commands, validate_chmod_command


class TestErrorHandling(unittest.TestCase):
    """Error handling tests for OpenCode SDK"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_client_creation_network_error(self):
        """Test client creation with network error"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_opencode.side_effect = ConnectionError('Network unreachable')
            
            with self.assertRaises(ConnectionError):
                create_client(self.test_dir)

    async def test_client_creation_invalid_api_key(self):
        """Test client creation with invalid API key"""
        os.environ['ANTHROPIC_API_KEY'] = 'invalid-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_opencode.side_effect = Exception('Invalid API key')
            
            with self.assertRaises(Exception):
                create_client(self.test_dir)

    async def test_session_creation_timeout(self):
        """Test session creation with timeout"""
        mock_client = AsyncMock()
        mock_client.session.create.side_effect = asyncio.TimeoutError('Request timeout')
        
        with self.assertRaises(asyncio.TimeoutError):
            await create_session(mock_client, 'Test Session', self.test_dir)

    async def test_session_creation_rate_limit(self):
        """Test session creation with rate limiting"""
        mock_client = AsyncMock()
        mock_client.session.create.side_effect = Exception('Rate limit exceeded')
        
        with self.assertRaises(Exception):
            await create_session(mock_client, 'Test Session', self.test_dir)

    async def test_prompt_sending_session_not_found(self):
        """Test prompt sending to non-existent session"""
        mock_client = AsyncMock()
        mock_client.session.chat.side_effect = Exception('Session not found')
        
        with self.assertRaises(Exception):
            await send_prompt(mock_client, 'invalid-session', 'Test message')

    async def test_prompt_sending_message_too_large(self):
        """Test prompt sending with oversized message"""
        mock_client = AsyncMock()
        mock_client.session.chat.side_effect = Exception('Message too large')
        
        large_message = 'x' * (10 * 1024 * 1024)  # 10MB message
        
        with self.assertRaises(Exception):
            await send_prompt(mock_client, 'test-session', large_message)

    async def test_prompt_sending_model_unavailable(self):
        """Test prompt sending with unavailable model"""
        mock_client = AsyncMock()
        mock_client.session.chat.side_effect = Exception('Model not available')
        
        with self.assertRaises(Exception):
            await send_prompt(mock_client, 'test-session', 'Test message', 'unavailable/model')

    async def test_filesystem_permission_error(self):
        """Test handling of filesystem permission errors"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Create a directory with no write permissions
        restricted_dir = self.test_dir / 'restricted'
        restricted_dir.mkdir()
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Mock file operations to raise permission error
            with patch('builtins.open', side_effect=PermissionError('Permission denied')):
                with patch('pathlib.Path.mkdir', side_effect=PermissionError('Permission denied')):
                    # Should handle permission error gracefully
                    result = create_client(restricted_dir)
                    # The function should still return a client, but log the error
                    self.assertIsNotNone(result)

    async def test_malformed_settings_file(self):
        """Test handling of malformed OpenCode settings file"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Create malformed settings file
        settings_file = self.test_dir / '.opencode_settings.json'
        with open(settings_file, 'w') as f:
            f.write('invalid json content')
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Should handle malformed file gracefully
            client = create_client(self.test_dir)
            self.assertIsNotNone(client)

    async def test_concurrent_session_conflicts(self):
        """Test handling of concurrent session creation conflicts"""
        mock_client = AsyncMock()
        
        # Simulate session ID conflict
        mock_client.session.create.side_effect = [
            Exception('Session ID conflict'),
            MagicMock(id='unique-session-id')
        ]
        
        # First call should fail, second should succeed
        with self.assertRaises(Exception):
            await create_session(mock_client, 'Test Session', self.test_dir)
        
        # Reset side effect for successful creation
        mock_client.session.create.side_effect = None
        mock_client.session.create.return_value = MagicMock(id='unique-session-id')
        
        session_id = await create_session(mock_client, 'Test Session', self.test_dir)
        self.assertEqual(session_id, 'unique-session-id')


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for OpenCode SDK"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_empty_project_directory(self):
        """Test operations with empty project directory"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(self.test_dir)
            self.assertIsNotNone(client)

    def test_very_long_project_path(self):
        """Test with very long project directory path"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Create a very long path
        long_path = self.test_dir
        for i in range(10):
            long_path = long_path / f'very_long_directory_name_{i}'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(long_path)
            self.assertIsNotNone(client)

    def test_special_characters_in_project_path(self):
        """Test with special characters in project path"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        special_path = self.test_dir / 'project with spaces & symbols!@#$%'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(special_path)
            self.assertIsNotNone(client)

    def test_unicode_in_project_path(self):
        """Test with Unicode characters in project path"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        unicode_path = self.test_dir / '项目目录' / 'тест' / '🚀'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(unicode_path)
            self.assertIsNotNone(client)

    async def test_empty_prompt_message(self):
        """Test sending empty prompt message"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_client.session.chat.return_value = mock_response
        
        result = await send_prompt(mock_client, 'test-session', '')
        self.assertIsNotNone(result)

    async def test_whitespace_only_prompt(self):
        """Test sending whitespace-only prompt"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='')]
        mock_client.session.chat.return_value = mock_response
        
        result = await send_prompt(mock_client, 'test-session', '   \n\t   ')
        self.assertIsNotNone(result)

    async def test_very_long_prompt(self):
        """Test sending very long prompt"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Response to long prompt')]
        mock_client.session.chat.return_value = mock_response
        
        long_prompt = 'Test message ' * 10000  # Very long message
        
        result = await send_prompt(mock_client, 'test-session', long_prompt)
        self.assertIsNotNone(result)

    async def test_prompt_with_special_characters(self):
        """Test prompt with special characters"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Response')]
        mock_client.session.chat.return_value = mock_response
        
        special_prompt = 'Test with émojis 🚀 and spëcial chars & symbols!@#$%^&*()'
        
        result = await send_prompt(mock_client, 'test-session', special_prompt)
        self.assertIsNotNone(result)

    async def test_prompt_with_json_content(self):
        """Test prompt with JSON content"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='JSON processed')]
        mock_client.session.chat.return_value = mock_response
        
        json_prompt = json.dumps({
            'action': 'test',
            'data': {'key': 'value', 'nested': {'array': [1, 2, 3]}}
        })
        
        result = await send_prompt(mock_client, 'test-session', json_prompt)
        self.assertIsNotNone(result)

    def test_security_edge_cases(self):
        """Test security validation edge cases"""
        async def test_edge_case(command, expected_decision):
            result = await bash_security_hook({
                'tool_name': 'Bash',
                'tool_input': {'command': command}
            })
            self.assertEqual(result['decision'], expected_decision)
        
        # Test empty command
        asyncio.run(test_edge_case('', 'allow'))
        
        # Test whitespace-only command
        asyncio.run(test_edge_case('   \n\t   ', 'allow'))
        
        # Test very long command
        long_command = 'ls ' + 'a' * 10000
        asyncio.run(test_edge_case(long_command, 'allow'))
        
        # Test command with null bytes
        asyncio.run(test_edge_case('ls\x00la', 'block'))

    def test_command_extraction_edge_cases(self):
        """Test command extraction edge cases"""
        # Empty string
        self.assertEqual(extract_commands(''), [])
        
        # Whitespace only
        self.assertEqual(extract_commands('   \n\t   '), [])
        
        # Multiple separators
        self.assertEqual(extract_commands('cmd1 && cmd2 || cmd3; cmd4 | cmd5'), 
                        ['cmd1', 'cmd2', 'cmd3', 'cmd4', 'cmd5'])
        
        # Complex command with quotes
        self.assertEqual(extract_commands('echo "hello && world" && ls'), 
                        ['echo', 'ls'])
        
        # Command with environment variables
        self.assertEqual(extract_commands('VAR1=val1 VAR2=val2 command arg1 arg2'), 
                        ['command'])

    def test_chmod_validation_edge_cases(self):
        """Test chmod validation edge cases"""
        # Empty chmod command
        allowed, reason = validate_chmod_command('chmod')
        self.assertFalse(allowed)
        
        # chmod with no arguments
        allowed, reason = validate_chmod_command('chmod ')
        self.assertFalse(allowed)
        
        # chmod with many files
        allowed, reason = validate_chmod_command('chmod +x file1.sh file2.sh file3.sh')
        self.assertTrue(allowed)
        
        # chmod with relative paths
        allowed, reason = validate_chmod_command('chmod +x ../script.sh')
        self.assertTrue(allowed)
        
        # chmod with absolute paths
        allowed, reason = validate_chmod_command('chmod +x /absolute/path/script.sh')
        self.assertTrue(allowed)

    async def test_concurrent_operations_edge_cases(self):
        """Test concurrent operations edge cases"""
        mock_client = AsyncMock()
        
        # Test concurrent operations on same session
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Response')]
        mock_client.session.chat.return_value = mock_response
        
        # Send multiple prompts to same session concurrently
        tasks = [
            send_prompt(mock_client, 'same-session', f'Message {i}', 'auto')
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        self.assertEqual(len(results), 10)
        
        # Verify all calls were made
        self.assertEqual(mock_client.session.chat.call_count, 10)

    def test_environment_variable_edge_cases(self):
        """Test environment variable edge cases"""
        # Test with empty API key
        os.environ['ANTHROPIC_API_KEY'] = ''
        
        with patch('opencode_ai.AsyncOpencode'):
            client = create_client(self.test_dir)
            self.assertIsNone(client)
        
        # Test with whitespace-only API key
        os.environ['ANTHROPIC_API_KEY'] = '   \n\t   '
        
        with patch('opencode_ai.AsyncOpencode'):
            client = create_client(self.test_dir)
            self.assertIsNone(client)
        
        # Test with multiple API keys (should prioritize)
        os.environ['ANTHROPIC_API_KEY'] = 'anthropic-key'
        os.environ['OPENROUTER_API_KEY'] = 'openrouter-key'
        os.environ['OPENCODE_API_KEY'] = 'opencode-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(self.test_dir)
            self.assertIsNotNone(client)


def run_async_test(coro):
    """Helper to run async tests"""
    return asyncio.run(coro)


# Make async methods callable from unittest
class TestErrorHandlingAsync(TestErrorHandling):
    def test_client_creation_network_error(self):
        return run_async_test(super().test_client_creation_network_error())
    
    def test_client_creation_invalid_api_key(self):
        return run_async_test(super().test_client_creation_invalid_api_key())
    
    def test_session_creation_timeout(self):
        return run_async_test(super().test_session_creation_timeout())
    
    def test_session_creation_rate_limit(self):
        return run_async_test(super().test_session_creation_rate_limit())
    
    def test_prompt_sending_session_not_found(self):
        return run_async_test(super().test_prompt_sending_session_not_found())
    
    def test_prompt_sending_message_too_large(self):
        return run_async_test(super().test_prompt_sending_message_too_large())
    
    def test_prompt_sending_model_unavailable(self):
        return run_async_test(super().test_prompt_sending_model_unavailable())
    
    def test_filesystem_permission_error(self):
        return run_async_test(super().test_filesystem_permission_error())
    
    def test_malformed_settings_file(self):
        return run_async_test(super().test_malformed_settings_file())
    
    def test_concurrent_session_conflicts(self):
        return run_async_test(super().test_concurrent_session_conflicts())


class TestEdgeCasesAsync(TestEdgeCases):
    def test_empty_prompt_message(self):
        return run_async_test(super().test_empty_prompt_message())
    
    def test_whitespace_only_prompt(self):
        return run_async_test(super().test_whitespace_only_prompt())
    
    def test_very_long_prompt(self):
        return run_async_test(super().test_very_long_prompt())
    
    def test_prompt_with_special_characters(self):
        return run_async_test(super().test_prompt_with_special_characters())
    
    def test_prompt_with_json_content(self):
        return run_async_test(super().test_prompt_with_json_content())
    
    def test_security_edge_cases(self):
        return run_async_test(super().test_security_edge_cases())
    
    def test_concurrent_operations_edge_cases(self):
        return run_async_test(super().test_concurrent_operations_edge_cases())


if __name__ == '__main__':
    unittest.main(verbosity=2)