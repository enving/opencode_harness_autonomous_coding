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
DEFAULT_MODEL = "anthropic/claude-3-5-sonnet-20241022"


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
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
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

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nGet your API key from: https://console.anthropic.com/")
        print("\nThen set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
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