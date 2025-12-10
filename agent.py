"""
OpenCode Agent Session Logic
=========================

Core agent interaction functions for running autonomous coding sessions with OpenCode.
"""

import asyncio
from pathlib import Path
from typing import Optional, Tuple

from opencode_ai import AsyncOpencode

from client import create_client, create_session, send_prompt
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: AsyncOpencode,
    session_id: str,
    message: str,
    project_dir: Path,
    model: str = "auto",
) -> Tuple[str, str]:
    """
    Run a single agent session using OpenCode SDK.

    Args:
        client: OpenCode client
        session_id: Existing session ID
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    print("Sending prompt to OpenCode agent...\n")

    try:
        # Send the prompt
        result = await send_prompt(client, session_id, message, model=model)
        print(f"DEBUG: send_prompt result: {result}")

        # Check for API errors
        if hasattr(result, 'error') and result.error:
            print(f"API Error: {result.error}")
            return "error", str(result.error)
        if hasattr(result, 'info') and result.info and 'error' in result.info:
            print(f"API Error in info: {result.info['error']}")
            return "error", str(result.info['error'])

        # Extract response text from result
        response_text = ""
        if hasattr(result, 'content'):
            for part in result.content:
                if hasattr(part, 'text'):
                    response_text += part.text
                    print(part.text, end="", flush=True)
                elif hasattr(part, 'type') and part.type == 'tool_use':
                    print(f"\n[Tool: {part.name}]", flush=True)
                    if hasattr(part, 'input'):
                        input_str = str(part.input)
                        if len(input_str) > 200:
                            print(f"   Input: {input_str[:200]}...", flush=True)
                        else:
                            print(f"   Input: {input_str}", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Run the autonomous agent loop using OpenCode.

    Args:
        project_dir: Directory for the project
        model: Model to use
        max_iterations: Maximum number of iterations (None for unlimited)
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT DEMO (OpenCode)")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()
    
    print(f"DEBUG: is_first_run={is_first_run}")
    print(f"DEBUG: feature_list.json exists={tests_file.exists()}")
    print(f"DEBUG: feature_list.json path={tests_file.resolve()}")
    if tests_file.exists():
        try:
            import json
            features = json.loads(tests_file.read_text())
            print(f"DEBUG: feature_list.json has {len(features)} features")
            passed = sum(1 for f in features if f.get("passes", False))
            print(f"DEBUG: {passed} features passed, {len(features) - passed} remaining")
        except Exception as e:
            print(f"WARNING: Could not read feature_list.json: {e}")

    if is_first_run:
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  The agent is generating 200 detailed test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir)
    else:
        print("Continuing existing project")
        print_progress_summary(project_dir)

    # Create OpenCode client
    client = create_client(project_dir, model)

    # Create or get session
    if is_first_run:
        print("📋 Using INITIALIZER prompt for first session")
        session_id = await create_session(client, "Initializer Agent - Project Setup", project_dir)
        prompt = get_initializer_prompt()
    else:
        print("💻 Using CODING prompt for continuation")
        session_id = await create_session(client, "Coding Agent - Feature Implementation", project_dir)
        prompt = get_coding_prompt()

    # Main loop
    iteration = 0
    used_initializer = is_first_run  # Track if we started with initializer

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Print session header
        print_session_header(iteration, used_initializer and iteration == 1)

        # Run session
        status, response = await run_agent_session(client, session_id, prompt, project_dir, model)
        
        # After first iteration with initializer, switch to coding prompt
        if iteration == 1 and used_initializer:
            print("\nSwitching from INITIALIZER to CODING prompt for next iteration")
            prompt = get_coding_prompt()
            
            # Check if feature_list.json was created
            if tests_file.exists():
                try:
                    import json
                    features = json.loads(tests_file.read_text())
                    print(f"feature_list.json created with {len(features)} features")
                except Exception as e:
                    print(f"WARNING: Could not validate feature_list.json: {e}")

        # Handle status
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            print("\nSession encountered an error")
            print("Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")