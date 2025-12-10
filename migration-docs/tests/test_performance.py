#!/usr/bin/env python3
"""
OpenCode SDK Performance Tests
==============================

Performance and load testing for the OpenCode SDK
"""

import asyncio
import time
import statistics
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

sys.path.append(str(Path(__file__).parent.parent))

from opencode_ai import AsyncOpencode
from client import create_client, create_session, send_prompt
from security import bash_security_hook


class TestPerformance(unittest.TestCase):
    """Performance tests for OpenCode SDK"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path('/tmp/performance-test')
        self.test_dir.mkdir(exist_ok=True)
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_concurrent_client_creation(self):
        """Test performance of concurrent client creation"""
        num_clients = 10
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            start_time = time.time()
            
            # Create clients concurrently
            tasks = [
                create_client(self.test_dir / f'client_{i}')
                for i in range(num_clients)
            ]
            clients = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # All clients should be created successfully
            self.assertEqual(len([c for c in clients if c is not None]), num_clients)
            
            # Performance assertion (should complete within reasonable time)
            self.assertLess(duration, 5.0, f"Client creation took too long: {duration}s")
            
            print(f"Created {num_clients} clients in {duration:.2f}s")
            print(f"Average time per client: {duration/num_clients:.3f}s")

    async def test_concurrent_session_creation(self):
        """Test performance of concurrent session creation"""
        num_sessions = 20
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Mock session creation
            mock_session = MagicMock()
            mock_session.id = 'test-session-id'
            mock_client.session.create.return_value = mock_session
            
            start_time = time.time()
            
            # Create sessions concurrently
            tasks = [
                create_session(mock_client, f'Test Session {i}', self.test_dir)
                for i in range(num_sessions)
            ]
            session_ids = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # All sessions should be created successfully
            self.assertEqual(len(session_ids), num_sessions)
            for session_id in session_ids:
                self.assertEqual(session_id, 'test-session-id')
            
            print(f"Created {num_sessions} sessions in {duration:.2f}s")
            print(f"Average time per session: {duration/num_sessions:.3f}s")

    async def test_concurrent_prompt_sending(self):
        """Test performance of concurrent prompt sending"""
        num_prompts = 50
        session_id = 'test-session-id'
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Mock prompt response
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='Test response')]
            mock_client.session.chat.return_value = mock_response
            
            start_time = time.time()
            
            # Send prompts concurrently
            tasks = [
                send_prompt(mock_client, session_id, f'Test prompt {i}', 'auto')
                for i in range(num_prompts)
            ]
            responses = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # All prompts should be sent successfully
            self.assertEqual(len(responses), num_prompts)
            
            print(f"Sent {num_prompts} prompts in {duration:.2f}s")
            print(f"Average time per prompt: {duration/num_prompts:.3f}s")
            print(f"Prompts per second: {num_prompts/duration:.1f}")

    async def test_security_validation_performance(self):
        """Test performance of security validation under load"""
        num_validations = 1000
        test_commands = [
            'ls -la',
            'npm install',
            'git status',
            'chmod +x init.sh',
            './init.sh',
            'pkill node',
        ]
        
        start_time = time.time()
        
        # Run security validations concurrently
        tasks = []
        for i in range(num_validations):
            command = test_commands[i % len(test_commands)]
            task = bash_security_hook({
                'tool_name': 'Bash',
                'tool_input': {'command': command}
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All validations should succeed
        allowed_count = sum(1 for r in results if r['decision'] == 'allow')
        self.assertEqual(allowed_count, num_validations)
        
        print(f"Validated {num_validations} commands in {duration:.2f}s")
        print(f"Average time per validation: {duration/num_validations*1000:.2f}ms")
        print(f"Validations per second: {num_validations/duration:.1f}")

    def test_memory_usage_stability(self):
        """Test memory usage stability over extended operations"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Run many operations
        for batch in range(10):
            async def run_batch():
                with patch('opencode_ai.AsyncOpencode') as mock_opencode:
                    mock_client = AsyncMock()
                    mock_opencode.return_value = mock_client
                    
                    mock_session = MagicMock()
                    mock_session.id = f'session-{batch}'
                    mock_client.session.create.return_value = mock_session
                    
                    mock_response = MagicMock()
                    mock_response.content = [MagicMock(text='Response')]
                    mock_client.session.chat.return_value = mock_response
                    
                    # Create client and session
                    client = create_client(self.test_dir / f'batch-{batch}')
                    if client:
                        session_id = await create_session(client, f'Batch {batch}', self.test_dir)
                        await send_prompt(client, session_id, f'Batch {batch} prompt', 'auto')
            
            asyncio.run(run_batch())
            gc.collect()  # Force garbage collection
            
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"Batch {batch + 1} memory usage: {current_memory:.1f} MB")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100, "Memory usage increased too much")


class TestLoadScenarios(unittest.TestCase):
    """Load testing scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path('/tmp/load-test')
        self.test_dir.mkdir(exist_ok=True)
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_high_volume_session_workflow(self):
        """Test high volume session creation and prompt sending"""
        num_workflows = 100
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            # Mock responses
            mock_session = MagicMock()
            mock_session.id = 'test-session-id'
            mock_client.session.create.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='Workflow response')]
            mock_client.session.chat.return_value = mock_response
            
            start_time = time.time()
            
            # Run complete workflows concurrently
            async def run_workflow(i):
                client = create_client(self.test_dir / f'workflow-{i}')
                if client:
                    session_id = await create_session(client, f'Workflow {i}', self.test_dir)
                    result = await send_prompt(client, session_id, f'Workflow {i} task', 'auto')
                    return result
                return None
            
            tasks = [run_workflow(i) for i in range(num_workflows)]
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            successful_workflows = len([r for r in results if r is not None])
            
            print(f"Completed {successful_workflows}/{num_workflows} workflows in {duration:.2f}s")
            print(f"Average time per workflow: {duration/num_workflows:.3f}s")
            print(f"Workflows per second: {successful_workflows/duration:.1f}")
            
            # Most workflows should succeed
            self.assertGreater(successful_workflows, num_workflows * 0.95)

    async def test_burst_load_handling(self):
        """Test handling of burst loads"""
        burst_size = 50
        num_bursts = 5
        
        with patch('opencode_ai.AsyncOpencode') as mock_opencode:
            mock_client = AsyncMock()
            mock_opencode.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='Burst response')]
            mock_client.session.chat.return_value = mock_response
            
            total_time = 0
            total_operations = 0
            
            for burst in range(num_bursts):
                print(f"Running burst {burst + 1}/{num_bursts}")
                
                burst_start = time.time()
                
                # Create burst of operations
                tasks = []
                for i in range(burst_size):
                    task = send_prompt(
                        mock_client, 
                        f'session-{burst}-{i}', 
                        f'Burst {burst} operation {i}', 
                        'auto'
                    )
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                
                burst_end = time.time()
                burst_duration = burst_end - burst_start
                
                print(f"  Burst {burst + 1}: {burst_size} operations in {burst_duration:.2f}s")
                
                total_time += burst_duration
                total_operations += burst_size
                
                # Small delay between bursts
                await asyncio.sleep(0.1)
            
            avg_time_per_operation = total_time / total_operations
            operations_per_second = total_operations / total_time
            
            print(f"Overall: {total_operations} operations in {total_time:.2f}s")
            print(f"Average time per operation: {avg_time_per_operation:.3f}s")
            print(f"Operations per second: {operations_per_second:.1f}")
            
            # Performance should remain consistent across bursts
            self.assertLess(avg_time_per_operation, 0.1, "Operations taking too long")

    async def test_stress_security_validation(self):
        """Stress test security validation with mixed commands"""
        num_commands = 2000
        
        # Mix of safe and dangerous commands
        safe_commands = [
            'ls -la', 'cat file.txt', 'npm install', 'git status',
            'chmod +x init.sh', './init.sh', 'pkill node'
        ]
        
        dangerous_commands = [
            'rm -rf /', 'shutdown now', 'chmod 777 file.sh',
            './malicious.sh', 'pkill bash'
        ]
        
        all_commands = safe_commands + dangerous_commands
        
        start_time = time.time()
        
        tasks = []
        for i in range(num_commands):
            command = all_commands[i % len(all_commands)]
            task = bash_security_hook({
                'tool_name': 'Bash',
                'tool_input': {'command': command}
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        allowed_count = sum(1 for r in results if r['decision'] == 'allow')
        blocked_count = sum(1 for r in results if r['decision'] == 'block')
        
        expected_safe = (num_commands // len(all_commands)) * len(safe_commands)
        expected_dangerous = (num_commands // len(all_commands)) * len(dangerous_commands)
        
        print(f"Validated {num_commands} commands in {duration:.2f}s")
        print(f"Allowed: {allowed_count}, Blocked: {blocked_count}")
        print(f"Average time per validation: {duration/num_commands*1000:.2f}ms")
        
        # Most safe commands should be allowed
        self.assertGreater(allowed_count, expected_safe * 0.9)
        # Most dangerous commands should be blocked
        self.assertGreater(blocked_count, expected_dangerous * 0.9)


def run_async_test(coro):
    """Helper to run async tests"""
    return asyncio.run(coro)


# Make async methods callable from unittest
class TestPerformanceAsync(TestPerformance):
    def test_concurrent_client_creation(self):
        return run_async_test(super().test_concurrent_client_creation())
    
    def test_concurrent_session_creation(self):
        return run_async_test(super().test_concurrent_session_creation())
    
    def test_concurrent_prompt_sending(self):
        return run_async_test(super().test_concurrent_prompt_sending())
    
    def test_security_validation_performance(self):
        return run_async_test(super().test_security_validation_performance())


class TestLoadScenariosAsync(TestLoadScenarios):
    def test_high_volume_session_workflow(self):
        return run_async_test(super().test_high_volume_session_workflow())
    
    def test_burst_load_handling(self):
        return run_async_test(super().test_burst_load_handling())
    
    def test_stress_security_validation(self):
        return run_async_test(super().test_stress_security_validation())


if __name__ == '__main__':
    # Run performance tests
    unittest.main(verbosity=2)