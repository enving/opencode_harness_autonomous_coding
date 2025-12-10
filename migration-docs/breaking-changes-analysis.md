# Breaking Changes & Compatibility Analysis

## Executive Summary

This document identifies breaking changes and compatibility issues when migrating from legacy OpenAI/Claude SDK to OpenCode SDK. The analysis covers API differences, data structure changes, and migration strategies.

## Critical Breaking Changes

### 1. Client Initialization & Authentication

#### Legacy (Claude SDK)
```python
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

client = ClaudeSDKClient(
    options=ClaudeCodeOptions(
        model=model,
        api_key=api_key,
        cwd=str(project_dir.resolve())
    )
)
```

#### OpenCode SDK
```python
from opencode_ai import AsyncOpencode

client = AsyncOpencode(
    base_url="http://localhost:4096"
)
# Authentication handled via environment variables or auth.set()
```

**Breaking Changes**:
- ✅ **Simpler initialization**: No complex options object
- ✅ **Separate auth**: Authentication handled independently
- ⚠️ **Server dependency**: Requires running OpenCode server
- ⚠️ **Base URL required**: Must specify server location

### 2. Session Management

#### Legacy (Claude SDK)
```python
# Implicit session management
async with client:
    await client.query(message)
    async for msg in client.receive_response():
        # Handle response
```

#### OpenCode SDK
```python
# Explicit session management
session = await client.session.create({
    "title": "My Session",
    "cwd": str(project_dir.resolve())
})

result = await client.session.chat(
    session.id,
    model_id="claude-3-5-sonnet",
    provider_id="anthropic",
    parts=[{"type": "text", "text": message}]
)
```

**Breaking Changes**:
- ✅ **Explicit sessions**: Better session control and persistence
- ⚠️ **Manual lifecycle**: Must create/manage sessions explicitly
- ⚠️ **Different API**: `query()` → `session.chat()`
- ⚠️ **Response structure**: Different response format

### 3. Response Handling

#### Legacy (Claude SDK)
```python
async for msg in client.receive_response():
    msg_type = type(msg).__name__
    
    if msg_type == "AssistantMessage":
        for block in msg.content:
            if type(block).__name__ == "TextBlock":
                print(block.text)
            elif type(block).__name__ == "ToolUseBlock":
                print(f"[Tool: {block.name}]")
```

#### OpenCode SDK
```python
result = await client.session.chat(...)
response_text = ""

if hasattr(result, 'content'):
    for part in result.content:
        if hasattr(part, 'text'):
            response_text += part.text
            print(part.text, end="", flush=True)
        elif hasattr(part, 'type') and part.type == 'tool_use':
            print(f"\n[Tool: {part.name}]", flush=True)
```

**Breaking Changes**:
- ⚠️ **Single response**: No streaming response iterator
- ⚠️ **Different structure**: `msg.content` → `result.content`
- ⚠️ **Block types**: `TextBlock` → generic `part` with `text` attribute
- ⚠️ **Tool use detection**: Different type checking logic

### 4. Security Model

#### Legacy (Claude SDK)
```python
security_settings = {
    "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
    "permissions": {
        "defaultMode": "acceptEdits",
        "allow": [
            "Read(./**)",
            "Write(./**)",
            "Edit(./**)",
            "Bash(*)",
        ],
    },
}

hooks = {
    "PreToolUse": [
        HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
    ],
}
```

#### OpenCode SDK
```python
opencode_config = {
    "model": model_strategy,
    "permissions": get_opencode_permissions(project_dir),
    "security": {
        "bash_allowlist": [
            "ls", "cat", "head", "tail", "wc", "grep",
            "npm", "node", "git", "ps", "lsof", "sleep", "pkill"
        ]
    }
}

# Written to .opencode_settings.json
```

**Breaking Changes**:
- ✅ **Simplified permissions**: More straightforward permission model
- ✅ **JSON configuration**: File-based configuration instead of code
- ⚠️ **No hooks system**: PreToolUse hooks not available
- ⚠️ **Different sandbox**: OpenCode handles sandboxing differently

### 5. Model Selection

#### Legacy (Claude SDK)
```python
client = ClaudeSDKClient(
    options=ClaudeCodeOptions(
        model="claude-3-5-sonnet-20241022"  # Direct model name
    )
)
```

#### OpenCode SDK
```python
# Multi-provider support
result = await client.session.chat(
    session_id,
    model_id="claude-3-5-sonnet",
    provider_id="anthropic",  # Required provider specification
    parts=[{"type": "text", "text": message}]
)

# Or with auto-selection
model_strategy = "openrouter/anthropic/claude-3.5-sonnet"
```

**Breaking Changes**:
- ✅ **Multi-provider**: Support for OpenRouter, Anthropic, etc.
- ⚠️ **Provider required**: Must specify both provider and model
- ⚠️ **Different naming**: Model names may differ between providers
- ⚠️ **Auto-selection**: New auto-selection logic needed

## Compatibility Issues

### 1. Import Dependencies

#### Legacy Imports
```python
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
from claude_code_sdk.types import HookMatcher
```

#### OpenCode Imports
```python
from opencode_ai import AsyncOpencode
# No HookMatcher equivalent
```

**Impact**: Complete rewrite of import statements and dependency management.

### 2. Error Handling

#### Legacy (Claude SDK)
```python
try:
    await client.query(message)
    async for msg in client.receive_response():
        # Handle response
except Exception as e:
    print(f"Error during agent session: {e}")
    return "error", str(e)
```

#### OpenCode SDK
```python
try:
    result = await client.session.chat(...)
    # Handle response
except Exception as e:
    print(f"❌ Failed to send prompt: {e}")
    raise  # Different error handling strategy
```

**Impact**: Error types and handling patterns need to be updated.

### 3. Configuration Management

#### Legacy (Claude SDK)
```python
# Code-based configuration
options = ClaudeCodeOptions(
    model=model,
    system_prompt="You are an expert...",
    allowed_tools=[...],
    mcp_servers={...},
    hooks={...},
    max_turns=1000,
    cwd=str(project_dir.resolve()),
    settings=str(settings_file.resolve())
)
```

#### OpenCode SDK
```python
# File-based configuration
config_file = project_dir / ".opencode_settings.json"
opencode_config = {
    "model": model_strategy,
    "permissions": get_opencode_permissions(project_dir),
    "security": {"bash_allowlist": [...]}
}

with open(config_file, "w") as f:
    json.dump(opencode_config, f, indent=2)
```

**Impact**: Configuration approach changes from code to JSON file-based.

## Migration Strategies

### 1. Adapter Pattern for Compatibility

Create compatibility layers to minimize code changes:

```python
class OpenCodeAdapter:
    def __init__(self, project_dir: Path, model: str):
        self.client = AsyncOpencode()
        self.project_dir = project_dir
        self.model = model
        self.session_id = None
    
    async def query(self, message: str):
        """Adapter method to mimic legacy query()"""
        if not self.session_id:
            await self._create_session()
        
        return await self.client.session.chat(
            self.session_id,
            model_id=self._get_model_id(),
            provider_id=self._get_provider_id(),
            parts=[{"type": "text", "text": message}]
        )
    
    async def receive_response(self):
        """Adapter to mimic streaming response"""
        # Convert single response to iterator
        result = await self.last_result
        yield result
```

### 2. Gradual Migration Approach

Phase 1: Core Infrastructure
- Migrate client initialization
- Update session management
- Implement basic error handling

Phase 2: Response Handling
- Update response parsing logic
- Migrate tool use detection
- Update progress tracking

Phase 3: Security & Configuration
- Migrate security model
- Update configuration management
- Implement permission system

Phase 4: Advanced Features
- Optimize model selection
- Enhance error handling
- Add monitoring and logging

### 3. Feature Flags for Transition

```python
USE_OPENCODE_SDK = os.environ.get("USE_OPENCODE_SDK", "true").lower() == "true"

if USE_OPENCODE_SDK:
    from opencode_client import OpenCodeClient as Client
else:
    from claude_client import ClaudeClient as Client
```

## Risk Assessment

### High-Risk Areas

1. **Session Management Complexity**
   - Risk: Session lifecycle management errors
   - Mitigation: Implement robust session tracking and cleanup

2. **Response Format Changes**
   - Risk: Broken response parsing logic
   - Mitigation: Create comprehensive response adapters

3. **Security Model Differences**
   - Risk: Security regressions or permission issues
   - Mitigation: Thorough security testing and validation

### Medium-Risk Areas

1. **Error Handling Patterns**
   - Risk: Inconsistent error handling
   - Mitigation: Standardize error handling patterns

2. **Configuration Management**
   - Risk: Configuration migration issues
   - Mitigation: Automated configuration migration tools

### Low-Risk Areas

1. **Import Statement Updates**
   - Risk: Minor import issues
   - Mitigation: Automated import updating

2. **Naming Convention Changes**
   - Risk: Minor naming inconsistencies
   - Mitigation: Clear naming convention documentation

## Testing Strategy

### 1. Unit Testing

```python
# Test adapter compatibility
async def test_adapter_query():
    adapter = OpenCodeAdapter(test_project_dir, "auto")
    response = await adapter.query("test message")
    assert response is not None

# Test session management
async def test_session_lifecycle():
    client = AsyncOpencode()
    session = await client.session.create({...})
    assert session.id is not None
    await client.session.delete({"id": session.id})
```

### 2. Integration Testing

```python
# Test complete workflow
async def test_autonomous_agent_workflow():
    result = await run_autonomous_agent(
        project_dir=test_project_dir,
        model="auto",
        max_iterations=1
    )
    assert result is not None
```

### 3. Compatibility Testing

```python
# Test parity between implementations
async def test_response_parity():
    legacy_response = await legacy_client.query(message)
    opencode_response = await opencode_client.query(message)
    
    # Compare key aspects of responses
    assert compare_responses(legacy_response, opencode_response)
```

## Rollback Plan

### 1. Version Control Strategy
- Maintain separate branches for legacy and new implementations
- Use feature flags for runtime switching
- Keep legacy code as fallback during transition

### 2. Configuration Backup
- Backup all configuration files
- Maintain migration scripts for rollback
- Document configuration differences

### 3. Monitoring & Alerting
- Monitor key metrics during migration
- Set up alerts for regression detection
- Implement gradual rollout with monitoring

## Timeline & Milestones

### Week 1: Foundation (High Risk)
- [ ] Client initialization migration
- [ ] Basic session management
- [ ] Error handling framework

### Week 2: Core Logic (Medium Risk)
- [ ] Response handling migration
- [ ] Tool use detection
- [ ] Progress tracking updates

### Week 3: Security & Config (Medium Risk)
- [ ] Security model migration
- [ ] Configuration management
- [ ] Permission system implementation

### Week 4: Validation (Low Risk)
- [ ] Comprehensive testing
- [ ] Performance validation
- [ ] Documentation updates

## Success Criteria

### Functional Requirements
- [ ] 100% feature parity with legacy implementation
- [ ] All existing tests pass
- [ ] No security regressions
- [ ] Performance maintained or improved

### Technical Requirements
- [ ] Clean, maintainable code
- [ ] Comprehensive test coverage
- [ ] Proper error handling
- [ ] Clear documentation

### Operational Requirements
- [ ] Smooth deployment process
- [ ] Monitoring and alerting
- [ ] Rollback capability
- [ ] User communication plan

---

**Risk Level**: Medium (with proper mitigation)  
**Migration Complexity**: High (significant API changes)  
**Success Probability**: High (with thorough planning and testing)