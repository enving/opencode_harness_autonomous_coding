#!/usr/bin/env python3
"""
Minimal test to send one message to OpenCode
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_single_message():
    """Send a single test message to OpenCode"""
    print("Testing single message to OpenCode...")

    try:
        from client import create_client, create_session, send_prompt
        from prompts import get_initializer_prompt

        project_dir = Path("../claude_clone_test1")
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create client
        print("Creating client...")
        client = create_client(project_dir, "opencode/big-pickle")
        if not client:
            print("✗ Client creation failed")
            return

        # Create session
        print("Creating session...")
        session_id = await create_session(client, "Debug Session", project_dir)

        # Get prompt
        print("Getting prompt...")
        prompt = get_initializer_prompt()
        print(f"Prompt length: {len(prompt)} characters")

        # Send message
        print("Sending message to OpenCode...")
        print("This may take a while for the first message...")

        result = await send_prompt(client, session_id, prompt[:500], model="opencode/big-pickle")  # Short prompt for testing

        print("✓ Message sent successfully!")
        print(f"Result type: {type(result)}")

        if hasattr(result, 'content'):
            print(f"Response has content: {len(result.content)} parts")
            for i, part in enumerate(result.content):
                if hasattr(part, 'text'):
                    print(f"Part {i}: {part.text[:100]}...")
                else:
                    print(f"Part {i}: {type(part)}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Single Message Test")
    print("=" * 30)

    # Run test
    success = asyncio.run(test_single_message())

    if success:
        print("\n✓ Single message test passed!")
    else:
        print("\n✗ Single message test failed!")

if __name__ == "__main__":
    main()