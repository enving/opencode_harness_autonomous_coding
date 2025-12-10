#!/usr/bin/env python3
"""
Quick test to create feature_list.json manually
"""

import asyncio
from opencode_ai import AsyncOpencode

async def create_simple_feature_list():
    """Create a simple feature_list.json to test"""
    client = AsyncOpencode(base_url="http://localhost:4096")
    
    # Use existing session
    sessions = await client.session.list()
    if sessions:
        session = sessions[0]
        print(f"Using session: {session.id}")
        
        # Send simple message to create basic feature list
        result = await client.session.chat(
            session.id,
            model_id="anthropic/claude-3.5-sonnet",
            provider_id="openrouter",
            parts=[{
                "type": "text", 
                "text": """
Please create a simple feature_list.json file with just 5 basic test cases to get started.

Format:
[
  {
    "category": "functional",
    "description": "User can register for an account",
    "steps": [
      "Step 1: Navigate to registration page",
      "Step 2: Fill in registration form",
      "Step 3: Submit form and verify success"
    ],
    "passes": false
  }
]

Create this file now so we can proceed with development.
"""
            }]
        )
        
        print("Message sent successfully!")
        return True
    else:
        print("No sessions available")
        return False

if __name__ == "__main__":
    asyncio.run(create_simple_feature_list())