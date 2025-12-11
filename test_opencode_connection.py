#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test OpenCode SDK Connection
============================

Quick test to verify the OpenCode Python SDK is working correctly
with the local server at http://localhost:4096
"""

import asyncio
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from opencode_ai import AsyncOpencode


async def main():
    """Test OpenCode connection."""
    print("=" * 70)
    print("  OpenCode SDK Connection Test")
    print("=" * 70)
    print()
    
    # 1. Create client with correct base_url
    base_url = "http://localhost:4096"
    print(f"[1/5] Creating client with base_url: {base_url}")
    try:
        client = AsyncOpencode(base_url=base_url, timeout=30.0)
        print("      ✓ Client created successfully")
    except Exception as e:
        print(f"      ✗ Failed to create client: {e}")
        return
    print()
    
    # 2. List providers
    print("[2/5] Fetching available providers...")
    try:
        providers_response = await client.app.providers()
        # providers_response is a Pydantic model, access .providers attribute
        providers = providers_response.providers if hasattr(providers_response, 'providers') else []
        print(f"      ✓ Found {len(providers)} providers:")
        for p in providers:
            num_models = len(p.models) if hasattr(p, 'models') else 0
            provider_name = p.name if hasattr(p, 'name') else 'Unknown'
            provider_id = p.id if hasattr(p, 'id') else 'unknown'
            print(f"        - {provider_name} ({provider_id}): {num_models} models")
    except Exception as e:
        print(f"      ✗ Failed to fetch providers: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 3. Create a session
    print("[3/5] Creating a test session...")
    try:
        # session.create() needs empty extra_body to send valid JSON
        session = await client.session.create(extra_body={})
        session_id = session.id
        print(f"      ✓ Session created: {session_id}")
    except Exception as e:
        print(f"      ✗ Failed to create session: {e}")
        print(f"      Trying fallback: use existing session...")
        try:
            sessions = await client.session.list()
            if sessions and len(sessions) > 0:
                session_id = sessions[0].id
                print(f"      ✓ Using existing session: {session_id}")
            else:
                print(f"      ✗ No sessions available")
                return
        except Exception as e2:
            print(f"      ✗ Fallback also failed: {e2}")
            return
    print()
    
    # 4. Send a simple test message
    print("[4/5] Sending test message with FREE opencode/big-pickle model...")
    try:
        result = await client.session.chat(
            session_id,
            model_id="big-pickle",
            provider_id="opencode",
            parts=[{"type": "text", "text": "Hello! Please respond with just 'OK' if you can read this."}],
        )
        print(f"      ✓ Response received")
        
        # Extract text from response
        response_text = ""
        if hasattr(result, 'content'):
            for part in result.content:
                if hasattr(part, 'text'):
                    response_text += part.text
        
        if response_text:
            print(f"      Model response: {response_text[:200]}")
        else:
            print(f"      Full result: {result}")
            
    except Exception as e:
        print(f"      ✗ Failed to send message: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 5. Clean up
    print("[5/5] Cleaning up...")
    try:
        await client.session.delete(session_id)
        print(f"      ✓ Session deleted")
    except Exception as e:
        print(f"      ⚠ Could not delete session: {e}")
    print()
    
    print("=" * 70)
    print("  Test Complete!")
    print("=" * 70)
    print()
    print("If all steps passed, your OpenCode SDK setup is working correctly.")
    print("You can now run: python autonomous_agent_demo.py --project-dir ./test_project")


if __name__ == "__main__":
    asyncio.run(main())
