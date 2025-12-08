"""
OpenCode Client Configuration
===========================

Functions for creating and configuring the OpenCode Python SDK client.
"""

import json
import os
from pathlib import Path
from typing import Optional

from opencode_ai import AsyncOpencode

from security import get_opencode_permissions


def create_client(project_dir: Path, model: str = "anthropic/claude-3-5-sonnet-20241022") -> AsyncOpencode:
    """
    Create an OpenCode client with security configuration.

    Args:
        project_dir: Directory for the project
        model: Model to use (default: Claude Sonnet 3.5)

    Returns:
        Configured AsyncOpencode client

    Security layers (defense in depth):
    1. Permissions - File operations restricted to project_dir only
    2. Security rules - Bash commands validated against an allowlist
       (see security.py for ALLOWED_COMMANDS)
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Get your API key from: https://console.anthropic.com/"
        )

    # Create OpenCode client
    client = AsyncOpencode(
        # Base URL can be configured via OPENCODE_BASE_URL env var
        # Default: http://localhost:4096
    )

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create OpenCode configuration file
    config_file = project_dir / ".opencode_settings.json"
    opencode_config = {
        "model": model,
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

    print(f"Created OpenCode settings at {config_file}")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist (see security.py)")
    print(f"   - Model: {model}")
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
    session = await client.session.create({
        "title": title,
        "cwd": str(project_dir.resolve())
    })
    
    print(f"Created OpenCode session: {session.id}")
    return session.id


async def send_prompt(
    client: AsyncOpencode, 
    session_id: str, 
    message: str,
    model: str = "anthropic/claude-3-5-sonnet-20241022"
) -> dict:
    """
    Send a prompt to an OpenCode session.
    
    Args:
        client: OpenCode client
        session_id: Session ID
        message: Prompt message
        model: Model to use
        
    Returns:
        Response data
    """
    result = await client.session.prompt({
        "path": {"id": session_id},
        "body": {
            "model": {
                "providerID": model.split("/")[0],
                "modelID": model.split("/")[1]
            },
            "parts": [{"type": "text", "text": message}]
        }
    })
    
    return result