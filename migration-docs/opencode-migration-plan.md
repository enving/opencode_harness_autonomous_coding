# Migration Plan: Legacy OpenAI SDK → OpenCode SDK

## Executive Summary

This document outlines a comprehensive migration strategy from the legacy OpenAI SDK to the modern OpenCode SDK. The project has already undergone a partial migration from Claude Code SDK to OpenCode Python SDK, but this plan focuses on completing the transition to leverage OpenCode's full capabilities.

## Current State Analysis

### Existing Architecture
- **Language**: Python 3.x
- **Current SDK**: OpenCode Python SDK (`opencode-ai>=0.1.0`)
- **Legacy SDK**: Claude Code SDK (`claude-code-sdk>=0.0.25`) - in `legacy/` directory
- **Pattern**: Two-agent system (Initializer + Coding Agent)
- **Security**: Multi-layered defense with permissions and bash allowlist
- **Persistence**: `feature_list.json` + Git commits

### Key Components Status
| Component | Current Status | Target Status |
|-----------|----------------|---------------|
| **Client** | ✅ Migrated to OpenCode Python SDK | ✅ Complete |
| **Agent** | ✅ Migrated to OpenCode Python SDK | ✅ Complete |
| **Security** | ✅ Migrated to OpenCode permissions | ✅ Complete |
| **Session Management** | ✅ Using OpenCode sessions | ✅ Complete |
| **TypeScript Migration** | 🔄 Partial (package.json exists) | ⏳ To be completed |

## Migration Goals

### Primary Objectities
1. **Complete TypeScript Migration**: Migrate remaining Python components to TypeScript
2. **Enhanced Security**: Leverage OpenCode's advanced permission system
3. **Improved Performance**: Utilize OpenCode's optimized session handling
4. **Better Developer Experience**: TypeScript tooling and IntelliSense
5. **Future-Proofing**: Align with OpenCode's roadmap and updates

### Success Criteria
- [ ] All components migrated to TypeScript
- [ ] 100% functional parity with Python version
- [ ] Enhanced security model implemented
- [ ] Performance benchmarks met or exceeded
- [ ] Comprehensive test coverage
- [ ] Documentation updated

## Detailed Migration Plan

### Phase 1: Foundation Setup (2-3 hours)

#### 1.1 TypeScript Environment Completion
**Current Status**: ✅ Package.json and tsconfig.json exist
**Remaining Tasks**:
- [ ] Install OpenCode SDK TypeScript dependencies
- [ ] Configure ESLint and Prettier for TypeScript
- [ ] Set up build pipeline with proper scripts
- [ ] Verify TypeScript compilation

**Files to Update**:
```json
// package.json additions
{
  "dependencies": {
    "@opencode-ai/sdk": "^1.0.0",
    "typescript": "^5.0.0"
  }
}
```

#### 1.2 Project Structure Finalization
**Current Status**: ✅ Basic structure exists
**Remaining Tasks**:
- [ ] Complete `src/` directory structure
- [ ] Set up proper module imports/exports
- [ ] Configure TypeScript path mapping
- [ ] Establish build output structure

### Phase 2: Core Components Migration (4-6 hours)

#### 2.1 Client Configuration (`src/client.ts`)
**Python Reference**: `client.py`
**Key Changes**:
```typescript
// From Python
from opencode_ai import AsyncOpencode

// To TypeScript
import { createOpencodeClient } from "@opencode-ai/sdk"

// Migration mapping
Python AsyncOpencode → TypeScript createOpencodeClient
Python session.chat() → TypeScript session.prompt()
Python extra_body → TypeScript body parameter
```

**Implementation Strategy**:
1. Create client factory function
2. Implement model selection logic
3. Configure security permissions
4. Handle authentication (multiple providers)

#### 2.2 Security System (`src/security.ts`)
**Python Reference**: `security.py`
**Key Changes**:
```typescript
// Permission system migration
Python bash_allowlist → TypeScript OpenCode permissions
Python hook system → TypeScript tool restrictions
Python sandbox → TypeScript OpenCode sandbox
```

**Security Features to Implement**:
- Filesystem restrictions
- Bash command allowlist
- Tool access control
- MCP server permissions

#### 2.3 Agent Logic (`src/agent.ts`)
**Python Reference**: `agent.py`
**Key Changes**:
```typescript
// Session management migration
Python AsyncOpencode → TypeScript OpenCode client
Python session.chat() → TypeScript session.prompt()
Python response parsing → TypeScript response handling
```

**Core Functions to Migrate**:
- `run_agent_session()`
- `run_autonomous_agent()`
- Response text extraction
- Tool use monitoring

### Phase 3: Advanced Features (6-8 hours)

#### 3.1 Session Management Enhancement
**Current Python Implementation**:
```python
session = await client.session.create(
    extra_body={
        "title": title,
        "cwd": str(project_dir.resolve())
    }
)
```

**Target TypeScript Implementation**:
```typescript
const session = await client.session.create({
  body: {
    title: title,
    cwd: projectDir.resolve()
  }
})
```

#### 3.2 Model Selection Strategy
**Python Logic**:
```python
if model == "auto":
    if openrouter_key:
        model_strategy = "openrouter/anthropic/claude-3.5-sonnet"
    elif anthropic_key:
        model_strategy = "anthropic/claude-3-5-sonnet-20241022"
```

**TypeScript Enhancement**:
```typescript
interface ModelStrategy {
  provider: string;
  model: string;
  reasoning?: string;
}

function selectOptimalModel(
  availableKeys: ApiKeys,
  preference: string = "auto"
): ModelStrategy
```

#### 3.3 Error Handling & Resilience
**Python Approach**:
```python
try:
    result = await client.session.chat(...)
except Exception as e:
    print(f"❌ Failed to send prompt: {e}")
    raise
```

**TypeScript Enhancement**:
```typescript
class OpenCodeError extends Error {
  constructor(
    message: string,
    public code: string,
    public retryable: boolean = false
  ) {
    super(message);
  }
}

async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3
): Promise<T>
```

### Phase 4: Testing & Validation (3-4 hours)

#### 4.1 Unit Tests
**Components to Test**:
- [ ] Client configuration
- [ ] Security permissions
- [ ] Agent session logic
- [ ] Model selection
- [ ] Error handling

**Test Structure**:
```typescript
// tests/client.test.ts
describe('OpenCode Client', () => {
  test('creates client with valid configuration', async () => {
    const client = await createClient(testProjectDir, 'auto');
    expect(client).toBeDefined();
  });
});
```

#### 4.2 Integration Tests
**Scenarios to Test**:
- [ ] Complete agent workflow
- [ ] Session persistence
- [ ] Security model enforcement
- [ ] Error recovery
- [ ] Performance benchmarks

#### 4.3 Manual Validation
**Test Cases**:
- [ ] Fresh project initialization
- [ ] Existing project continuation
- [ ] Model switching
- [ ] Security boundary testing
- [ ] Long-running stability

## Component Mapping Reference

### Python → TypeScript Equivalents

| Python Component | TypeScript Component | Key Differences |
|------------------|---------------------|-----------------|
| `AsyncOpencode` | `createOpencodeClient()` | Factory pattern vs class instantiation |
| `client.session.chat()` | `client.session.prompt()` | Different method names, similar functionality |
| `extra_body` | `body` parameter | Simpler parameter structure |
| `result.content` | `result.parts` | Different response structure |
| `part.text` | `part.text` | Same interface |
| `part.type == 'tool_use'` | `part.type === 'tool_use' | TypeScript strict equality |

### API Migration Examples

#### Session Creation
**Python**:
```python
session = await client.session.create(
    extra_body={
        "title": "My Session",
        "cwd": "/path/to/project"
    }
)
```

**TypeScript**:
```typescript
const session = await client.session.create({
  body: {
    title: "My Session",
    cwd: "/path/to/project"
  }
});
```

#### Sending Prompts
**Python**:
```python
result = await client.session.chat(
    session_id,
    model_id="claude-3-5-sonnet",
    provider_id="anthropic",
    parts=[{"type": "text", "text": message}]
)
```

**TypeScript**:
```typescript
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    model: {
      providerID: "anthropic",
      modelID: "claude-3-5-sonnet"
    },
    parts: [{ type: "text", text: message }]
  }
});
```

## Breaking Changes & Compatibility

### Major Breaking Changes
1. **Import Syntax**: ES modules vs Python imports
2. **Type System**: Static typing vs dynamic typing
3. **Error Handling**: Typed exceptions vs generic exceptions
4. **Async Patterns**: Promises vs asyncio
5. **Configuration**: JSON vs Python dictionaries

### Compatibility Strategies
1. **Gradual Migration**: Migrate one component at a time
2. **Adapter Pattern**: Create compatibility layers
3. **Feature Flags**: Enable/disable new features during transition
4. **Parallel Testing**: Run both versions during validation

## Risk Assessment & Mitigation

### High-Risk Areas
1. **Session Management**: Complex state transitions
2. **Security Model**: Permission system differences
3. **Error Handling**: Different exception patterns
4. **Performance**: TypeScript compilation overhead

### Mitigation Strategies
1. **Incremental Testing**: Test each component independently
2. **Rollback Plan**: Keep Python version as fallback
3. **Monitoring**: Performance metrics during migration
4. **Documentation**: Detailed migration notes

## Timeline & Milestones

### Week 1: Foundation
- [ ] Complete TypeScript setup
- [ ] Migrate client configuration
- [ ] Basic session management

### Week 2: Core Logic
- [ ] Migrate agent logic
- [ ] Implement security system
- [ ] Error handling framework

### Week 3: Advanced Features
- [ ] Enhanced session management
- [ ] Model selection optimization
- [ ] Performance improvements

### Week 4: Testing & Validation
- [ ] Comprehensive test suite
- [ ] Performance benchmarking
- [ ] Documentation updates

## Success Metrics

### Technical Metrics
- [ ] 100% TypeScript compilation
- [ ] 95%+ test coverage
- [ ] Performance parity or improvement
- [ ] Zero security regressions

### User Experience Metrics
- [ ] Seamless migration experience
- [ ] Improved developer tooling
- [ ] Better error messages
- [ ] Enhanced documentation

## Next Steps

1. **Immediate Actions**:
   - Review and approve this plan
   - Set up development environment
   - Begin Phase 1 implementation

2. **Preparation Tasks**:
   - Backup current Python implementation
   - Set up CI/CD for TypeScript
   - Prepare test data and scenarios

3. **Communication**:
   - Notify stakeholders of migration timeline
   - Document progress and blockers
   - Schedule regular check-ins

---

**Migration Status**: Ready to begin  
**Estimated Timeline**: 3-4 weeks  
**Risk Level**: Medium (with proper mitigation)  
**Success Probability**: High (with thorough testing)