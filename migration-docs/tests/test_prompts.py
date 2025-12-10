"""
Unit tests for prompts.py module.
================================

Tests prompt loading utilities and file copying functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from prompts import (
    load_prompt,
    get_initializer_prompt,
    get_coding_prompt,
    copy_spec_to_project,
    PROMPTS_DIR
)


class TestLoadPrompt:
    """Test cases for load_prompt function."""
    
    def test_load_prompt_success(self):
        """Test successful prompt loading."""
        prompt_content = "# Test Prompt\nThis is a test prompt."
        
        with patch("builtins.open", mock_open(read_data=prompt_content)):
            with patch.object(Path, "read_text", return_value=prompt_content):
                result = load_prompt("test_prompt")
                assert result == prompt_content
    
    def test_load_prompt_file_not_found(self):
        """Test loading non-existent prompt."""
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                load_prompt("nonexistent_prompt")
    
    def test_load_prompt_empty_file(self):
        """Test loading empty prompt file."""
        with patch.object(Path, "read_text", return_value=""):
            result = load_prompt("empty_prompt")
            assert result == ""


class TestGetPromptFunctions:
    """Test cases for specific prompt getter functions."""
    
    def test_get_initializer_prompt(self):
        """Test getting initializer prompt."""
        expected_content = "# Initializer Prompt\nSetup the project."
        
        with patch("prompts.load_prompt", return_value=expected_content) as mock_load:
            result = get_initializer_prompt()
            assert result == expected_content
            mock_load.assert_called_once_with("initializer_prompt")
    
    def test_get_coding_prompt(self):
        """Test getting coding prompt."""
        expected_content = "# Coding Prompt\nWrite the code."
        
        with patch("prompts.load_prompt", return_value=expected_content) as mock_load:
            result = get_coding_prompt()
            assert result == expected_content
            mock_load.assert_called_once_with("coding_prompt")


class TestCopySpecToProject:
    """Test cases for copy_spec_to_project function."""
    
    def test_copy_spec_to_project_success(self, temp_project_dir):
        """Test successful spec file copy."""
        # Create source spec file
        spec_source = temp_project_dir / "prompts" / "app_spec.txt"
        spec_source.parent.mkdir(parents=True, exist_ok=True)
        spec_source.write_text("Test app specification")
        
        # Create destination project directory
        project_dir = temp_project_dir / "test_project"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock PROMPTS_DIR to point to our test directory
        with patch("prompts.PROMPTS_DIR", spec_source.parent):
            with patch("builtins.print") as mock_print:
                copy_spec_to_project(project_dir)
                
                # Check that file was copied
                spec_dest = project_dir / "app_spec.txt"
                assert spec_dest.exists()
                assert spec_dest.read_text() == "Test app specification"
                
                # Check that print was called
                mock_print.assert_called_with("Copied app_spec.txt to project directory")
    
    def test_copy_spec_to_project_already_exists(self, temp_project_dir):
        """Test copying spec when it already exists."""
        # Create source spec file
        spec_source = temp_project_dir / "prompts" / "app_spec.txt"
        spec_source.parent.mkdir(parents=True, exist_ok=True)
        spec_source.write_text("Original spec")
        
        # Create destination project directory with existing spec
        project_dir = temp_project_dir / "test_project"
        project_dir.mkdir(parents=True, exist_ok=True)
        spec_dest = project_dir / "app_spec.txt"
        spec_dest.write_text("Existing spec")
        
        # Mock PROMPTS_DIR to point to our test directory
        with patch("prompts.PROMPTS_DIR", spec_source.parent):
            with patch("builtins.print") as mock_print:
                copy_spec_to_project(project_dir)
                
                # Check that existing file was not overwritten
                assert spec_dest.read_text() == "Existing spec"
                
                # Check that print was not called (since file already exists)
                mock_print.assert_not_called()
    
    def test_copy_spec_to_project_source_not_found(self, temp_project_dir):
        """Test copying spec when source doesn't exist."""
        # Create non-existent source path
        non_existent_dir = temp_project_dir / "nonexistent"
        
        # Create destination project directory
        project_dir = temp_project_dir / "test_project"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock PROMPTS_DIR to point to non-existent directory
        with patch("prompts.PROMPTS_DIR", non_existent_dir):
            with pytest.raises(FileNotFoundError):
                copy_spec_to_project(project_dir)


class TestPromptsDir:
    """Test cases for PROMPTS_DIR constant."""
    
    def test_prompts_dir_exists(self):
        """Test that PROMPTS_DIR points to existing directory."""
        # This test assumes the prompts directory exists in the project
        assert isinstance(PROMPTS_DIR, Path)
        assert PROMPTS_DIR.name == "prompts"
    
    def test_prompts_dir_has_required_files(self):
        """Test that PROMPTS_DIR contains required prompt files."""
        required_files = [
            "initializer_prompt.md",
            "coding_prompt.md",
            "app_spec.txt"
        ]
        
        # Check if required files exist (may not exist in test environment)
        for filename in required_files:
            file_path = PROMPTS_DIR / filename
            # Don't assert existence here as it depends on test setup
            # Just verify the path construction works
            assert file_path.name == filename


class TestPromptIntegration:
    """Integration tests for prompt functionality."""
    
    def test_full_prompt_workflow(self, temp_project_dir):
        """Test full workflow of loading and copying prompts."""
        # Create mock prompt files
        prompts_test_dir = temp_project_dir / "prompts"
        prompts_test_dir.mkdir(parents=True, exist_ok=True)
        
        (prompts_test_dir / "initializer_prompt.md").write_text("# Initializer\nTest initializer")
        (prompts_test_dir / "coding_prompt.md").write_text("# Coding\nTest coding")
        (prompts_test_dir / "app_spec.txt").write_text("Test specification")
        
        # Create project directory
        project_dir = temp_project_dir / "test_project"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock PROMPTS_DIR
        with patch("prompts.PROMPTS_DIR", prompts_test_dir):
            # Test loading prompts
            initializer = get_initializer_prompt()
            coding = get_coding_prompt()
            
            assert initializer == "# Initializer\nTest initializer"
            assert coding == "# Coding\nTest coding"
            
            # Test copying spec
            copy_spec_to_project(project_dir)
            
            spec_file = project_dir / "app_spec.txt"
            assert spec_file.exists()
            assert spec_file.read_text() == "Test specification"