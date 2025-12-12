"""
OpenCode Client Configuration
===========================

Functions for creating and configuring OpenCode Python SDK client.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # Ignore if reconfigure not available

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
                         print(f"[OK] Found API key in {path}")
                         return config["apiKey"]
                else:
                    print(f"[OK] Found API key in {path}")
                    return content
            except Exception as e:
                print(f"[WARN] Could not read API key from {path}: {e}")
    
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
        print("[ERROR] No API keys found!")
        print("\nOptions:")
        print("  1. Set environment variable:")
        print("     $env:OPENROUTER_API_KEY='sk-or-v1-...'")
        print("\n  2. Create /tmp/api-key file with your key")
        print("\n  3. Put key in .opencode.json as 'apiKey'")
        return None
    
    # Determine model strategy based on available providers
    # Provider priorities: opencode (FREE) > mistral (cheap) > anthropic (PAID)
    if model == "auto":
        # ALWAYS prefer FREE OpenCode models!
        if opencode_key or True:  # OpenCode has public models
            model_strategy = "opencode/big-pickle"  # FREE OpenCode model
            print(f"[INFO] Using FREE OpenCode 'big-pickle' model")
        elif anthropic_key:
            model_strategy = "anthropic/claude-3-5-sonnet-20241022"
            print(f"[WARNING] Using Claude Sonnet 3.5 (PAID tier - costs apply!)")
        else:
            # Fallback to cheapest Mistral
            model_strategy = "mistral/ministral-3b-latest"
            print(f"[INFO] Using Mistral 3B (very cheap: $0.04/M tokens)")
    else:
        # Use specified model
        model_strategy = model
        print(f"[INFO] Using specified model: {model}")
    
    print(f"[INFO] Model strategy: {model_strategy}")
    
    # Create OpenCode client
    try:
        # Check for custom base URL
        base_url = os.environ.get("OPENCODE_BASE_URL", "http://localhost:4096")
        client = AsyncOpencode(base_url=base_url, timeout=1200.0)
        print(f"[OK] OpenCode client created with URL: {base_url}")
        print("[INFO] Make sure OpenCode server is running on this address")
    except Exception as e:
        print(f"[ERROR] Failed to create OpenCode client: {e}")
        return None
    
    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create OpenCode configuration file
    config_file = project_dir / ".opencode.json"
    
    # Parse model strategy into provider and model
    if "/" in model_strategy:
        provider, model_id = model_strategy.split("/", 1)
    else:
        provider = "opencode"
        model_id = model_strategy
    
    opencode_config = {
        "$schema": "https://opencode.ai/config.json",
        "theme": "opencode",
        "provider": provider,  # SDK uses separate provider field
        "model": model_id,      # Just the model ID, not provider/model
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
                "npm", "node", "npx", "git", "ps", "lsof", "sleep", "pkill"
            ]
        },
        "mcpServers": {
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            }
        }
    }

    with open(config_file, "w") as f:
        json.dump(opencode_config, f, indent=2)

    print(f"[OK] Created OpenCode settings at {config_file}")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist (see security.py)")
    print(f"   - Provider: {provider}")
    print(f"   - Model: {model_id}")
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
        
        # Handle model selection - use SDK-compatible providers
        if model == "auto":
            # ALWAYS prefer FREE OpenCode models!
            print("[OK] Using FREE OpenCode model (big-pickle)")
            result = await client.session.chat(
                session_id,
                model_id="big-pickle",  # Free OpenCode model
                provider_id="opencode",
                parts=[{"type": "text", "text": message}],
                extra_body={"max_tokens": 8000}  # Reasonable for free tier
            )
        else:
            # Use specified model (format: provider/model)
            # Supported providers: mistral, anthropic, opencode
            if "/" in model:
                parts_list = model.split("/", 1)  # Split only on first /
                provider, model_id = parts_list
                
                # Validate provider (must be one of: mistral, anthropic, opencode)
                valid_providers = ["mistral", "anthropic", "opencode"]
                if provider not in valid_providers:
                    print(f"[WARN] Invalid provider '{provider}'. Using 'opencode' instead.")
                    print(f"[INFO] Valid providers: {', '.join(valid_providers)}")
                    provider = "opencode"
                    model_id = "big-pickle"
                
                # Set max_tokens based on cost
                if provider == "opencode":
                    max_tokens = 8000  # Free tier - generous
                    print(f"[OK] Using FREE {provider} model: {model_id}")
                elif provider == "mistral":
                    max_tokens = 4000  # Cheap but not free
                    print(f"[OK] Using Mistral model: {model_id} (low cost)")
                else:  # anthropic
                    max_tokens = 2000  # Expensive - limit usage
                    print(f"[WARNING] Using PAID Anthropic model: {model_id}")
                    print(f"[WARNING] This will incur costs! Consider using opencode/big-pickle instead.")

                result = await client.session.chat(
                    session_id,
                    model_id=model_id,
                    provider_id=provider,
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": max_tokens}
                )
            else:
                # No provider specified - assume it's an opencode model ID
                print(f"[WARN] No provider specified. Assuming opencode/{model}")
                result = await client.session.chat(
                    session_id,
                    model_id=model,
                    provider_id="opencode",
                    parts=[{"type": "text", "text": message}],
                    extra_body={"max_tokens": 8000}
                )
        
        return result
    except Exception as e:
        print(f"[ERROR] Failed to send prompt: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise



