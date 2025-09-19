#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting all Dopemux MCP servers..."

# Validate environment
for server_dir in */; do
    if [ -f "$server_dir/.env" ]; then
        echo "✅ Found configuration for ${server_dir%/}"
    fi
done

echo ""
echo "🔨 Building and starting containers..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ All MCP servers started successfully!"
echo ""
echo "📋 Management commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop all:  docker-compose down"
echo "   Restart:   ./start-all-mcp-servers.sh"
