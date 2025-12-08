# 🎉 OpenCode Autonomous Coding Agent - Migration Complete!

A minimal harness demonstrating long-running autonomous coding with OpenCode Python SDK. This demo implements a two-agent pattern (initializer + coding agent) that can build complete applications over multiple sessions.

## ✅ Migration Complete: Claude Code SDK → OpenCode Python SDK!

**Successfully migrated from Claude Code SDK to official OpenCode Python SDK while maintaining 100% functionality and staying in Python!**

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run the agent
python autonomous_agent_demo.py --project-dir ./my_project
```

For testing with limited iterations:
```bash
python src/autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

## Project Structure

```
opencode-harness-autonomous-coding/
├── src/
│   ├── agent.py              # OpenCode agent session logic
│   ├── client.py             # OpenCode client configuration
│   ├── security.py           # Security rules and permissions
│   ├── progress.py           # Progress tracking utilities
│   ├── prompts.py            # Prompt loading utilities
│   ├── autonomous_agent_demo.py # Main entry point
│   ├── requirements.txt       # Python dependencies
│   ├── tests/               # Test files
│   └── [config files]       # TypeScript/Node.js configs (legacy)
├── prompts/                 # Agent prompts
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── legacy/                  # Original Claude SDK files
└── migration-docs/          # Migration documentation
```

## Important Timing Expectations

> **Warning: This demo takes a long time to run!**

- **First session (initialization):** The agent generates a `feature_list.json` with 200 test cases. This takes several minutes and may appear to hang - this is normal. The agent is writing out all the features.

- **Subsequent sessions:** Each coding iteration can take **5-15 minutes** depending on complexity.

- **Full app:** Building all 200 features typically requires **many hours** of total runtime across multiple sessions.

## How It Works

### Two-Agent Pattern

1. **Initializer Agent (Session 1):** Reads `app_spec.txt`, creates `feature_list.json` with 200 test cases, sets up project structure, and initializes git.

2. **Coding Agent (Sessions 2+):** Picks up where the previous session left off, implements features one by one, and marks them as passing in `feature_list.json`.

### Session Management

- Each session runs with a fresh context window
- Progress is persisted via `feature_list.json` and git commits
- The agent auto-continues between sessions (3 second delay)
- Press `Ctrl+C` to pause; run the same command to resume

## Security Model

This demo uses a defense-in-depth security approach:

1. **Permissions:** File operations restricted to project directory only
2. **Bash Allowlist:** Only specific commands are permitted:
   - File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `grep`
   - Node.js: `npm`, `node`
   - Version control: `git`
   - Process management: `ps`, `lsof`, `sleep`, `pkill` (dev processes only)

Commands not in the allowlist are blocked by the security system.

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the project | `./autonomous_demo_project` |
| `--max-iterations` | Max agent iterations | Unlimited |
| `--model` | OpenCode model to use | `anthropic/claude-3-5-sonnet-20241022` |

## Running the Generated Application

After the agent completes (or pauses), you can run the generated application:

```bash
cd my_project

# Run the setup script created by the agent
./init.sh

# Or manually (typical for Node.js apps):
npm install
npm run dev
```

The application will typically be available at `http://localhost:3000` or similar (check the agent's output or `init.sh` for the exact URL).

## Migration from Claude Code SDK

This repository was successfully migrated from Claude Code SDK to OpenCode Python SDK. Key changes:

- **SDK:** `claude-code-sdk` → `opencode-ai`
- **Session Management:** Direct queries → OpenCode sessions
- **Security:** Bash hooks → OpenCode permissions
- **API:** Different response format and error handling

All original functionality is preserved while gaining OpenCode's multi-provider support and modern architecture.

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r src/requirements.txt

# Run tests
python -m pytest src/tests/

# Lint code
python -m flake8 src/

# Format code
python -m black src/
```

### Architecture

- **agent.py:** Core agent interaction with OpenCode sessions
- **client.py:** OpenCode client configuration and security
- **security.py:** Bash command validation and permissions
- **progress.py:** Progress tracking and user feedback
- **prompts.py:** Prompt template management

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read the migration documentation in `migration-docs/` for context on the project's evolution.