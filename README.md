# OpenCode Harness - Autonomous Coding Agent

An autonomous coding agent that uses OpenCode (Claude-powered IDE) to automatically build applications from specifications. The agent iteratively implements features, runs tests, and refines code until the application is complete.

## Features

- **Autonomous Development**: AI agent implements features independently
- **Test-Driven Development**: Works from a detailed feature list with test specifications
- **Multi-Model Support**: Works with Anthropic Claude, OpenRouter, and free models
- **Flexible Architecture**: Supports both provider/model and provider/vendor/model formats
- **Docker Integration**: OpenCode server runs in Docker with volume mounts
- **Progress Tracking**: Monitors feature completion across sessions
- **Security**: Bash command allowlist and filesystem restrictions

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Python Client  │────▶│  OpenCode Server │────▶│  LLM Provider   │
│  (agent.py)     │     │  (Docker)        │     │  (OpenRouter)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         └─────────────▶│  Project Dir     │
                        │  (Volume Mount)  │
                        └──────────────────┘
```

## Quick Start

### 1. Prerequisites

- Docker Desktop (for OpenCode server)
- Python 3.11+
- OpenRouter API Key (or Anthropic API Key)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start OpenCode Server

```bash
# With OpenRouter (recommended for free models)
docker run -d -p 4096:4096 \
  -e OPENROUTER_API_KEY='your-key-here' \
  -v "$(pwd)/your-project:/workspace" \
  --workdir /workspace \
  --name opencode-server \
  ghcr.io/sst/opencode serve --port 4096 --hostname 0.0.0.0

# Or with Anthropic (paid, higher quality)
docker run -d -p 4096:4096 \
  -e ANTHROPIC_API_KEY='your-key-here' \
  -v "$(pwd)/your-project:/workspace" \
  --workdir /workspace \
  --name opencode-server \
  ghcr.io/sst/opencode serve --port 4096 --hostname 0.0.0.0
```

### 4. Create Your App Specification

Create `prompts/app_spec.txt` with your application requirements:

```
Build a CLI Todo Application

Requirements:
- Add tasks with descriptions
- List all tasks with status
- Mark tasks as completed
- Store tasks in JSON file
- Python implementation
```

### 5. Run the Agent

```bash
# With free model (Google Gemini)
python autonomous_agent_demo.py \
  --project-dir ./my-app \
  --model openrouter/google/gemini-flash-1.5-8b:free

# With paid model (Claude)
python autonomous_agent_demo.py \
  --project-dir ./my-app \
  --model anthropic/claude-sonnet-4-5-20250929

# With OpenRouter + Claude
python autonomous_agent_demo.py \
  --project-dir ./my-app \
  --model openrouter/anthropic/claude-3.5-sonnet
```

## How It Works

1. **Initialization Phase**: Agent reads `app_spec.txt` and creates:
   - `feature_list.json` - Test cases for all features
   - `init.sh` - Setup script
   - Basic project structure

2. **Implementation Phase**: Agent iteratively:
   - Picks next unimplemented feature
   - Writes code and tests
   - Runs tests
   - Marks feature as passing when tests succeed

3. **Completion**: Continues until all features pass

## Configuration

### Model Selection

The agent supports flexible model formats:

```bash
# Format: provider/model
--model anthropic/claude-sonnet-4-5-20250929

# Format: provider/vendor/model  
--model openrouter/anthropic/claude-3.5-sonnet

# Free models
--model openrouter/google/gemini-flash-1.5-8b:free
--model openrouter/mistralai/mistral-7b-instruct:free
```

### Max Tokens

Configured automatically based on model:
- Free models: 1000 tokens
- Paid models: 4096 tokens

### Security

Edit `security.py` to customize:
- Bash command allowlist
- Filesystem restrictions
- Permission settings

## Project Structure

```
opencode_harness_autonomous_coding/
├── agent.py                    # Core agent logic
├── client.py                   # OpenCode client wrapper
├── autonomous_agent_demo.py    # Main entry point
├── prompts.py                  # Prompt management
├── security.py                 # Security configuration
├── prompts/
│   ├── app_spec.txt           # Your app specification
│   ├── initializer_prompt.md  # First-run prompt
│   └── coding_prompt.md       # Feature implementation prompt
├── tests/                      # Test suite
└── README.md
```

## API Keys

### OpenRouter (Recommended)

1. Sign up at https://openrouter.ai
2. Add credits: https://openrouter.ai/settings/credits
3. Create API key: https://openrouter.ai/settings/keys
4. Use in Docker: `-e OPENROUTER_API_KEY='sk-or-v1-...'`

**Note**: Free models require ~$5 minimum credits due to server-side `max_tokens` settings.

### Anthropic

1. Sign up at https://console.anthropic.com
2. Create API key: https://console.anthropic.com/settings/keys
3. Use in Docker: `-e ANTHROPIC_API_KEY='sk-ant-api03-...'`

## Troubleshooting

### "No API keys found"
- This warning is safe to ignore if your server has the key
- Keys are set in Docker container, not Python client

### "Connection error"
- Ensure OpenCode server is running: `docker ps`
- Check logs: `docker logs opencode-server`

### "Request requires more credits"
- Add credits to your OpenRouter account
- Or use a paid Anthropic API key

### Files created in wrong location
- Ensure Docker volume mount is correct: `-v "$(pwd)/project:/workspace"`
- Check `--workdir /workspace` is set

## Advanced Usage

### Custom Iteration Limit

```bash
python autonomous_agent_demo.py \
  --project-dir ./my-app \
  --model openrouter/google/gemini-flash-1.5-8b:free \
  --max-iterations 10
```

### Resume Existing Project

The agent automatically detects existing `feature_list.json` and continues from where it left off.

### Adjust Feature Count

Edit `prompts/initializer_prompt.md` to change the number of features generated (default: 3 for testing, increase for production).

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_agent.py::test_agent_session

# With coverage
pytest --cov=. --cov-report=html
```

### Code Style

- Follow PEP 8 conventions
- Type hints required
- Use async/await for OpenCode SDK calls
- See `AGENTS.md` for detailed guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

- Built on [OpenCode](https://opencode.ai) by SST
- Uses [Anthropic Claude](https://anthropic.com) and [OpenRouter](https://openrouter.ai)
- Python SDK: [opencode-ai](https://pypi.org/project/opencode-ai/)
