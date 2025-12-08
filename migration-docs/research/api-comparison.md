# OpenCode vs Claude Code SDK Comparison

## Architecture Differences

| Aspect | Claude Code SDK | OpenCode |
|--------|----------------|-----------|
| **Language** | Python | TypeScript/JavaScript |
| **Architecture** | Direct client | Client/Server |
| **Sessions** | Fresh client per session | Persistent sessions |
| **Security** | Bash hooks + sandbox | Permissions system |
| **Tools** | Predefined list | Extensible system |
| **Providers** | Anthropic only | Multi-provider |

## API Mapping

### Client Creation
**Claude SDK:**
```python
client = ClaudeSDKClient(
    options=ClaudeCodeOptions(
        model="claude-sonnet-4-5-20250929",
        cwd=str(project_dir)
    )
)
```

**OpenCode:**
```typescript
const { client } = await createOpencode({
  config: {
    model: "anthropic/claude-3-5-sonnet-20241022"
  }
})
```

### Sending Messages
**Claude SDK:**
```python
await client.query(message)
async for msg in client.receive_response():
    # Handle response
```

**OpenCode:**
```typescript
const result = await client.session.prompt({
  path: { id: session.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
    parts: [{ type: "text", text: message }]
  }
})
```

### Security Configuration
**Claude SDK:**
```python
security_settings = {
    "sandbox": {"enabled": True},
    "permissions": {
        "allow": ["Read(./**)", "Write(./**)", "Bash(*)"]
    },
    "hooks": {
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[bash_security_hook])
        ]
    }
}
```

**OpenCode:**
```typescript
// Configured via opencode.json or SDK config
{
  "permissions": {
    "allow": ["Read(./**)", "Write(./**)", "Bash(*)"]
  }
}
```

## Key Migration Challenges

### 1. Session Management
- **Claude**: Create new client for each session
- **OpenCode**: Create persistent sessions, reuse client

### 2. Security Model
- **Claude**: Bash hooks for command filtering
- **OpenCode**: Permission-based system

### 3. Response Handling
- **Claude**: Stream-based with async iteration
- **OpenCode**: Response-based with structured data

### 4. Tool Integration
- **Claude**: Built-in tools + MCP servers
- **OpenCode**: Configurable tool ecosystem

## Migration Strategy

### Phase 1: Foundation
- Set up TypeScript project
- Install OpenCode SDK
- Create basic client connection

### Phase 2: Core Migration
- Port client configuration
- Adapt security model
- Implement session management

### Phase 3: Agent Logic
- Migrate agent loop
- Adapt prompt system
- Implement error handling

### Phase 4: Testing & Polish
- Comprehensive testing
- Performance optimization
- Documentation updates