# Testing Strategy for OpenCode SDK Migration

## Executive Summary

This document outlines a comprehensive testing strategy for migrating from legacy OpenAI/Claude SDK to OpenCode SDK. The strategy covers unit testing, integration testing, performance validation, and compatibility verification to ensure a smooth transition with minimal risk.

## Testing Philosophy

### Core Principles
1. **Test-Driven Migration**: Write tests before implementing migration
2. **Incremental Validation**: Test each component independently before integration
3. **Parity Verification**: Ensure 100% functional parity with legacy implementation
4. **Performance Benchmarking**: Validate performance improvements or parity
5. **Security Validation**: Ensure no security regressions

### Testing Pyramid
```
    E2E Tests (10%)
   ─────────────────
  Integration Tests (30%)
 ─────────────────────────
Unit Tests (60%)
```

## Test Environment Setup

### 1. Test Infrastructure

#### Test Directory Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── client/
│   ├── agent/
│   ├── security/
│   ├── progress/
│   └── prompts/
├── integration/             # Integration tests for component interaction
│   ├── session-management/
│   ├── security-integration/
│   └── workflow/
├── e2e/                     # End-to-end tests for complete workflows
│   ├── autonomous-agent/
│   └── migration-validation/
├── performance/             # Performance and benchmark tests
│   ├── session-creation/
│   ├── response-times/
│   └── memory-usage/
├── compatibility/           # Legacy vs new implementation tests
│   ├── response-parity/
│   └── behavior-parity/
└── fixtures/                # Test data and mock objects
    ├── sample-projects/
    ├── mock-responses/
    └── test-configs/
```

#### Test Configuration
```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/tests/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
};
```

### 2. Mock Strategy

#### OpenCode SDK Mocking
```typescript
// tests/mocks/opencode-mock.ts
export class MockOpenCodeClient {
  private sessions: Map<string, MockSession> = new Map();
  
  async session() {
    return {
      create: jest.fn().mockImplementation(async (params) => {
        const sessionId = `test-session-${Date.now()}`;
        const session = new MockSession(sessionId, params);
        this.sessions.set(sessionId, session);
        return session;
      }),
      
      get: jest.fn().mockImplementation(async (params) => {
        return this.sessions.get(params.path.id);
      }),
      
      delete: jest.fn().mockImplementation(async (params) => {
        this.sessions.delete(params.path.id);
        return true;
      }),
      
      chat: jest.fn().mockImplementation(async (sessionId, ...args) => {
        const session = this.sessions.get(sessionId);
        return session?.chat(...args);
      }),
    };
  }
}

export class MockSession {
  constructor(
    public id: string,
    private params: any
  ) {}
  
  async chat(...args: any[]) {
    return {
      content: [
        { type: 'text', text: 'Mock response' },
        { type: 'tool_use', name: 'mock_tool', input: {} }
      ]
    };
  }
}
```

## Unit Testing Strategy

### 1. Client Configuration Tests

#### Test Suite: `client.test.ts`
```typescript
describe('OpenCode Client Configuration', () => {
  let mockProjectDir: Path;
  
  beforeEach(() => {
    mockProjectDir = Path.join(__dirname, '../fixtures/test-project');
  });
  
  describe('createClient', () => {
    test('should create client with valid configuration', async () => {
      const client = await createClient(mockProjectDir, 'auto');
      
      expect(client).toBeDefined();
      expect(client.baseUrl).toBe('http://localhost:4096');
    });
    
    test('should handle missing API keys gracefully', async () => {
      // Mock environment without API keys
      delete process.env.ANTHROPIC_API_KEY;
      delete process.env.OPENROUTER_API_KEY;
      delete process.env.OPENCODE_API_KEY;
      
      const client = await createClient(mockProjectDir, 'auto');
      expect(client).toBeNull();
    });
    
    test('should select optimal model for auto mode', async () => {
      process.env.OPENROUTER_API_KEY = 'test-key';
      
      const client = await createClient(mockProjectDir, 'auto');
      // Verify model selection logic
      expect(client).toBeDefined();
    });
    
    test('should create OpenCode settings file', async () => {
      await createClient(mockProjectDir, 'auto');
      
      const settingsFile = mockProjectDir.join('.opencode_settings.json');
      expect(await settingsFile.exists()).toBe(true);
      
      const settings = JSON.parse(await settingsFile.read());
      expect(settings.model).toBeDefined();
      expect(settings.permissions).toBeDefined();
    });
  });
  
  describe('createSession', () => {
    test('should create session with valid parameters', async () => {
      const client = await createClient(mockProjectDir, 'auto');
      const sessionId = await createSession(client, 'Test Session', mockProjectDir);
      
      expect(sessionId).toBeDefined();
      expect(typeof sessionId).toBe('string');
    });
    
    test('should handle session creation errors', async () => {
      const client = await createClient(mockProjectDir, 'auto');
      // Mock session creation failure
      jest.spyOn(client.session, 'create').mockRejectedValue(new Error('Session creation failed'));
      
      await expect(createSession(client, 'Test Session', mockProjectDir))
        .rejects.toThrow('Session creation failed');
    });
  });
  
  describe('sendPrompt', () => {
    test('should send prompt and receive response', async () => {
      const client = await createClient(mockProjectDir, 'auto');
      const sessionId = 'test-session-id';
      const message = 'Test message';
      
      const response = await sendPrompt(client, sessionId, message);
      
      expect(response).toBeDefined();
      expect(response.content).toBeDefined();
    });
    
    test('should handle model selection correctly', async () => {
      const client = await createClient(mockProjectDir, 'auto');
      const sessionId = 'test-session-id';
      
      // Test auto mode
      await sendPrompt(client, sessionId, 'test', 'auto');
      
      // Test specific model
      await sendPrompt(client, sessionId, 'test', 'anthropic/claude-3-5-sonnet');
      
      // Verify correct API calls were made
      expect(client.session.chat).toHaveBeenCalledTimes(2);
    });
  });
});
```

### 2. Security System Tests

#### Test Suite: `security.test.ts`
```typescript
describe('Security System', () => {
  let mockProjectDir: Path;
  
  beforeEach(() => {
    mockProjectDir = Path.join(__dirname, '../fixtures/test-project');
  });
  
  describe('get_opencode_permissions', () => {
    test('should generate correct permissions for project directory', () => {
      const permissions = get_opencode_permissions(mockProjectDir);
      
      expect(permissions).toBeDefined();
      expect(permissions.allow).toBeDefined();
      expect(permissions.deny).toBeDefined();
    });
    
    test('should restrict file access to project directory', () => {
      const permissions = get_opencode_permissions(mockProjectDir);
      
      // Verify allowed paths are within project directory
      const allowedPaths = permissions.allow.filter(p => p.includes('Read') || p.includes('Write'));
      allowedPaths.forEach(path => {
        expect(path).toContain('./'); // Relative paths only
      });
    });
    
    test('should include bash allowlist in security settings', () => {
      const permissions = get_opencode_permissions(mockProjectDir);
      
      expect(permissions.security).toBeDefined();
      expect(permissions.security.bash_allowlist).toBeDefined();
      
      const allowedCommands = permissions.security.bash_allowlist;
      expect(allowedCommands).toContain('ls');
      expect(allowedCommands).toContain('cat');
      expect(allowedCommands).toContain('npm');
      expect(allowedCommands).not.toContain('rm'); // Dangerous commands excluded
    });
  });
  
  describe('bash command validation', () => {
    test('should allow safe bash commands', () => {
      const safeCommands = ['ls -la', 'cat file.txt', 'npm install'];
      
      safeCommands.forEach(command => {
        expect(validate_bash_command(command)).toBe(true);
      });
    });
    
    test('should block dangerous bash commands', () => {
      const dangerousCommands = ['rm -rf /', 'sudo su', 'chmod 777 /etc'];
      
      dangerousCommands.forEach(command => {
        expect(validate_bash_command(command)).toBe(false);
      });
    });
    
    test('should handle command injection attempts', () => {
      const injectionAttempts = [
        'ls; rm -rf /',
        'cat file.txt && sudo su',
        'npm install | curl malicious.com'
      ];
      
      injectionAttempts.forEach(command => {
        expect(validate_bash_command(command)).toBe(false);
      });
    });
  });
});
```

### 3. Agent Logic Tests

#### Test Suite: `agent.test.ts`
```typescript
describe('Agent Logic', () => {
  let mockClient: MockOpenCodeClient;
  let mockProjectDir: Path;
  
  beforeEach(() => {
    mockClient = new MockOpenCodeClient();
    mockProjectDir = Path.join(__dirname, '../fixtures/test-project');
  });
  
  describe('run_agent_session', () => {
    test('should run single agent session successfully', async () => {
      const sessionId = 'test-session';
      const message = 'Test message';
      
      const [status, response] = await run_agent_session(
        mockClient as any,
        sessionId,
        message,
        mockProjectDir
      );
      
      expect(status).toBe('continue');
      expect(response).toBeDefined();
    });
    
    test('should handle tool use in responses', async () => {
      // Mock response with tool use
      const mockResponse = {
        content: [
          { type: 'text', text: 'I will help you' },
          { type: 'tool_use', name: 'read_file', input: { path: 'test.txt' } }
        ]
      };
      
      mockClient.session.chat = jest.fn().mockResolvedValue(mockResponse);
      
      const [, response] = await run_agent_session(
        mockClient as any,
        'test-session',
        'read test.txt',
        mockProjectDir
      );
      
      expect(response).toContain('I will help you');
    });
    
    test('should handle session errors gracefully', async () => {
      mockClient.session.chat = jest.fn().mockRejectedValue(new Error('Session error'));
      
      const [status, error] = await run_agent_session(
        mockClient as any,
        'test-session',
        'test message',
        mockProjectDir
      );
      
      expect(status).toBe('error');
      expect(error).toContain('Session error');
    });
  });
  
  describe('run_autonomous_agent', () => {
    test('should handle fresh project initialization', async () => {
      const maxIterations = 1;
      
      // Mock fresh project (no feature_list.json)
      jest.spyOn(mockProjectDir, 'join').mockReturnValue({
        exists: jest.fn().mockResolvedValue(false)
      } as any);
      
      await run_autonomous_agent(
        mockProjectDir,
        'auto',
        maxIterations
      );
      
      // Verify initializer agent was used
      expect(mockClient.session.create).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Initializer Agent - Project Setup'
        })
      );
    });
    
    test('should handle existing project continuation', async () => {
      const maxIterations = 1;
      
      // Mock existing project (feature_list.json exists)
      jest.spyOn(mockProjectDir, 'join').mockReturnValue({
        exists: jest.fn().mockResolvedValue(true)
      } as any);
      
      await run_autonomous_agent(
        mockProjectDir,
        'auto',
        maxIterations
      );
      
      // Verify coding agent was used
      expect(mockClient.session.create).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Coding Agent - Feature Implementation'
        })
      );
    });
    
    test('should respect max iterations limit', async () => {
      const maxIterations = 2;
      let iterationCount = 0;
      
      // Mock successful sessions
      mockClient.session.chat = jest.fn().mockResolvedValue({
        content: [{ type: 'text', text: 'Working on features...' }]
      });
      
      await run_autonomous_agent(
        mockProjectDir,
        'auto',
        maxIterations
      );
      
      // Verify session was called maxIterations times
      expect(mockClient.session.chat).toHaveBeenCalledTimes(maxIterations);
    });
  });
});
```

## Integration Testing Strategy

### 1. Session Management Integration

#### Test Suite: `session-management.test.ts`
```typescript
describe('Session Management Integration', () => {
  let client: OpenCodeClient;
  let projectDir: Path;
  
  beforeAll(async () => {
    client = await createClient(Path.join(__dirname, '../fixtures/test-project'), 'auto');
    projectDir = Path.join(__dirname, '../fixtures/integration-project');
  });
  
  afterAll(async () => {
    // Cleanup test sessions
    const sessions = await client.session.list();
    for (const session of sessions) {
      await client.session.delete({ path: { id: session.id } });
    }
  });
  
  test('should maintain session state across multiple prompts', async () => {
    const sessionId = await createSession(client, 'State Test', projectDir);
    
    // Send first prompt
    const response1 = await sendPrompt(client, sessionId, 'Create a file called test.txt');
    expect(response1.content).toBeDefined();
    
    // Send second prompt (should maintain context)
    const response2 = await sendPrompt(client, sessionId, 'Now read the file you created');
    expect(response2.content).toBeDefined();
    
    // Verify session still exists and has context
    const session = await client.session.get({ path: { id: sessionId } });
    expect(session).toBeDefined();
    expect(session.id).toBe(sessionId);
  });
  
  test('should handle session persistence and recovery', async () => {
    const sessionId = await createSession(client, 'Persistence Test', projectDir);
    
    // Send initial prompt
    await sendPrompt(client, sessionId, 'Initialize project');
    
    // Simulate session disconnect/reconnect
    const reconnectedSession = await client.session.get({ path: { id: sessionId } });
    expect(reconnectedSession).toBeDefined();
    
    // Continue with new prompt
    const response = await sendPrompt(client, sessionId, 'Continue work');
    expect(response.content).toBeDefined();
  });
  
  test('should handle concurrent sessions properly', async () => {
    const session1Id = await createSession(client, 'Concurrent Test 1', projectDir);
    const session2Id = await createSession(client, 'Concurrent Test 2', projectDir);
    
    // Send prompts to both sessions concurrently
    const [response1, response2] = await Promise.all([
      sendPrompt(client, session1Id, 'Work in session 1'),
      sendPrompt(client, session2Id, 'Work in session 2')
    ]);
    
    expect(response1.content).toBeDefined();
    expect(response2.content).toBeDefined();
    
    // Verify sessions are independent
    expect(session1Id).not.toBe(session2Id);
  });
});
```

### 2. Security Integration Tests

#### Test Suite: `security-integration.test.ts`
```typescript
describe('Security Integration', () => {
  let client: OpenCodeClient;
  let projectDir: Path;
  
  beforeAll(async () => {
    projectDir = Path.join(__dirname, '../fixtures/security-test-project');
    client = await createClient(projectDir, 'auto');
  });
  
  test('should enforce file access restrictions', async () => {
    const sessionId = await createSession(client, 'Security Test', projectDir);
    
    // Try to access file outside project directory
    const maliciousPrompt = 'Read the file /etc/passwd';
    const response = await sendPrompt(client, sessionId, maliciousPrompt);
    
    // Should be blocked or return error
    expect(response.content).toBeDefined();
    // Verify no actual file access occurred (would need filesystem monitoring)
  });
  
  test('should enforce bash command restrictions', async () => {
    const sessionId = await createSession(client, 'Bash Security Test', projectDir);
    
    // Try to execute dangerous command
    const maliciousPrompt = 'Run the command: rm -rf /';
    const response = await sendPrompt(client, sessionId, maliciousPrompt);
    
    // Should be blocked
    expect(response.content).toBeDefined();
    // Verify command was not executed
  });
  
  test('should allow legitimate operations within project', async () => {
    const sessionId = await createSession(client, 'Legitimate Operations Test', projectDir);
    
    // Perform legitimate operations
    const legitimatePrompt = `
      1. Create a file called app.js with console.log('Hello World')
      2. Read the file back
      3. Run npm init -y
      4. Run npm install express
    `;
    
    const response = await sendPrompt(client, sessionId, legitimatePrompt);
    
    // Should succeed
    expect(response.content).toBeDefined();
    
    // Verify files were created in project directory only
    const appJsExists = await projectDir.join('app.js').exists();
    const packageJsonExists = await projectDir.join('package.json').exists();
    
    expect(appJsExists).toBe(true);
    expect(packageJsonExists).toBe(true);
  });
});
```

## End-to-End Testing Strategy

### 1. Complete Workflow Tests

#### Test Suite: `autonomous-agent-e2e.test.ts`
```typescript
describe('Autonomous Agent E2E Tests', () => {
  let projectDir: Path;
  
  beforeEach(() => {
    projectDir = Path.join(__dirname, '../fixtures/e2e-project');
  });
  
  test('should complete full autonomous workflow', async () => {
    const maxIterations = 3; // Limited for testing
    
    await run_autonomous_agent(projectDir, 'auto', maxIterations);
    
    // Verify project structure was created
    const featureListExists = await projectDir.join('feature_list.json').exists();
    expect(featureListExists).toBe(true);
    
    // Verify git was initialized
    const gitDirExists = await projectDir.join('.git').exists();
    expect(gitDirExists).toBe(true);
    
    // Verify some progress was made
    const featureList = JSON.parse(await projectDir.join('feature_list.json').read());
    expect(featureList.features).toBeDefined();
    expect(featureList.features.length).toBeGreaterThan(0);
  }, 60000); // 60 second timeout for E2E test
  
  test('should handle project continuation correctly', async () => {
    // Create initial project state
    await projectDir.join('feature_list.json').write(JSON.stringify({
      features: [
        { id: 1, description: 'Test feature', status: 'pending' }
      ]
    }));
    
    // Run agent for one iteration
    await run_autonomous_agent(projectDir, 'auto', 1);
    
    // Verify progress was made
    const featureList = JSON.parse(await projectDir.join('feature_list.json').read());
    expect(featureList.features[0].status).not.toBe('pending');
  });
  
  test('should handle errors and recovery gracefully', async () => {
    // Mock error conditions
    const originalCreateClient = createClient;
    let callCount = 0;
    
    (createClient as jest.Mock) = jest.fn().mockImplementation(async (...args) => {
      callCount++;
      if (callCount === 1) {
        throw new Error('Simulated client creation error');
      }
      return originalCreateClient(...args);
    });
    
    // Should recover from error
    await expect(run_autonomous_agent(projectDir, 'auto', 1))
      .resolves.not.toThrow();
    
    // Restore original function
    (createClient as jest.Mock).mockRestore();
  });
});
```

## Performance Testing Strategy

### 1. Benchmark Tests

#### Test Suite: `performance.test.ts`
```typescript
describe('Performance Tests', () => {
  let client: OpenCodeClient;
  let projectDir: Path;
  
  beforeAll(async () => {
    client = await createClient(Path.join(__dirname, '../fixtures/perf-project'), 'auto');
    projectDir = Path.join(__dirname, '../fixtures/perf-project');
  });
  
  test('session creation should be within acceptable time limits', async () => {
    const startTime = Date.now();
    
    for (let i = 0; i < 10; i++) {
      const sessionId = await createSession(client, `Perf Test ${i}`, projectDir);
      expect(sessionId).toBeDefined();
    }
    
    const endTime = Date.now();
    const avgTime = (endTime - startTime) / 10;
    
    // Should average less than 1 second per session
    expect(avgTime).toBeLessThan(1000);
  });
  
  test('prompt response should be within acceptable time limits', async () => {
    const sessionId = await createSession(client, 'Response Time Test', projectDir);
    const prompts = [
      'Create a simple hello world function',
      'Add error handling to the function',
      'Write unit tests for the function'
    ];
    
    const responseTimes: number[] = [];
    
    for (const prompt of prompts) {
      const startTime = Date.now();
      await sendPrompt(client, sessionId, prompt);
      const endTime = Date.now();
      
      responseTimes.push(endTime - startTime);
    }
    
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    
    // Should average less than 30 seconds per response (adjust based on model)
    expect(avgResponseTime).toBeLessThan(30000);
  });
  
  test('memory usage should remain stable during extended operation', async () => {
    const initialMemory = process.memoryUsage().heapUsed;
    
    // Run multiple sessions
    for (let i = 0; i < 20; i++) {
      const sessionId = await createSession(client, `Memory Test ${i}`, projectDir);
      await sendPrompt(client, sessionId, `Test prompt ${i}`);
    }
    
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
    
    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;
    
    // Memory increase should be reasonable (less than 100MB)
    expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024);
  });
});
```

## Compatibility Testing Strategy

### 1. Response Parity Tests

#### Test Suite: `compatibility.test.ts`
```typescript
describe('Legacy Compatibility Tests', () => {
  test('should produce equivalent responses to legacy implementation', async () => {
    const testPrompts = [
      'Create a simple REST API',
      'Add authentication to the API',
      'Write documentation for the API'
    ];
    
    const legacyResponses = [];
    const opencodeResponses = [];
    
    // Test with legacy implementation (if available)
    for (const prompt of testPrompts) {
      // Mock legacy response for comparison
      const legacyResponse = await mockLegacyClient.query(prompt);
      legacyResponses.push(legacyResponse);
    }
    
    // Test with OpenCode implementation
    const opencodeClient = await createClient(projectDir, 'auto');
    for (const prompt of testPrompts) {
      const sessionId = await createSession(opencodeClient, 'Compatibility Test', projectDir);
      const response = await sendPrompt(opencodeClient, sessionId, prompt);
      opencodeResponses.push(response);
    }
    
    // Compare key aspects of responses
    legacyResponses.forEach((legacy, index) => {
      const opencode = opencodeResponses[index];
      
      // Both should have content
      expect(legacy.content).toBeDefined();
      expect(opencode.content).toBeDefined();
      
      // Both should include tool use for coding tasks
      const legacyToolUse = legacy.content.some(part => part.type === 'tool_use');
      const opencodeToolUse = opencode.content.some(part => part.type === 'tool_use');
      
      expect(legacyToolUse).toBe(opencodeToolUse);
    });
  });
  
  test('should maintain behavior parity for edge cases', async () => {
    const edgeCases = [
      '', // Empty prompt
      'x'.repeat(10000), // Very long prompt
      '🚀🔥💻', // Unicode characters
      '```javascript\nconst x = 1;\n```', // Code blocks
    ];
    
    const client = await createClient(projectDir, 'auto');
    
    for (const edgeCase of edgeCases) {
      const sessionId = await createSession(client, 'Edge Case Test', projectDir);
      
      // Should not crash or throw unhandled exceptions
      await expect(sendPrompt(client, sessionId, edgeCase))
        .resolves.toBeDefined();
    }
  });
});
```

## Test Data Management

### 1. Test Fixtures

#### Sample Projects
```typescript
// tests/fixtures/sample-projects/simple-web-app/
export const SIMPLE_WEB_APP = {
  'package.json': JSON.stringify({
    name: 'test-app',
    version: '1.0.0',
    scripts: { start: 'node server.js' }
  }),
  'server.js': `
    const express = require('express');
    const app = express();
    app.get('/', (req, res) => res.send('Hello World'));
    app.listen(3000);
  `,
  'README.md': '# Test App\n\nA simple web application.'
};

// tests/fixtures/sample-projects/feature-list.json
export const SAMPLE_FEATURE_LIST = {
  features: [
    {
      id: 1,
      description: 'Create basic Express server',
      status: 'pending',
      test_cases: ['Server starts on port 3000', 'Returns "Hello World"']
    },
    {
      id: 2,
      description: 'Add user authentication',
      status: 'pending',
      test_cases: ['Users can register', 'Users can login', 'Protected routes work']
    }
  ]
};
```

### 2. Mock Responses

#### OpenCode API Responses
```typescript
// tests/fixtures/mock-responses/opencode-responses.ts
export const MOCK_SESSION_RESPONSE = {
  id: 'test-session-123',
  title: 'Test Session',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  status: 'active'
};

export const MOCK_CHAT_RESPONSE = {
  content: [
    {
      type: 'text',
      text: 'I will help you create a web application.'
    },
    {
      type: 'tool_use',
      name: 'write_file',
      input: {
        path: 'server.js',
        content: 'console.log("Hello World");'
      }
    }
  ],
  usage: {
    input_tokens: 100,
    output_tokens: 50
  }
};
```

## Continuous Integration

### 1. CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/test-migration.yml
name: Migration Tests

on:
  push:
    branches: [main, migration/*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        npm ci
        pip install -r requirements.txt
    
    - name: Start OpenCode server
      run: |
        npx opencode-ai serve --port 4096 --hostname 0.0.0.0 &
        sleep 10  # Wait for server to start
    
    - name: Run unit tests
      run: npm run test:unit
    
    - name: Run integration tests
      run: npm run test:integration
    
    - name: Run E2E tests
      run: npm run test:e2e
    
    - name: Run performance tests
      run: npm run test:performance
    
    - name: Generate coverage report
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 2. Test Scripts

#### Package.json Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:unit": "jest tests/unit",
    "test:integration": "jest tests/integration",
    "test:e2e": "jest tests/e2e",
    "test:performance": "jest tests/performance",
    "test:compatibility": "jest tests/compatibility",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

## Test Execution Plan

### Phase 1: Unit Testing (Week 1)
- [ ] Client configuration tests
- [ ] Security system tests
- [ ] Agent logic tests
- [ ] Progress tracking tests
- [ ] Prompt management tests

### Phase 2: Integration Testing (Week 2)
- [ ] Session management integration
- [ ] Security integration tests
- [ ] Component interaction tests
- [ ] Error handling integration

### Phase 3: End-to-End Testing (Week 3)
- [ ] Complete workflow tests
- [ ] Autonomous agent tests
- [ ] Project lifecycle tests
- [ ] Error recovery tests

### Phase 4: Performance & Compatibility (Week 4)
- [ ] Performance benchmarks
- [ ] Memory usage tests
- [ ] Legacy compatibility tests
- [ ] Response parity validation

## Success Metrics

### Coverage Requirements
- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: 80%+ feature coverage
- **E2E Tests**: 100% critical path coverage

### Performance Benchmarks
- **Session Creation**: < 1 second average
- **Response Time**: < 30 seconds average
- **Memory Usage**: < 100MB increase during extended operation

### Quality Gates
- All tests must pass
- No security regressions
- Performance parity or improvement
- 100% functional compatibility

---

**Testing Timeline**: 4 weeks  
**Risk Level**: Low (comprehensive testing)  
**Success Probability**: High (thorough validation)