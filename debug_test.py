#!/usr/bin/env python3
"""
Simple test script to debug OpenCode client creation
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test basic imports"""
    print("Testing imports...")

    try:
        from client import create_client
        print("✓ client import successful")
    except Exception as e:
        print(f"✗ client import failed: {e}")
        return False

    try:
        from agent import run_autonomous_agent
        print("✓ agent import successful")
    except Exception as e:
        print(f"✗ agent import failed: {e}")
        return False

    try:
        from prompts import get_initializer_prompt
        print("✓ prompts import successful")
    except Exception as e:
        print(f"✗ prompts import failed: {e}")
        return False

    return True

def test_client_creation():
    """Test client creation"""
    print("\nTesting client creation...")

    try:
        from client import create_client
        project_dir = Path("../claude_clone_test1")
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"Project dir: {project_dir.resolve()}")

        # Test client creation
        client = create_client(project_dir, "opencode/big-pickle")
        if client:
            print("✓ Client creation successful")
            return True
        else:
            print("✗ Client creation failed")
            return False

    except Exception as e:
        print(f"✗ Client creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent():
    """Test agent session creation"""
    print("\nTesting agent session creation...")

    try:
        from client import create_client, create_session
        from prompts import get_initializer_prompt

        project_dir = Path("../claude_clone_test1")
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"Creating client for project: {project_dir.resolve()}")
        client = create_client(project_dir, "opencode/big-pickle")

        if not client:
            print("✗ Client creation failed")
            return False

        print("Creating session...")
        session_id = await create_session(client, "Test Session", project_dir)
        print(f"✓ Session created: {session_id}")

        print("Getting prompt...")
        prompt = get_initializer_prompt()
        print(f"✓ Prompt loaded (length: {len(prompt)})")

        return True

    except Exception as e:
        print(f"✗ Agent test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("OpenCode Debug Test")
    print("=" * 50)

    # Check environment
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")

    # Check API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    opencode_key = os.environ.get("OPENCODE_API_KEY")

    print(f"ANTHROPIC_API_KEY: {'SET' if anthropic_key else 'NOT SET'}")
    print(f"OPENROUTER_API_KEY: {'SET' if openrouter_key else 'NOT SET'}")
    print(f"OPENCODE_API_KEY: {'SET' if opencode_key else 'NOT SET'}")

    # Test imports
    if not test_imports():
        return

    # Test client creation
    if not test_client_creation():
        return

    # Test agent functionality
    import asyncio
    if not asyncio.run(test_agent()):
        return

    print("\n✓ All tests passed!")

if __name__ == "__main__":
    main()