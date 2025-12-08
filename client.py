"""
OpenCode Client Configuration
===========================

Functions for creating and configuring OpenCode Python SDK client.
"""

import json
import os
from pathlib import Path
from typing import Optional

from opencode_ai import AsyncOpencode

from security import get_opencode_permissions


def create_client(project_dir: Path, model: str = "auto") -> Optional[AsyncOpencode]:
    """
    Create an OpenCode client with security configuration.

    Args:
        project_dir: Directory for project
        model: Model strategy ("auto" for optimal free model, or specific model)

    Returns:
        Configured AsyncOpencode client, or None if no API key available

    Security layers (defense in depth):
    1. Permissions - File operations restricted to project_dir only
    2. Security rules - Bash commands validated against an allowlist
       (see security.py for ALLOWED_COMMANDS)
    """
    # Check for API key (support multiple providers)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not anthropic_key and not openrouter_key:
        print("🔑 No API key found!")
        print("💡 Options:")
        print("   1. Set ANTHROPIC_API_KEY for Claude models")
        print("   2. Set OPENROUTER_API_KEY for OpenRouter models")
        print()
        return None
    
    # Determine model strategy
    if model == "auto":
        if openrouter_key:
            model_strategy = "openrouter/anthropic/claude-3.5-sonnet"  # Default OpenRouter model
            print(f"🚀 Using OpenRouter Claude 3.5 Sonnet")
        elif anthropic_key:
            model_strategy = "anthropic/claude-3-5-sonnet-20241022"  # Default Claude model
            print(f"🤖 Using Claude Sonnet 3.5 (paid tier)")
        else:
            model_strategy = "auto"  # Fallback to auto-selection
            print(f"🎯 Using auto-selected model")
    else:
        # Use specified model
        model_strategy = model
        print(f"🎯 Using specified model: {model}")
    
    print(f"📋 Model strategy: {model_strategy}")
    
    # Create OpenCode client
    try:
        client = AsyncOpencode()
        print(f"✅ OpenCode client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OpenCode client: {e}")
        return None
    
    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create OpenCode configuration file
    config_file = project_dir / ".opencode_settings.json"
    opencode_config = {
        "model": model_strategy,
        "permissions": get_opencode_permissions(project_dir),
        "security": {
            "bash_allowlist": [
                "ls", "cat", "head", "tail", "wc", "grep",
                "npm", "node", "git", "ps", "lsof", "sleep", "pkill"
            ]
        }
    }

    with open(config_file, "w") as f:
        json.dump(opencode_config, f, indent=2)

    print(f"✅ Created OpenCode settings at {config_file}")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist (see security.py)")
    print(f"   - Model strategy: {model_strategy}")
    print()

    return client


async def create_session(client: AsyncOpencode, title: str, project_dir: Path) -> str:
    """
    Create a new OpenCode session for the agent.
    
    Args:
        client: OpenCode client
        title: Session title
        project_dir: Project directory path
        
    Returns:
        Session ID
    """
    try:
        session = await client.session.create({
            "title": title,
            "cwd": str(project_dir.resolve())
        })
        
        print(f"✅ Created OpenCode session: {session.id}")
        return session.id
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        raise


async def send_prompt(
    client: AsyncOpencode, 
    session_id: str, 
    message: str,
    model: str = "auto"
) -> dict:
    """
    Send a prompt to an OpenCode session.
    
    Args:
        client: OpenCode client
        session_id: Session ID
        message: Prompt message
        model: Model strategy ("auto" for optimal selection)
        
    Returns:
        Response data
    """
    try:
        # Handle model selection
        if model == "auto":
            # Let OpenCode choose the optimal model
            model_config = {}  # OpenCode will auto-select
        else:
            # Use specified model (format: provider/model)
            if "/" in model:
                provider, model_id = model.split("/", 1)
                model_config = {
                    "providerID": provider,
                    "modelID": model_id
                }
            else:
                # If no provider specified, use as model ID
                model_config = {
                    "modelID": model
                }
        
        result = await client.session.prompt({
            "path": {"id": session_id},
            "body": {
                "model": model_config,
                "parts": [{"type": "text", "text": message}]
            }
        })
        
        return result
    except Exception as e:
        print(f"❌ Failed to send prompt: {e}")
        raise