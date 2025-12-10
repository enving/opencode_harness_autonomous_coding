# AGENTS.md - OpenCode Harness Autonomous Coding

## 🔧 BUILD/LINT/TEST COMMANDS

### Build & Install
```bash
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
pytest

# Run single test
pytest tests/test_file.py::test_function

# With coverage
pytest --cov=. --cov-report=html
```

### Linting & Formatting
```bash
# Type checking
mypy .

# Linting
pylint **/*.py

# Formatting
black .
```

## 📝 CODE STYLE GUIDELINES

### Python
- **Imports**: stdlib → third-party → local (sorted alphabetically)
- **Type Hints**: Required for all function signatures
- **Formatting**: Follow PEP 8 conventions
- **Async/Await**: Use for all OpenCode SDK calls
- **Naming**: snake_case for variables/functions, CamelCase for classes

### Error Handling
- Use try/except with specific exception types
- Handle OpencodeError/AsyncOpencode errors explicitly
- Log all API errors with full traceback
- Never expose sensitive information in error messages

### Testing
- **Framework**: Pytest
- **File Naming**: test_*.py
- **Test Functions**: test_* prefix
- **Coverage**: Aim for 80%+ coverage
- **Single Test**: `pytest tests/test_file.py::test_function -v`

### Security
- Validate all user inputs
- Use allowlists for bash commands
- Restrict filesystem access
- Never log API keys or sensitive data

### Documentation
- Use Google-style docstrings
- Document all public functions/classes
- Keep README.md updated with usage examples
- Use type hints as primary documentation

## 🎯 CURRENT PRIORITIES

1. **Cost Control**: Ensure only free models are used
2. **Session Continuation**: Fix feature_list.json detection
3. **Auto-Continue**: Implement continuous feature implementation
4. **Testing**: Add comprehensive test coverage

## 📚 RESOURCES

- OpenRouter Free Models: https://openrouter.ai/models?pricing=free
- OpenCode Python SDK: https://github.com/opencode-ai/opencode-python
- PEP 8 Style Guide: https://peps.python.org/pep-0008/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
