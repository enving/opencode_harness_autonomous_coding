#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo - OpenCode Version
==========================================

A minimal harness demonstrating long-running autonomous coding with OpenCode.
This script implements the two-agent pattern (initializer + coding agent) and
incorporates all the strategies from the long-running agents guide.

Example Usage:
    python autonomous_agent_demo.py --project-dir ./my_project
    python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 5
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_autonomous_agent


# Configuration
DEFAULT_MODEL = "auto"  # Auto-select optimal model (free tier with OpenCode key)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent Demo - OpenCode Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start fresh project
  python autonomous_agent_demo.py --project-dir ./my_project

  # Use a specific model
  python autonomous_agent_demo.py --project-dir ./my_project --model anthropic/claude-3-5-sonnet-20241022

  # Limit iterations for testing
  python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 5

  # Continue existing project
  python autonomous_agent_demo.py --project-dir ./my_project

 Environment Variables:
   ANTHROPIC_API_KEY    Your Anthropic API key (for Claude models)
   OPENCODE_API_KEY   Your OpenRouter API key (for multiple models)
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help="Directory for the project (default: ./autonomous_demo_project). Relative paths automatically placed in project directory.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

 # Check for API key (support multiple providers)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    opencode_key = os.environ.get("OPENCODE_API_KEY")
    
    # TEMPORARY: Set keys manually for testing (remove this in production!)
    if not anthropic_key and not openrouter_key and not opencode_key:
        print("Warning: No API keys found in environment. Please set them manually.")
        print("For now, continuing with test setup...")
        # For testing, we'll assume keys are set and let the client handle it
        anthropic_key = "dummy_key_for_testing"
        openrouter_key = "dummy_key_for_testing"
    
    if not anthropic_key and not openrouter_key and not opencode_key:
        print("Error: No API key found. Set either ANTHROPIC_API_KEY or OPENCODE_API_KEY")
        print("\nOptions:")
        print("  1. Anthropic API key (Claude models):")
        print("     $env:ANTHROPIC_API_KEY='your-api-key-here'")
        print("     Get key from: https://console.anthropic.com/")
        print("\n  2. OpenRouter API key (multiple models):")
        print("     $env:OPENCODE_API_KEY='your-api-key-here'")
        print("     Get key from: https://openrouter.ai/")
        print("\n  3. OpenCode API key (free models):")
        print("     $env:OPENCODE_API_KEY='your-api-key-here'")
        print("     Get key from: https://opencode.ai/auth")
        print("\n  3. OpenCode API key (free models):")
        print("     $env:OPENCODE_API_KEY='your-api-key-here'")
        print("     Get key from: https://opencode.ai/auth")
        return

    # Use project directory as specified
    project_dir = args.project_dir

    # Run the agent
    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()

