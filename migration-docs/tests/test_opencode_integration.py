#!/usr/bin/env python3
"""
OpenCode SDK Integration Tests
=============================

Comprehensive integration tests for the OpenCode Python SDK
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
from security import (
    bash_security_hook,
    extract_commands,
    validate_chmod_command,
    validate_init_script,
    get_opencode_permissions
)


class TestOpenCodeIntegration(unittest.TestCase):
    """Integration tests for OpenCode SDK"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_client_creation_with_anthropic_key(self):
        """Test client creation with Anthropic API key"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(self.test_dir, 'anthropic/claude-3-5-sonnet-20241022')
            
            self.assertIsNotNone(client)
            mock_opencode.assert_called_once_with(base_url='http://localhost:4096')

    async def test_client_creation_with_openrouter_key(self):
        """Test client creation with OpenRouter API key"""
        os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            client = create_client(self.test_dir, 'openrouter/anthropic/claude-3.5-sonnet')
            
            self.assertIsNotNone(client)
            mock_opencode.assert_called_once_with(base_url='http://localhost:4096')

    def test_client_creation_no_api_key(self):
        """Test client creation fails without API key"""
        # Remove all API keys
        for key in ['ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY', 'OPENCODE_API_KEY']:
            os.environ.pop(key, None)
        
        with patch('opencode_ai.AsyncOpencode'):
            client = create_client(self.test_dir)
            self.assertIsNone(client)

    async def test_opencode_settings_creation(self):
        """Test OpenCode settings file creation"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            create_client(self.test_dir)
            
            settings_file = self.test_dir / '.opencode_settings.json'
            self.assertTrue(settings_file.exists())
            
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            self.assertIn('model', settings)
            self.assertIn('permissions', settings)
            self.assertIn('security', settings)

    async def test_session_creation(self):
        """Test session creation"""
        mock_client = AsyncMock()
        mock_session = MagicMock()
        mock_session.id = 'test-session-id'
        mock_client.session.create.return_value = mock_session
        
        session_id = await create_session(mock_client, 'Test Session', self.test_dir)
        
        self.assertEqual(session_id, 'test-session-id')
        mock_client.session.create.assert_called_once()

    async def test_session_creation_failure(self):
        """Test session creation failure handling"""
        mock_client = AsyncMock()
        mock_client.session.create.side_effect = Exception('Session creation failed')
        
        with self.assertRaises(Exception):
            await create_session(mock_client, 'Test Session', self.test_dir)

    async def test_send_prompt_auto_model(self):
        """Test sending prompt with auto model selection"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Test response')]
        mock_client.session.chat.return_value = mock_response
        
        result = await send_prompt(mock_client, 'test-session', 'Hello, world!', 'auto')
        
        self.assertEqual(result, mock_response)
        mock_client.session.chat.assert_called_once_with(
            'test-session',
            'anthropic/claude-3.5-sonnet',
            'openrouter',
            [{'type': 'text', 'text': 'Hello, world!'}]
        )

    async def test_send_prompt_specific_model(self):
        """Test sending prompt with specific provider/model"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Test response')]
        mock_client.session.chat.return_value = mock_response
        
        result = await send_prompt(
            mock_client, 
            'test-session', 
            'Hello, world!', 
            'anthropic/claude-3-haiku-20240307'
        )
        
        self.assertEqual(result, mock_response)
        mock_client.session.chat.assert_called_once_with(
            'test-session',
            'claude-3-haiku-20240307',
            'anthropic',
            [{'type': 'text', 'text': 'Hello, world!'}]
        )

    async def test_send_prompt_failure(self):
        """Test prompt sending failure handling"""
        mock_client = AsyncMock()
        mock_client.session.chat.side_effect = Exception('Prompt failed')
        
        with self.assertRaises(Exception):
            await send_prompt(mock_client, 'test-session', 'Hello, world!')


class TestSecurityIntegration(unittest.TestCase):
    """Integration tests for security module"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extract_commands(self):
        """Test command extraction from various patterns"""
        test_cases = [
            ('ls -la', ['ls']),
            ('npm install && npm run build', ['npm', 'npm']),
            ('cat file.txt | grep pattern', ['cat', 'grep']),
            ('/usr/bin/node script.js', ['node']),
            ('VAR=value ls', ['ls']),
            ('git status || git init', ['git', 'git']),
        ]
        
        for command, expected in test_cases:
            with self.subTest(command=command):
                result = extract_commands(command)
                self.assertEqual(result, expected)

    def test_validate_chmod_allowed(self):
        """Test allowed chmod patterns"""
        allowed_commands = [
            'chmod +x init.sh',
            'chmod +x script.sh',
            'chmod u+x init.sh',
            'chmod a+x init.sh',
            'chmod ug+x init.sh',
            'chmod +x file1.sh file2.sh',
        ]
        
        for command in allowed_commands:
            with self.subTest(command=command):
                allowed, reason = validate_chmod_command(command)
                self.assertTrue(allowed, f"Command should be allowed: {command}")
                self.assertEqual(reason, 'Allowed chmod pattern')

    def test_validate_chmod_blocked(self):
        """Test blocked chmod patterns"""
        blocked_commands = [
            'chmod 777 init.sh',
            'chmod 755 init.sh',
            'chmod +w init.sh',
            'chmod +r init.sh',
            'chmod -x init.sh',
            'chmod -R +x dir/',
            'chmod --recursive +x dir/',
            'chmod +x',  # missing file
        ]
        
        for command in blocked_commands:
            with self.subTest(command=command):
                allowed, reason = validate_chmod_command(command)
                self.assertFalse(allowed, f"Command should be blocked: {command}")
                self.assertEqual(reason, 'Dangerous chmod pattern detected')

    def test_validate_init_script_allowed(self):
        """Test allowed init.sh patterns"""
        allowed_commands = [
            './init.sh',
            './init.sh arg1 arg2',
            '/path/to/init.sh',
            '../dir/init.sh',
        ]
        
        for command in allowed_commands:
            with self.subTest(command=command):
                allowed, reason = validate_init_script(command)
                self.assertTrue(allowed, f"Command should be allowed: {command}")
                self.assertEqual(reason, 'Allowed init.sh execution')

    def test_validate_init_script_blocked(self):
        """Test blocked init.sh patterns"""
        blocked_commands = [
            './setup.sh',
            './init.py',
            'bash init.sh',
            'sh init.sh',
            './malicious.sh',
            './init.sh; rm -rf /',
        ]
        
        for command in blocked_commands:
            with self.subTest(command=command):
                allowed, reason = validate_init_script(command)
                self.assertFalse(allowed, f"Command should be blocked: {command}")

    async def test_bash_security_hook_allowed_commands(self):
        """Test security hook allows safe commands"""
        safe_commands = [
            'ls -la',
            'cat README.md',
            'npm install',
            'git status',
            'chmod +x init.sh',
            './init.sh',
            'pkill node',
        ]
        
        for command in safe_commands:
            with self.subTest(command=command):
                result = await bash_security_hook({
                    'tool_name': 'Bash',
                    'tool_input': {'command': command}
                })
                self.assertEqual(result['decision'], 'allow')

    async def test_bash_security_hook_blocked_commands(self):
        """Test security hook blocks dangerous commands"""
        dangerous_commands = [
            'rm -rf /',
            'shutdown now',
            'chmod 777 file.sh',
            './malicious.sh',
            'pkill bash',
        ]
        
        for command in dangerous_commands:
            with self.subTest(command=command):
                result = await bash_security_hook({
                    'tool_name': 'Bash',
                    'tool_input': {'command': command}
                })
                self.assertEqual(result['decision'], 'block')
                self.assertIn('reason', result)

    def test_get_opencode_permissions(self):
        """Test filesystem permissions generation"""
        permissions = get_opencode_permissions(str(self.test_dir))
        
        self.assertIn(str(self.test_dir.resolve()), permissions['read'])
        self.assertIn(str(self.test_dir.resolve()), permissions['write'])
        self.assertIn('/dev/null', permissions['read'])
        self.assertIn('/tmp', permissions['write'])


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end workflow tests"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_full_workflow_simulation(self):
        """Test complete workflow simulation"""
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            # Mock client
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Mock session creation
            mock_session = MagicMock()
            mock_session.id = 'test-session-id'
            mock_client.session.create.return_value = mock_session
            
            # Mock prompt response
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='Workflow completed successfully')]
            mock_client.session.chat.return_value = mock_response
            
            # Step 1: Create client
            client = create_client(self.test_dir)
            self.assertIsNotNone(client)
            
            # Step 2: Create session
            session_id = await create_session(client, 'Test Workflow', self.test_dir)
            self.assertEqual(session_id, 'test-session-id')
            
            # Step 3: Send prompt
            result = await send_prompt(client, session_id, 'Execute workflow', 'auto')
            self.assertIsNotNone(result)
            
            # Verify settings file was created
            settings_file = self.test_dir / '.opencode_settings.json'
            self.assertTrue(settings_file.exists())


def run_async_test(coro):
    """Helper to run async tests"""
    return asyncio.run(coro)


# Make async methods callable from unittest
class TestOpenCodeIntegrationAsync(TestOpenCodeIntegration):
    """Async wrapper for integration tests"""
    
    def test_client_creation_with_anthropic_key(self):
        return run_async_test(super().test_client_creation_with_anthropic_key())
    
    def test_client_creation_with_openrouter_key(self):
        return run_async_test(super().test_client_creation_with_openrouter_key())
    
    def test_opencode_settings_creation(self):
        return run_async_test(super().test_opencode_settings_creation())
    
    def test_session_creation(self):
        return run_async_test(super().test_session_creation())
    
    def test_session_creation_failure(self):
        return run_async_test(super().test_session_creation_failure())
    
    def test_send_prompt_auto_model(self):
        return run_async_test(super().test_send_prompt_auto_model())
    
    def test_send_prompt_specific_model(self):
        return run_async_test(super().test_send_prompt_specific_model())
    
    def test_send_prompt_failure(self):
        return run_async_test(super().test_send_prompt_failure())


class TestSecurityIntegrationAsync(TestSecurityIntegration):
    """Async wrapper for security tests"""
    
    def test_bash_security_hook_allowed_commands(self):
        return run_async_test(super().test_bash_security_hook_allowed_commands())
    
    def test_bash_security_hook_blocked_commands(self):
        return run_async_test(super().test_bash_security_hook_blocked_commands())


class TestEndToEndWorkflowAsync(TestEndToEndWorkflow):
    """Async wrapper for end-to-end tests"""
    
    def test_full_workflow_simulation(self):
        return run_async_test(super().test_full_workflow_simulation())


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)