#!/usr/bin/env python3
"""
Test script for OpenCode connection
"""

import asyncio
from opencode_ai import AsyncOpencode

async def test_opencode_connection():
    """Test basic OpenCode functionality"""
    print("Testing OpenCode connection...")
    
    # Create client
    client = AsyncOpencode(base_url="http://localhost:4096")
    print("Client created successfully")
        
        # Test basic connection - list sessions
    sessions = await client.session.list()
    print(f"Connection successful! Found {len(sessions)} existing sessions")
    
    # Create a test session
    session = await client.session.create(
        body={"title": "Test Session"}
    )
    print(f"Test session created: {session.id}")
    
    # Send a simple message
    result = await client.session.chat(
        session.id,
        body={
            "parts": [{"type": "text", "text": "Hello, can you create a simple test file?"}]
        }
    )
    print("Message sent successfully")
    print(f"Response type: {type(result)}")
    
    # Clean up
    await client.session.delete(session.id)
    print("Test session deleted")
    
    return True
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
    success = asyncio.run(test_opencode_connection())
    if success:
        print("\nOpenCode connection test PASSED!")
    else:
        print("\nOpenCode connection test FAILED!")