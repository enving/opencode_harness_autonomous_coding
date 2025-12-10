# AGENTS.md - OpenCode Harness Autonomous Coding



**Python:**
- `python -m pytest` - Run all tests
- `python -m pytest tests/test_file.py::test_name` - Run single test
- `python -m pytest -v` - Verbose test output

## Code Style Guidelines


**Python:**
- Follow PEP 8 conventions
- Type hints required for function signatures
- Use async/await for OpenCode SDK calls
- Import organization: stdlib → third-party → local

**Error Handling:**
- TypeScript: Use try/catch with proper error typing
- Python: Use try/except with specific exception types
- Always handle OpencodeError/AsyncOpencode errors

**Testing:**
- Jest for TypeScript (30s timeout)
- Pytest for Python
- Test files: *.test.ts, *.spec.ts, test_*.py