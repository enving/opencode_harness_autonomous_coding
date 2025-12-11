#!/usr/bin/env python3
"""
Direct Autonomous Coding Agent
================================

A minimal harness that bypasses OpenCode SDK and calls LLM APIs directly.
Provides full cost control and transparency.

Based on: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import os

# Using OpenAI SDK (compatible with OpenRouter)
from openai import AsyncOpenAI


class DirectTools:
    """Tool implementations that execute locally."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        
        # Security: Allowlist for bash commands
        self.allowed_commands = [
            "ls", "cat", "head", "tail", "wc", "grep", "pwd",
            "git", "npm", "node", "python", "pip",
            "mkdir", "touch", "echo", "find"
        ]
    
    def validate_command(self, command: str) -> bool:
        """Check if command starts with an allowed command."""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        return cmd_parts[0] in self.allowed_commands
    
    def bash(self, command: str) -> Dict[str, Any]:
        """Execute bash command with security checks."""
        if not self.validate_command(command):
            return {
                "success": False,
                "error": f"Command not allowed. Allowed: {', '.join(self.allowed_commands)}"
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """Read file content with path validation."""
        file_path = (self.project_dir / path).resolve()
        
        # Security: Ensure path is within project directory
        if not str(file_path).startswith(str(self.project_dir)):
            return {"success": False, "error": "Path outside project directory"}
        
        try:
            content = file_path.read_text()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write file content with path validation."""
        file_path = (self.project_dir / path).resolve()
        
        # Security: Ensure path is within project directory
        if not str(file_path).startswith(str(self.project_dir)):
            return {"success": False, "error": "Path outside project directory"}
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_dir(self, path: str = ".") -> Dict[str, Any]:
        """List directory contents."""
        dir_path = (self.project_dir / path).resolve()
        
        # Security: Ensure path is within project directory
        if not str(dir_path).startswith(str(self.project_dir)):
            return {"success": False, "error": "Path outside project directory"}
        
        try:
            files = [f.name for f in dir_path.iterdir()]
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}


class DirectAgent:
    """Autonomous coding agent with direct LLM API calls."""
    
    def __init__(
        self,
        project_dir: Path,
        model: str = "mistralai/mistral-7b-instruct:free",
        api_key: Optional[str] = None
    ):
        self.project_dir = project_dir
        self.model = model
        self.tools = DirectTools(project_dir)
        
        # Initialize OpenAI-compatible client for OpenRouter
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY required")
        
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Tool definitions for LLM
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Execute a bash command. Limited to allowlisted commands for security.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The bash command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file relative to project directory"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file relative to project directory"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "List contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to directory (default: current directory)"
                            }
                        }
                    }
                }
            }
        ]
        
        self.messages = []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return the result as a string."""
        print(f"[Tool: {tool_name}] {arguments}")
        
        tool_method = getattr(self.tools, tool_name, None)
        if not tool_method:
            return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})
        
        result = tool_method(**arguments)
        return json.dumps(result, indent=2)
    
    async def chat(self, user_message: str) -> str:
        """Send a message and get response, handling tool calls."""
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            print(f"\n[Iteration {iteration}] Calling {self.model}...")
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Add assistant message
            self.messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })
            
            # If no tool calls, we're done
            if not message.tool_calls:
                print(f"\n[Assistant]: {message.content}\n")
                return message.content or ""
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                tool_result = await self.execute_tool(function_name, function_args)
                
                # Add tool result to messages
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
        
        return "Max iterations reached"
    
    def reset(self):
        """Reset conversation history."""
        self.messages = []


async def main():
    """Demo of direct agent."""
    print("=" * 60)
    print("  DIRECT AUTONOMOUS CODING AGENT")
    print("=" * 60)
    print()
    
    # Setup
    project_dir = Path("./test4")
    project_dir.mkdir(exist_ok=True)
    
    # Initialize agent with FREE model
    agent = DirectAgent(
        project_dir=project_dir,
        model="mistralai/mistral-7b-instruct:free"  # GUARANTEED FREE
    )
    
    print(f"Project: {project_dir.resolve()}")
    print(f"Model: {agent.model}")
    print(f"Provider: OpenRouter (free tier)")
    print()
    
    # Test 1: Simple task
    print("=" * 60)
    print("  TEST 1: Create a simple Python file")
    print("=" * 60)
    
    response = await agent.chat(
        "Create a file called hello.py with a simple 'Hello World' script. "
        "Then list the directory contents to verify it was created."
    )
    
    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)
    print()
    print("Check OpenRouter logs at: https://openrouter.ai/activity")
    print("Verify the model used and cost.")


if __name__ == "__main__":
    asyncio.run(main())
