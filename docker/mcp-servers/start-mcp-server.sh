#!/bin/bash

# === Dopemux MCP Server Startup Script ===
# Starts the mas-sequential-thinking MCP server in Docker

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

echo "🚀 Starting Dopemux MCP Server (mas-sequential-thinking)"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    echo "💡 Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check required environment variables
echo "🔍 Checking environment configuration..."

# Source the environment file to check variables
set -a  # automatically export all variables
source "$ENV_FILE"
set +a

# Validate critical environment variables
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ Error: DEEPSEEK_API_KEY is not set"
    echo "💡 Please set your DeepSeek API key in .env file"
    exit 1
fi

if [ -z "$EXA_API_KEY" ]; then
    echo "⚠️  Warning: EXA_API_KEY is not set (research features will be limited)"
fi

echo "✅ Configuration validated"

# Build and start the container
echo "🔨 Building MCP server container..."
cd "$SCRIPT_DIR"

# Check if we need to rebuild
if [ "$1" == "--rebuild" ] || [ "$1" == "-r" ]; then
    echo "🔄 Forcing rebuild..."
    docker-compose down
    docker-compose build --no-cache
fi

# Start the service
echo "🚀 Starting MCP server..."
docker-compose up -d

# Wait a moment for startup
sleep 3

# Check if the container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ MCP Server started successfully!"
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "📋 To view logs: docker-compose -f $SCRIPT_DIR/docker-compose.yml logs -f"
    echo "🛑 To stop: docker-compose -f $SCRIPT_DIR/docker-compose.yml down"
else
    echo "❌ Failed to start MCP server"
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi