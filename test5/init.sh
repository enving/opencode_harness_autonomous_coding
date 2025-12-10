#!/bin/bash
set -e

echo "Initializing project..."

# Initialize git if not already
if [ ! -d ".git" ]; then
  git init
  echo "Git initialized."
fi

# Create .gitignore
cat <<EOF > .gitignore
node_modules
dist
.env
.DS_Store
coverage
EOF

# Client Setup
if [ ! -d "client" ]; then
  echo "Setting up client..."
  # Use Vite to scaffold React + TypeScript project
  # We use a template to avoid interactive prompts
  npm create vite@latest client -- --template react-ts
  
  cd client
  echo "Installing client dependencies..."
  npm install
  
  # Install Tailwind CSS and dependencies
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  
  # Configure Tailwind Content
  cat > tailwind.config.js <<EOF
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
         'claude-accent': '#CC785C',
      }
    },
  },
  plugins: [],
}
EOF

  # Add Tailwind directives
  echo "@tailwind base;" > src/index.css
  echo "@tailwind components;" >> src/index.css
  echo "@tailwind utilities;" >> src/index.css

  # Install other frontend dependencies mentioned in spec
  npm install react-router-dom react-markdown framer-motion lucide-react clsx tailwind-merge date-fns prismjs react-syntax-highlighter katex
  
  cd ..
fi

# Server Setup
if [ ! -d "server" ]; then
  echo "Setting up server..."
  mkdir server
  cd server
  npm init -y
  
  # Install backend dependencies
  echo "Installing server dependencies..."
  npm install express cors better-sqlite3 dotenv
  npm install -D nodemon ts-node typescript @types/express @types/node @types/cors @types/better-sqlite3
  
  # Create basic server structure
  mkdir -p src/routes src/controllers src/models src/middleware src/db
  
  # Create basic index.ts
  cat <<EOF > src/index.ts
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { db } from './db/database';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health Check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(\`Server running on port \${PORT}\`);
});
EOF

  # Create database init
  cat <<EOF > src/db/database.ts
import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(__dirname, '../../claude_clone.sqlite');
export const db = new Database(dbPath);

console.log('Connected to SQLite database at', dbPath);
EOF

  # Create custom tsconfig.json for server
  cat <<EOF > tsconfig.json
{
  "compilerOptions": {
    "target": "es2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF

  cd ..
fi

# Create README
echo "# Claude Clone" > README.md

echo "Initialization complete."
