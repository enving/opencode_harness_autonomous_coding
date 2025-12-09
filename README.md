# Claude.ai Clone

A fully functional clone of Anthropic's Claude.ai conversational AI interface, built with modern web technologies.

## Features

- **Streaming Chat**: Real-time message streaming with Claude API
- **Artifact System**: Code rendering, HTML previews, and interactive artifacts
- **Conversation Management**: Organize, search, and manage conversations
- **Projects**: Group related conversations with custom instructions
- **Model Selection**: Choose between Claude Sonnet, Haiku, and Opus models
- **Advanced Settings**: Temperature, token limits, and custom instructions
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark Mode**: Full dark theme support
- **Collaboration**: Share conversations and artifacts

## Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Node.js + Express + SQLite
- **AI**: Anthropic Claude API
- **Streaming**: Server-Sent Events (SSE)

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd claude-clone
   ```

2. **Environment setup**:
   ```bash
   # Copy environment file
   cp .env.example .env

   # Add your Anthropic API key
   echo "VITE_ANTHROPIC_API_KEY=your_key_here" >> .env
   ```

3. **Run the application**:
   ```bash
   ./init.sh
   ```

4. **Open your browser**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:5000/api/docs

## Development

### Prerequisites

- Node.js 18+
- npm or pnpm

### Project Structure

```
├── server/                 # Backend (Express + SQLite)
│   ├── src/
│   ├── database.db        # SQLite database
│   └── package.json
├── src/                   # Frontend (React + Vite)
├── public/                # Static assets
├── feature_list.json      # Test specifications (200+ tests)
├── init.sh               # Development setup script
└── README.md
```

### Available Scripts

- `npm run dev` - Start development servers
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run lint` - Lint code

## API Reference

### Authentication
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Conversations
- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/:id`

### Messages
- `POST /api/conversations/:id/messages`
- `GET /api/messages/stream` (SSE)

### Artifacts
- `GET /api/conversations/:id/artifacts`
- `GET /api/artifacts/:id`

## Contributing

1. Follow the feature_list.json for implementation priorities
2. Write tests for new features
3. Ensure responsive design
4. Maintain accessibility standards

## License

MIT License - see LICENSE file for details.