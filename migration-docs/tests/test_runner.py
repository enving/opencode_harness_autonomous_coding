#!/usr/bin/env python3
"""
OpenCode SDK Test Runner
========================

Comprehensive test runner for the OpenCode SDK test suite
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Test runner for OpenCode SDK"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results: Dict[str, Dict] = {}
        
    def run_test_file(self, test_file: Path) -> Tuple[bool, str, float]:
        """Run a single test file and return results"""
        start_time = time.time()
        
        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_file), '-v'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            duration = time.time() - start_time
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output, duration
            
        except Exception as e:
            duration = time.time() - start_time
            return False, f"Error running {test_file}: {e}", duration
    
    def run_all_tests(self) -> Dict[str, Dict]:
        """Run all test files and collect results"""
        test_files = [
            'test_opencode_integration.py',
            'test_performance.py', 
            'test_error_handling.py',
            '../src/tests/test_security.py'
        ]
        
        print("=" * 70)
        print("  OPENCODE SDK COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print()
        
        total_start = time.time()
        
        for test_file in test_files:
            test_path = self.test_dir / test_file
            
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue
                
            print(f"🧪 Running {test_file}...")
            
            success, output, duration = self.run_test_file(test_path)
            
            self.results[test_file] = {
                'success': success,
                'duration': duration,
                'output': output
            }
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} ({duration:.2f}s)")
            
            if not success:
                print(f"   Output: {output[:200]}...")
            
            print()
        
        total_duration = time.time() - total_start
        
        # Print summary
        self.print_summary(total_duration)
        
        return self.results
    
    def print_summary(self, total_duration: float):
        """Print test summary"""
        print("=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results.values() if r['success'])
        total = len(self.results)
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Duration: {total_duration:.2f}s")
        print()
        
        if failed > 0:
            print("FAILED TESTS:")
            for test_file, result in self.results.items():
                if not result['success']:
                    print(f"  ❌ {test_file}")
            print()
        
        # Performance summary
        if 'test_performance.py' in self.results:
            print("PERFORMANCE TESTS:")
            perf_result = self.results['test_performance.py']
            print(f"  Duration: {perf_result['duration']:.2f}s")
            print(f"  Status: {'✅ PASSED' if perf_result['success'] else '❌ FAILED'}")
            print()
        
        # Integration tests summary
        if 'test_opencode_integration.py' in self.results:
            print("INTEGRATION TESTS:")
            integ_result = self.results['test_opencode_integration.py']
            print(f"  Duration: {integ_result['duration']:.2f}s")
            print(f"  Status: {'✅ PASSED' if integ_result['success'] else '❌ FAILED'}")
            print()
        
        # Error handling tests summary
        if 'test_error_handling.py' in self.results:
            print("ERROR HANDLING TESTS:")
            error_result = self.results['test_error_handling.py']
            print(f"  Duration: {error_result['duration']:.2f}s")
            print(f"  Status: {'✅ PASSED' if error_result['success'] else '❌ FAILED'}")
            print()
        
        print("=" * 70)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"💥 {failed} TEST(S) FAILED")
            return 1
    
    def run_specific_test(self, test_name: str):
        """Run a specific test file"""
        test_path = self.test_dir / test_name
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_name}")
            return 1
        
        print(f"🧪 Running {test_name}...")
        
        success, output, duration = self.run_test_file(test_path)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} ({duration:.2f}s)")
        
        if not success:
            print("\nOUTPUT:")
            print(output)
        
        return 0 if success else 1
    
    def run_quick_tests(self):
        """Run a quick subset of tests"""
        quick_tests = [
            'test_opencode_integration.py',
            '../src/tests/test_security.py'
        ]
        
        print("=" * 70)
        print("  OPENCODE SDK QUICK TESTS")
        print("=" * 70)
        print()
        
        total_start = time.time()
        
        for test_file in quick_tests:
            test_path = self.test_dir / test_file
            
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue
                
            print(f"🧪 Running {test_file}...")
            
            success, output, duration = self.run_test_file(test_path)
            
            self.results[test_file] = {
                'success': success,
                'duration': duration,
                'output': output
            }
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} ({duration:.2f}s)")
            print()
        
        total_duration = time.time() - total_start
        return self.print_summary(total_duration)


def main():
    """Main test runner entry point"""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick":
            return runner.run_quick_tests()
        elif command.startswith("test_"):
            return runner.run_specific_test(command)
        else:
            print("Usage:")
            print("  python test_runner.py              # Run all tests")
            print("  python test_runner.py quick        # Run quick tests")
            print("  python test_runner.py test_<name>   # Run specific test")
            return 1
    else:
        results = runner.run_all_tests()
        return 0 if all(r['success'] for r in results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())