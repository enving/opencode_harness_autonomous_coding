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


def read_api_key_from_file() -> Optional[str]:
    """
    Try to read API key from /tmp/api-key file (Docker setup).
    
    Returns:
        API key string or None
    """
    api_key_paths = [
        Path("/tmp/api-key"),
        Path("C:/tmp/api-key"),
        Path("./.opencode.json"),
    ]
    
    for path in api_key_paths:
        if path.exists():
            try:
                content = path.read_text().strip()
                # If it's a JSON file, extract the key
                if path.suffix == ".json":
                    config = json.loads(content)
                    if "apiKey" in config:
                        print(f"✅ Found API key in {path}")
                        return config["apiKey"]
                else:
                    print(f"✅ Found API key in {path}")
                    return content
            except Exception as e:
                print(f"⚠️  Could not read API key from {path}: {e}")
    
    return None


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
    opencode_key = os.environ.get("OPENCODE_API_KEY")
    
    # Try to read from file if not in environment
    if not anthropic_key and not openrouter_key and not opencode_key:
        file_key = read_api_key_from_file()
        if file_key:
            # Assume it's an OpenRouter key if read from file
            openrouter_key = file_key
            os.environ["OPENROUTER_API_KEY"] = file_key
    
    # Debug output
    print(f"Debug: ANTHROPIC_API_KEY = {'SET' if anthropic_key else 'NOT SET'}")
    print(f"Debug: OPENROUTER_API_KEY = {'SET' if openrouter_key else 'NOT SET'}")
    print(f"Debug: OPENCODE_API_KEY = {'SET' if opencode_key else 'NOT SET'}")
    
    # If still no key, show error
    if not anthropic_key and not openrouter_key and not opencode_key:
        print("❌ ERROR: No API keys found!")
        print("\nOptions:")
        print("  1. Set environment variable:")
        print("     $env:OPENROUTER_API_KEY='sk-or-v1-...'")
        print("\n  2. Create /tmp/api-key file with your key")
        print("\n  3. Put key in .opencode.json as 'apiKey'")
        return None
    
    # Determine model strategy
    if model == "auto":
        if openrouter_key:
            model_strategy = "openrouter/meta-llama/llama-3.1-8b-instruct:free"  # Free OpenRouter model
            print(f"🚀 Using free OpenRouter Llama 3.1")
        elif anthropic_key:
            model_strategy = "anthropic/claude-3-5-sonnet-20241022"  # Default Claude model
            print(f"🤖 Using Claude Sonnet 3.5 (paid tier)")
        elif opencode_key:
            model_strategy = "opencode/gpt-4o-mini"  # OpenCode free model
            print(f"🎯 Using OpenCode GPT-4o Mini (free)")
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
        # Check for custom base URL
        base_url = os.environ.get("OPENCODE_BASE_URL", "http://localhost:4096")
        client = AsyncOpencode(base_url=base_url, timeout=1200.0)
        print(f"✅ OpenCode client created with URL: {base_url}")
        print("💡 Make sure OpenCode server is running on this address")
    except Exception as e:
        print(f"❌ Failed to create OpenCode client: {e}")
        return None
    
    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create OpenCode configuration file
    config_file = project_dir / ".opencode.json"
    opencode_config = {
        "$schema": "https://opencode.ai/config.json",
        "theme": "opencode",
        "model": model_strategy,
        "max_tokens": 200,  # Reduced to minimize costs
        "autoupdate": True,
        "permission": {
            "edit": "allow",
            "bash": "ask",
            "webfetch": "deny",
            "doom_loop": "ask",
            "external_directory": "ask"
        },
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
        # Try to create a new session first
        try:
            session = await client.session.create(extra_body={"title": title})
            print(f"Created new OpenCode session: {session.id}")
            return session.id
        except Exception as create_error:
            print(f"Failed to create new session: {create_error}")
            print("Falling back to existing session...")
            
            # Fall back to using existing session
            sessions = await client.session.list()
            if sessions:
                session = sessions[0]
                print(f"Using existing session: {session.id}")
                return session.id
            else:
                raise Exception("No existing sessions available and cannot create new one")
                
    except Exception as e:
        print(f"Failed to create or get session: {e}")
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
        print(f"DEBUG: Sending prompt with model={model}, message length={len(message)}")
        
        # Get API keys
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        opencode_key = os.environ.get("OPENCODE_API_KEY")
        
        # Handle model selection
        if model == "auto":
            # ALWAYS prefer FREE models!
            if openrouter_key:
                # Use FREE Mistral model
                print("Using FREE OpenRouter Mistral model")
                result = await client.session.chat(
                    session_id,
                    model_id="mistralai/mistral-7b-instruct:free",
                    provider_id="openrouter",
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": 200}
                )
            elif anthropic_key:
                # WARNING: This is PAID tier!
                print("WARNING: Using PAID Claude model - costs apply!")
                print("TIP: Set OPENROUTER_API_KEY to use free models instead")
                result = await client.session.chat(
                    session_id,
                    model_id="claude-3-5-sonnet-20241022",
                    provider_id="anthropic",
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": 200}  # Reduced from 1000
                )
            else:
                # Fallback to OpenCode free model
                print("Using OpenCode free model")
                result = await client.session.chat(
                    session_id,
                    model_id="gpt-4o-mini",
                    provider_id="opencode",
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": 200}  # Reduced from 500
                )
        else:
            # Use specified model (format: provider/model or provider/vendor/model)
            if "/" in model:
                parts_list = model.split("/")
                if len(parts_list) == 2:
                    # Format: provider/model (e.g., anthropic/claude-sonnet-4-5-20250929)
                    provider, model_id = parts_list
                elif len(parts_list) == 3:
                    # Format: provider/vendor/model (e.g., openrouter/anthropic/claude-3.5-sonnet)
                    provider, vendor, model_name = parts_list
                    model_id = f"{vendor}/{model_name}"
                else:
                    # Fallback: use as-is
                    provider = "openrouter"
                    model_id = model
                
                # Force free tier by setting very low max_tokens
                extra_body = {"max_tokens": 200}  # Reduced from 500
                if "free" in model_id.lower():
                    extra_body["max_tokens"] = 200  # Keep at 200 for free models

                result = await client.session.chat(
                    session_id,
                    model_id=model_id,
                    provider_id=provider,
                    parts=[{"type": "text", "text": message}],
                    extra_body=extra_body
                )
            else:
                # If no provider specified, use as model ID with default provider
                print("⚠️  Using default provider with custom model")
                result = await client.session.chat(
                    session_id,
                    model_id=model,
                    provider_id="openrouter",
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": 200}  # Reduced from 2000
                )
        
        return result
    except Exception as e:
        print(f"❌ Failed to send prompt: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise



