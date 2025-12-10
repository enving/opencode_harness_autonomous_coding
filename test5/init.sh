#!/bin/bash

# Initialize git
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized."
else
    echo "Git repository already exists."
fi

# Create server directory
if [ ! -d "server" ]; then
    mkdir server
    cd server
    npm init -y
    # Install backend dependencies mentioned in spec
    npm install express better-sqlite3 cors dotenv
    # Create basic server file
    echo "const express = require('express');" > index.js
    echo "const app = express();" >> index.js
    echo "const port = 3001;" >> index.js
    echo "const cors = require('cors');" >> index.js
    echo "" >> index.js
    echo "app.use(cors());" >> index.js
    echo "app.use(express.json());" >> index.js
    echo "" >> index.js
    echo "app.get('/api/health', (req, res) => res.json({ status: 'ok' }));" >> index.js
    echo "" >> index.js
    echo "app.listen(port, () => {" >> index.js
    echo "  console.log(\`Server running on port \${port}\`);" >> index.js
    echo "});" >> index.js
    cd ..
    echo "Server setup complete."
else
    echo "Server directory already exists."
fi

# Create client directory
if [ ! -d "client" ]; then
    # scaffolding vite react app
    npm create vite@latest client -- --template react
    cd client
    # Install frontend dependencies mentioned in spec
    npm install
    npm install tailwindcss postcss autoprefixer react-router-dom react-markdown
    npx tailwindcss init -p
    
    # Configure Tailwind
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

    # Add Tailwind directives to index.css
    echo "@tailwind base;" > src/index.css
    echo "@tailwind components;" >> src/index.css
    echo "@tailwind utilities;" >> src/index.css

    cd ..
    echo "Client setup complete."
else
    echo "Client directory already exists."
fi

# Create .gitignore
cat > .gitignore <<EOF
node_modules
.env
dist
.DS_Store
*.log
EOF

echo "Project initialization complete."
