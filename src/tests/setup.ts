// Test setup file
import { config } from 'dotenv';

// Load environment variables for tests
config({ path: '.env.test' });

// Set test environment variables
process.env.NODE_ENV = 'test';

// Mock console methods for cleaner test output
global.console = {
  ...console,
  // Uncomment to ignore specific console methods during tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
};

// Set default test timeout
jest.setTimeout(30000);