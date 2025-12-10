"""
Unit tests for security.py module.
================================

Tests security validation functions, command allowlist, and bash security hooks.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from security import (
    ALLOWED_COMMANDS,
    COMMANDS_NEEDING_EXTRA_VALIDATION,
    split_command_segments,
    extract_commands,
    validate_pkill_command,
    validate_chmod_command,
    validate_init_script,
    bash_security_hook,
    get_opencode_permissions
)


class TestCommandExtraction:
    """Test cases for command extraction functions."""
    
    def test_extract_simple_commands(self):
        """Test extracting simple commands."""
        commands = extract_commands("ls -la")
        assert commands == ["ls"]
        
        commands = extract_commands("cat file.txt")
        assert commands == ["cat"]
    
    def test_extract_commands_with_pipes(self):
        """Test extracting commands with pipes."""
        commands = extract_commands("ls -la | grep test")
        assert commands == ["ls", "grep"]
        
        commands = extract_commands("cat file.txt | head -10 | tail -5")
        assert commands == ["cat", "head", "tail"]
    
    def test_extract_commands_with_chaining(self):
        """Test extracting commands with chaining operators."""
        commands = extract_commands("ls && echo done")
        assert commands == ["ls", "echo"]
        
        commands = extract_commands("ls || echo failed")
        assert commands == ["ls", "echo"]
        
        commands = extract_commands("ls; echo next")
        assert commands == ["ls", "echo"]
    
    def test_extract_commands_with_paths(self):
        """Test extracting commands with full paths."""
        commands = extract_commands("/usr/bin/python script.py")
        assert commands == ["python"]
        
        commands = extract_commands("./script.sh")
        assert commands == ["script.sh"]
    
    def test_extract_commands_with_variables(self):
        """Test extracting commands with variable assignments."""
        commands = extract_commands("VAR=value command")
        assert commands == ["command"]
        
        commands = extract_commands("VAR=value && command")
        assert commands == ["command"]
    
    def test_extract_commands_with_quotes(self):
        """Test extracting commands with quotes."""
        commands = extract_commands('echo "hello world"')
        assert commands == ["echo"]
        
        commands = extract_commands("echo 'hello world'")
        assert commands == ["echo"]
    
    def test_extract_commands_malformed(self):
        """Test extracting commands from malformed strings."""
        commands = extract_commands('echo "unclosed quote')
        assert commands == []  # Should return empty for malformed input


class TestCommandSegmentation:
    """Test cases for command segmentation function."""
    
    def test_split_simple_commands(self):
        """Test splitting simple command chains."""
        segments = split_command_segments("ls && echo done")
        assert segments == ["ls", "echo done"]
        
        segments = split_command_segments("ls || echo failed")
        assert segments == ["ls", "echo failed"]
        
        segments = split_command_segments("ls; echo next")
        assert segments == ["ls", "echo next"]
    
    def test_split_complex_chains(self):
        """Test splitting complex command chains."""
        segments = split_command_segments("ls && echo step1 || echo step2; echo final")
        assert segments == ["ls", "echo step1", "echo step2", "echo final"]
    
    def test_split_with_pipes(self):
        """Test splitting commands with pipes (should not split pipes)."""
        segments = split_command_segments("ls | grep test && echo found")
        assert segments == ["ls | grep test", "echo found"]


class TestPkillValidation:
    """Test cases for pkill command validation."""
    
    def test_validate_pkill_allowed_processes(self):
        """Test pkill validation for allowed processes."""
        allowed, reason = validate_pkill_command("pkill node")
        assert allowed is True
        assert reason == ""
        
        allowed, reason = validate_pkill_command("pkill npm")
        assert allowed is True
        
        allowed, reason = validate_pkill_command("pkill vite")
        assert allowed is True
    
    def test_validate_pkill_with_flags(self):
        """Test pkill validation with flags."""
        allowed, reason = validate_pkill_command("pkill -f node server.js")
        assert allowed is True
        
        allowed, reason = validate_pkill_command("pkill -SIGTERM node")
        assert allowed is True
    
    def test_validate_pkill_blocked_processes(self):
        """Test pkill validation for blocked processes."""
        allowed, reason = validate_pkill_command("pkill python")
        assert allowed is False
        assert "dev processes" in reason
        
        allowed, reason = validate_pkill_command("pkill bash")
        assert allowed is False
    
    def test_validate_pkill_no_target(self):
        """Test pkill validation with no target."""
        allowed, reason = validate_pkill_command("pkill")
        assert allowed is False
        assert "requires a process name" in reason
    
    def test_validate_pkill_malformed(self):
        """Test pkill validation with malformed command."""
        allowed, reason = validate_pkill_command('pkill "unclosed quote')
        assert allowed is False
        assert "Could not parse" in reason


class TestChmodValidation:
    """Test cases for chmod command validation."""
    
    def test_validate_chmod_allowed_modes(self):
        """Test chmod validation for allowed modes."""
        allowed, reason = validate_chmod_command("chmod +x script.sh")
        assert allowed is True
        
        allowed, reason = validate_chmod_command("chmod u+x script.sh")
        assert allowed is True
        
        allowed, reason = validate_chmod_command("chmod a+x script.sh")
        assert allowed is True
        
        allowed, reason = validate_chmod_command("chmod ug+x script.sh")
        assert allowed is True
    
    def test_validate_chmod_blocked_modes(self):
        """Test chmod validation for blocked modes."""
        allowed, reason = validate_chmod_command("chmod 755 script.sh")
        assert allowed is False
        assert "+x mode" in reason
        
        allowed, reason = validate_chmod_command("chmod -x script.sh")
        assert allowed is False
        
        allowed, reason = validate_chmod_command("chmod u+w script.sh")
        assert allowed is False
    
    def test_validate_chmod_no_files(self):
        """Test chmod validation with no files."""
        allowed, reason = validate_chmod_command("chmod +x")
        assert allowed is False
        assert "requires at least one file" in reason
    
    def test_validate_chmod_with_flags(self):
        """Test chmod validation with flags."""
        allowed, reason = validate_chmod_command("chmod -R +x dir/")
        assert allowed is False
        assert "flags are not allowed" in reason


class TestInitScriptValidation:
    """Test cases for init script validation."""
    
    def test_validate_init_script_allowed(self):
        """Test init script validation for allowed commands."""
        allowed, reason = validate_init_script("./init.sh")
        assert allowed is True
        
        allowed, reason = validate_init_script("path/to/init.sh")
        assert allowed is True
        
        allowed, reason = validate_init_script("./init.sh arg1 arg2")
        assert allowed is True
    
    def test_validate_init_script_blocked(self):
        """Test init script validation for blocked commands."""
        allowed, reason = validate_init_script("init.sh")
        assert allowed is False
        assert "Only ./init.sh is allowed" in reason
        
        allowed, reason = validate_init_script("other.sh")
        assert allowed is False
        
        allowed, reason = validate_init_script("/bin/bash init.sh")
        assert allowed is False


class TestBashSecurityHook:
    """Test cases for bash security hook."""
    
    def test_bash_security_hook_non_bash_tool(self):
        """Test security hook with non-bash tool."""
        input_data = {"tool_name": "Read", "tool_input": {"path": "file.txt"}}
        result = bash_security_hook(input_data)
        assert result == {}  # Should allow non-bash tools
    
    def test_bash_security_hook_empty_command(self):
        """Test security hook with empty command."""
        input_data = {"tool_name": "Bash", "tool_input": {}}
        result = bash_security_hook(input_data)
        assert result == {}  # Should allow empty command
    
    def test_bash_security_hook_allowed_commands(self):
        """Test security hook with allowed commands."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"}
        }
        result = bash_security_hook(input_data)
        assert result == {}  # Should allow
    
    def test_bash_security_hook_blocked_commands(self):
        """Test security hook with blocked commands."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf file.txt"}
        }
        result = bash_security_hook(input_data)
        assert result["decision"] == "block"
        assert "not in the allowed commands list" in result["reason"]
    
    def test_bash_security_hook_malformed_command(self):
        """Test security hook with malformed command."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": 'echo "unclosed quote'}
        }
        result = bash_security_hook(input_data)
        assert result["decision"] == "block"
        assert "Could not parse command" in result["reason"]
    
    def test_bash_security_hook_pkill_validation(self):
        """Test security hook with pkill requiring extra validation."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "pkill python"}
        }
        result = bash_security_hook(input_data)
        assert result["decision"] == "block"
        assert "dev processes" in result["reason"]
    
    def test_bash_security_hook_chmod_validation(self):
        """Test security hook with chmod requiring extra validation."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "chmod 755 script.sh"}
        }
        result = bash_security_hook(input_data)
        assert result["decision"] == "block"
        assert "+x mode" in result["reason"]
    
    def test_bash_security_hook_init_script_validation(self):
        """Test security hook with init script requiring extra validation."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "other.sh"}
        }
        result = bash_security_hook(input_data)
        assert result["decision"] == "block"
        assert "Only ./init.sh is allowed" in result["reason"]


class TestOpenCodePermissions:
    """Test cases for OpenCode permissions configuration."""
    
    def test_get_opencode_permissions(self):
        """Test OpenCode permissions generation."""
        project_dir = Path("/test/project")
        permissions = get_opencode_permissions(project_dir)
        
        assert "allow" in permissions
        assert "defaultMode" in permissions
        assert permissions["defaultMode"] == "acceptEdits"
        
        # Check that all required permissions are present
        allow_list = permissions["allow"]
        project_path = project_dir.resolve()
        
        assert any(f"Read({project_path}/**)" in perm for perm in allow_list)
        assert any(f"Write({project_path}/**)" in perm for perm in allow_list)
        assert any(f"Edit({project_path}/**)" in perm for perm in allow_list)
        assert any(f"Glob({project_path}/**)" in perm for perm in allow_list)
        assert any(f"Grep({project_path}/**)" in perm for perm in allow_list)
        assert "Bash(*)" in allow_list


class TestSecurityConstants:
    """Test cases for security constants."""
    
    def test_allowed_commands_not_empty(self):
        """Test that allowed commands are defined."""
        assert len(ALLOWED_COMMANDS) > 0
        assert "ls" in ALLOWED_COMMANDS
        assert "cat" in ALLOWED_COMMANDS
        assert "npm" in ALLOWED_COMMANDS
    
    def test_commands_needing_validation_subset(self):
        """Test that commands needing extra validation are in allowed commands."""
        for cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            assert cmd in ALLOWED_COMMANDS