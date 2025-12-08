# OpenCode API Research

## Session Management

### Creating a Session
```typescript
const session = await client.session.create({
  body: { 
    title: "My session" 
  }
})
```

### Sending a Prompt
```typescript
const result = await client.session.prompt({
  path: { id: session.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
    parts: [{ type: "text", text: "Hello!" }]
  }
})
```

### Session Messages
```typescript
const messages = await client.session.messages({
  path: { id: session.id }
})
```

## Security Model

### Permissions
- File operations: `Read(./**)`, `Write(./**)`, `Edit(./**)`
- Tools: `Bash(*)`, `Glob(./**)`, `Grep(./**)`
- MCP servers: Configurable per server

### Key Differences from Claude SDK
- No built-in bash hooks - use permissions system
- Session-based instead of client-per-session
- More granular tool control

## File Operations

### Reading Files
```typescript
const content = await client.file.read({
  query: { path: "src/index.ts" }
})
```

### Finding Files
```typescript
const files = await client.find.files({
  query: { query: "*.ts" }
})
```

### Searching Text
```typescript
const results = await client.find.text({
  query: { pattern: "function.*opencode" }
})
```

## Configuration

### Client Creation
```typescript
import { createOpencode } from "@opencode-ai/sdk"
const { client } = await createOpencode({
  config: {
    model: "anthropic/claude-3-5-sonnet-20241022"
  }
})
```

### Server Options
```typescript
const opencode = await createOpencode({
  hostname: "127.0.0.1",
  port: 4096,
  config: { /* ... */ }
})
```