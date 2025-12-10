# OpenCode SDK Migration Plan

## Executive Summary

This document outlines the migration strategy from the legacy OpenAI SDK usage to the new OpenCode SDK. The project has already begun the migration process with some OpenCode SDK integration, but requires a comprehensive update to fully leverage the new SDK patterns.

## Current State Analysis

### ✅ Already Completed
- Basic OpenCode SDK dependency in package.json (`@opencode-ai/sdk": "^1.0.0`)
- TypeScript project structure established
- Some OpenCode client initialization in `client.py`
- Two-agent architecture pattern (Initializer + Coding Agent)

### ❌ Migration Gaps Identified

1. **SDK Usage Pattern Mismatch**
   - Current code uses `opencode_ai` Python package
   - Need to migrate to TypeScript `@opencode-ai/sdk`
   - API patterns are significantly different

2. **Client Creation Pattern**
   - Current: `AsyncOpencode(base_url=base_url)` 
   - Target: `createOpencodeClient({ baseUrl: "http://localhost:4096" })`

3. **Session Management**
   - Current: Manual session creation with `client.session.create()`
   - Target: Enhanced session API with proper lifecycle management

4. **Security Model**
   - Current: Custom bash allowlist + permissions JSON
   - Target: OpenCode's built-in permissions and security rules

## Migration Strategy

### Phase 1: Foundation (Immediate)
1. **Update Dependencies**
   - Ensure `@opencode-ai/sdk` is latest version
   - Add missing TypeScript types
   - Update build scripts

2. **Create TypeScript Client**
   - Migrate `client.py` → `src/client.ts`
   - Implement proper OpenCode client creation
   - Handle authentication and configuration

### Phase 2: Core Migration (High Priority)
1. **Agent Logic Migration**
   - Migrate `agent.py` → `src/agent.ts`
   - Update session management patterns
   - Implement proper error handling

2. **Security Integration**
   - Migrate `security.py` → `src/security.ts`
   - Convert bash allowlist to OpenCode permissions
   - Implement security rules

### Phase 3: Integration & Testing (Medium Priority)
1. **Entry Point Creation**
   - Create `src/index.ts` as main entry
   - Implement CLI interface
   - Add proper error handling

2. **Testing & Validation**
   - Ensure feature parity with Python version
   - Test security model
   - Performance validation

## Technical Implementation Details

### 1. Client Migration Pattern

**Current (Python):**
```python
from opencode_ai import AsyncOpencode

client = AsyncOpencode(base_url=base_url)
session = await client.session.create(extra_body={...})
result = await client.session.chat(session_id, ...)
```

**Target (TypeScript):**
```typescript
import { createOpencodeClient } from "@opencode-ai/sdk"

const client = createOpencodeClient({ 
  baseUrl: "http://localhost:4096" 
})
const session = await client.session.create({ 
  body: { title: "My Session" } 
})
const result = await client.session.prompt({
  path: { id: session.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
    parts: [{ type: "text", text: "Hello!" }]
  }
})
```

### 2. Security Model Migration

**Current (Custom JSON):**
```json
{
  "permissions": {
    "allow": ["Read(./**)", "Write(./**)", "Bash(*)"]
  },
  "security": {
    "bash_allowlist": ["ls", "cat", "npm", "git"]
  }
}
```

**Target (OpenCode Config):**
```typescript
const config = {
  permissions: {
    allow: [
      { tool: "read", pattern: "./**" },
      { tool: "write", pattern: "./**" },
      { tool: "bash", command: "ls" },
      { tool: "bash", command: "cat" },
      { tool: "bash", command: "npm" },
      { tool: "bash", command: "git" }
    ]
  }
}
```

### 3. Session Management Enhancement

**Current Issues:**
- Manual session ID tracking
- Limited session lifecycle management
- No session persistence

**Target Improvements:**
- Automatic session lifecycle management
- Session persistence and recovery
- Enhanced error handling and retry logic

## File Mapping

| Python File | TypeScript File | Priority | Notes |
|-------------|----------------|----------|-------|
| `client.py` | `src/client.ts` | High | Core client creation |
| `agent.py` | `src/agent.ts` | High | Agent session logic |
| `security.py` | `src/security.ts` | Medium | Security rules |
| `progress.py` | `src/progress.ts` | Medium | Progress tracking |
| `prompts.py` | `src/prompts.ts` | Low | Prompt utilities |
| `autonomous_agent_demo.py` | `src/index.ts` | High | Main entry point |

## Risk Assessment & Mitigation

### High Risk Items
1. **API Compatibility**: OpenCode SDK API differs significantly from current implementation
   - **Mitigation**: Incremental migration with fallback mechanisms

2. **Security Model Differences**: Current custom security may not map directly
   - **Mitigation**: Comprehensive security testing during migration

3. **Session Management**: Complex session logic may require redesign
   - **Mitigation**: Preserve existing session patterns while adopting new API

### Medium Risk Items
1. **Performance**: TypeScript version may have different performance characteristics
   - **Mitigation**: Performance benchmarking and optimization

2. **Error Handling**: New error patterns require updated handling logic
   - **Mitigation**: Comprehensive error handling implementation

## Success Criteria

### Functional Requirements
- [ ] Autonomous agent builds complete applications
- [ ] Two-agent pattern works correctly  
- [ ] Security model prevents unauthorized access
- [ ] Progress tracking and resume functionality
- [ ] CLI interface with all original options

### Technical Requirements
- [ ] TypeScript compilation without errors
- [ ] All tests passing
- [ ] Performance comparable to Python version
- [ ] Proper error handling and logging
- [ ] Clean, maintainable code structure

## Implementation Timeline

### Week 1: Foundation
- Day 1-2: Update dependencies and project setup
- Day 3-4: Migrate client.ts with basic OpenCode integration
- Day 5: Test client creation and basic functionality

### Week 2: Core Migration  
- Day 1-3: Migrate agent.ts with session management
- Day 4-5: Migrate security.ts with permissions model

### Week 3: Integration & Testing
- Day 1-2: Create index.ts entry point
- Day 3-4: Comprehensive testing and bug fixes
- Day 5: Performance optimization and documentation

## Next Steps

1. **Immediate Actions**
   - Update package.json with latest OpenCode SDK
   - Begin client.ts migration
   - Set up development environment

2. **This Week**
   - Complete client.ts and agent.ts migration
   - Implement basic session management
   - Test core functionality

3. **Next Week**  
   - Complete security migration
   - Implement entry point
   - Comprehensive testing

## Resources

### Documentation
- [OpenCode SDK Documentation](https://opencode.ai/docs/sdk/)
- [OpenCode GitHub Repository](https://github.com/sst/opencode)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Tools & Libraries
- `@opencode-ai/sdk` - Main SDK
- `tsx` - TypeScript execution
- `commander` - CLI framework
- `chalk` - Terminal styling

---

**Status**: Ready for implementation  
**Last Updated**: 2025-12-09  
**Owner**: Migration Team  
**Review Date**: 2025-12-10