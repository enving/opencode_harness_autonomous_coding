"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt")


def get_coding_prompt(project_dir: Path = None) -> str:
    """Load the coding agent prompt with project directory context."""
    prompt = load_prompt("coding_prompt")
    
    # Add project directory context if provided
    if project_dir:
        context = f"\n\n**IMPORTANT: Your working directory is: `{project_dir.resolve()}`**\n"
        context += f"All files (app_spec.txt, feature_list.json, etc.) are in this directory.\n"
        context += f"Use this path when reading/writing files.\n\n"
        prompt = context + prompt
    
    return prompt


def copy_spec_to_project(project_dir: Path) -> None:
    """Copy the app spec file into the project directory for the agent to read."""
    spec_source = PROMPTS_DIR / "app_spec.txt"
    spec_dest = project_dir / "app_spec.txt"
    if not spec_dest.exists():
        shutil.copy(spec_source, spec_dest)
        print("Copied app_spec.txt to project directory")
