#!/bin/bash

# Claude.ai Clone - Development Environment Setup
# This script sets up and runs the full-stack application

set -e

echo "🚀 Setting up Claude.ai Clone Development Environment"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd server

# Install backend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing backend dependencies..."
    npm install
else
    echo "Backend dependencies already installed"
fi

# Setup database
echo "Setting up SQLite database..."
if [ ! -f "database.db" ]; then
    npm run db:init
else
    echo "Database already exists"
fi

echo "✅ Backend setup complete"

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd ../

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Frontend dependencies already installed"
fi

echo "✅ Frontend setup complete"

# Start development servers
echo ""
echo "🔥 Starting development servers..."
echo ""

# Start backend server in background
echo "Starting backend server..."
cd server
npm run dev &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait for servers to start
sleep 5

echo ""
echo "🎉 Development environment is ready!"
echo "====================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "📝 API Documentation: http://localhost:5000/api/docs"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"
echo ""
echo "📂 Project structure:"
echo "  - Frontend: ./ (React + Vite)"
echo "  - Backend: ./server (Express + SQLite)"
echo "  - Database: ./server/database.db"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
wait