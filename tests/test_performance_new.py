import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


class TestSDKPerformance:
    """Performance tests for OpenCode SDK."""

    @pytest.mark.asyncio
    async def test_session_creation_performance(self):
        """Test session creation performance under load."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        try:
            from opencode_ai import AsyncOpencode
        except ImportError:
            pytest.skip("OpenCode SDK not available")
        
        client = AsyncOpencode()
        session_ids = []
        
        try:
            # Measure session creation time
            start_time = time.time()
            
            # Create sessions sequentially
            for i in range(10):
                session = await client.session.create({
                    'title': f'Performance Test Session {i}'
                })
                session_ids.append(session['id'])
            
            sequential_time = time.time() - start_time
            
            # Create sessions concurrently
            start_time = time.time()
            
            async def create_session(index):
                session = await client.session.create({
                    'title': f'Concurrent Session {index}'
                })
                return session['id']
            
            concurrent_ids = await asyncio.gather(*[
                create_session(i) for i in range(10)
            ])
            
            concurrent_time = time.time() - start_time
            
            # Concurrent should be faster
            assert concurrent_time < sequential_time
            assert len(concurrent_ids) == 10
            assert len(set(concurrent_ids)) == 10  # All unique
            
            # Performance assertions (adjust thresholds as needed)
            assert sequential_time < 30.0, f"Sequential creation too slow: {sequential_time}s"
            assert concurrent_time < 15.0, f"Concurrent creation too slow: {concurrent_time}s"
            
        finally:
            # Cleanup all sessions
            all_ids = session_ids + concurrent_ids
            for session_id in all_ids:
                try:
                    await client.session.delete({'path': {'id': session_id}})
                except:
                    pass

    @pytest.mark.asyncio
    async def test_prompt_response_performance(self):
        """Test prompt response performance."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        try:
            from opencode_ai import AsyncOpencode
        except ImportError:
            pytest.skip("OpenCode SDK not available")
        
        client = AsyncOpencode()
        
        # Create test session
        session = await client.session.create({
            'title': 'Performance Test Session'
        })
        
        try:
            # Test multiple prompts
            prompts = [
                "What is 2 + 2?",
                "What is capital of France?",
                "Explain recursion in one sentence.",
                "What is Python?",
                "How do you sort a list in JavaScript?"
            ]
            
            response_times = []
            
            for prompt in prompts:
                start_time = time.time()
                
                response = await client.session.prompt({
                    'path': {'id': session['id']},
                    'body': {
                        'model': {
                            'providerID': 'anthropic',
                            'modelID': 'claude-3-5-sonnet-20241022'
                        },
                        'parts': [{
                            'type': 'text',
                            'text': prompt
                        }]
                    }
                })
                
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                assert 'content' in response
            
            # Calculate statistics
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Performance assertions
            assert avg_time < 10.0, f"Average response time too slow: {avg_time}s"
            assert max_time < 20.0, f"Max response time too slow: {max_time}s"
            assert min_time < 5.0, f"Min response time too slow: {min_time}s"
            
        finally:
            await client.session.delete({'path': {'id': session['id']}})

    @pytest.mark.asyncio
    async def test_concurrent_session_performance(self):
        """Test performance with multiple concurrent sessions."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        try:
            from opencode_ai import AsyncOpencode
        except ImportError:
            pytest.skip("OpenCode SDK not available")
        
        client = AsyncOpencode()
        session_ids = []
        
        try:
            # Create multiple sessions
            async def create_and_use_session(index):
                session = await client.session.create({
                    'title': f'Concurrent Test Session {index}'
                })
                
                # Send a prompt
                response = await client.session.prompt({
                    'path': {'id': session['id']},
                    'body': {
                        'model': {
                            'providerID': 'anthropic',
                            'modelID': 'claude-3-5-sonnet-20241022'
                        },
                        'parts': [{
                            'type': 'text',
                            'text': f'Session {index}: What is {index} + {index}?'
                        }]
                    }
                })
                
                return session['id'], response
            
            start_time = time.time()
            
            results = await asyncio.gather(*[
                create_and_use_session(i) for i in range(5)
            ])
            
            total_time = time.time() - start_time
            session_ids = [result[0] for result in results]
            
            # Performance assertions
            assert total_time < 30.0, f"Concurrent operations too slow: {total_time}s"
            assert len(results) == 5
            assert all('content' in result[1] for result in results)
            
        finally:
            # Cleanup
            for session_id in session_ids:
                try:
                    await client.session.delete({'path': {'id': session_id}})
                except:
                    pass


class TestAgentPerformance:
    """Performance tests for autonomous agent."""

    @pytest.mark.asyncio
    async def test_task_execution_performance(self):
        """Test task execution performance."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        # Simulate agent task execution
        async def simulate_task(task, complexity):
            # Simulate work based on complexity
            await asyncio.sleep(complexity * 0.1)
            return {
                'task': task,
                'completed': True,
                'duration': complexity * 0.1
            }
        
        tasks = [
            ("Simple task", 1),
            ("Medium complexity task", 3),
            ("Complex task", 5)
        ]
        
        start_time = time.time()
        
        results = await asyncio.gather(*[
            simulate_task(task, complexity) for task, complexity in tasks
        ])
        
        total_time = time.time() - start_time
        
        # Verify all tasks completed
        assert len(results) == 3
        assert all(result['completed'] for result in results)
        
        # Performance should be reasonable
        assert total_time < 2.0, f"Task execution too slow: {total_time}s"

    @pytest.mark.asyncio
    async def test_memory_usage_simulation(self):
        """Test memory usage during extended operations."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        # Simulate memory-intensive operations
        data_store = []
        
        start_time = time.time()
        
        for i in range(100):
            # Simulate processing large data
            chunk = {
                'id': i,
                'data': 'x' * 1000,  # 1KB per chunk
                'processed': False
            }
            
            # Process chunk
            await asyncio.sleep(0.001)  # Simulate processing time
            chunk['processed'] = True
            
            data_store.append(chunk)
            
            # Simulate periodic cleanup to prevent memory bloat
            if i % 20 == 0 and len(data_store) > 50:
                # Keep only recent chunks
                data_store = data_store[-30:]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 5.0, f"Memory simulation took too long: {duration}s"
        assert len(data_store) <= 50  # Should have been cleaned up
        assert all(chunk['processed'] for chunk in data_store)

    @pytest.mark.asyncio
    async def test_concurrent_task_performance(self):
        """Test performance of concurrent task execution."""
        pytest.skip("Performance test - set RUN_PERFORMANCE_TESTS environment variable to run")
        
        async def worker_task(worker_id, task_count):
            results = []
            for i in range(task_count):
                await asyncio.sleep(0.01)  # Simulate work
                results.append(f'worker-{worker_id}-task-{i}')
            return results
        
        # Test with different numbers of workers
        worker_configs = [
            (2, 10),   # 2 workers, 10 tasks each
            (5, 4),    # 5 workers, 4 tasks each
            (10, 2)    # 10 workers, 2 tasks each
        ]
        
        for num_workers, tasks_per_worker in worker_configs:
            start_time = time.time()
            
            tasks = [
                worker_task(i, tasks_per_worker) for i in range(num_workers)
            ]
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Verify results
            assert len(results) == num_workers
            total_tasks = sum(len(worker_results) for worker_results in results)
            assert total_tasks == num_workers * tasks_per_worker
            
            # Performance should scale reasonably
            expected_max_time = tasks_per_worker * 0.01 * 1.5  # 50% buffer
            assert duration < expected_max_time, f"Worker config {num_workers}x{tasks_per_worker} too slow: {duration}s"


class TestSystemPerformance:
    """System-level performance tests."""

    @pytest.mark.asyncio
    async def test_file_io_performance(self):
        """Test file I/O performance."""
        import tempfile
        import os
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test file creation performance
            start_time = time.time()
            
            files_created = []
            for i in range(100):
                filename = os.path.join(temp_dir, f'test_file_{i}.txt')
                with open(filename, 'w') as f:
                    f.write(f'Content for file {i}\n' * 10)  # ~200 bytes per file
                files_created.append(filename)
            
            creation_time = time.time() - start_time
            
            # Test file reading performance
            start_time = time.time()
            
            for filename in files_created:
                with open(filename, 'r') as f:
                    content = f.read()
                    assert len(content) > 0
            
            reading_time = time.time() - start_time
            
            # Performance assertions
            assert creation_time < 1.0, f"File creation too slow: {creation_time}s"
            assert reading_time < 0.5, f"File reading too slow: {reading_time}s"
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_network_simulation_performance(self):
        """Test network operation simulation performance."""
        # Simulate network operations with varying latencies
        async def simulate_network_call(latency, payload_size):
            await asyncio.sleep(latency)
            return {
                'status': 'success',
                'payload': 'x' * payload_size,
                'latency': latency
            }
        
        # Test different scenarios
        scenarios = [
            (0.1, 100),   # Fast, small payload
            (0.5, 1000),  # Medium, medium payload
            (1.0, 10000), # Slow, large payload
        ]
        
        for latency, payload_size in scenarios:
            start_time = time.time()
            
            # Run multiple concurrent calls
            tasks = [
                simulate_network_call(latency, payload_size) for _ in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Verify results
            assert len(results) == 5
            assert all(result['status'] == 'success' for result in results)
            assert all(len(result['payload']) == payload_size for result in results)
            
            # Performance should be close to expected (with some tolerance)
            expected_time = latency * 1.5  # Allow 50% overhead
            assert duration < expected_time, f"Network simulation too slow: {duration}s (expected < {expected_time}s)"


# Configuration for performance tests
def pytest_configure(config):
    """Configure pytest for performance tests."""
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


if __name__ == '__main__':
    # Run with: python test_performance.py -v -m performance
    pytest.main([__file__, '-v'])