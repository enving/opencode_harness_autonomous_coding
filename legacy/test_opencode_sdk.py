#!/usr/bin/env python3
"""
Test OpenCode Python SDK Installation
"""

import asyncio
from opencode_ai import AsyncOpencode

async def test_opencode():
    """Test basic OpenCode SDK functionality."""
    try:
        print("Creating OpenCode client...")
        client = AsyncOpencode()
        
        print("Testing session list...")
        sessions = await client.session.list()
        print(f"✅ Success! Found {len(sessions)} existing sessions")
        
        print("Creating test session...")
        session = await client.session.create({
            "title": "Test Session - SDK Migration"
        })
        print(f"✅ Session created: {session.id}")
        
        print("Testing prompt...")
        result = await client.session.prompt({
            "path": {"id": session.id},
            "body": {
                "model": {
                    "providerID": "anthropic", 
                    "modelID": "claude-3-5-sonnet-20241022"
                },
                "parts": [{"type": "text", "text": "Hello! Can you help me understand the OpenCode API?"}]
            }
        })
        print(f"✅ Prompt sent successfully!")
        
        print("Cleaning up...")
        await client.session.delete({"path": {"id": session.id}})
        print("✅ Test session deleted")
        
        print("\n🎉 OpenCode SDK is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_opencode())