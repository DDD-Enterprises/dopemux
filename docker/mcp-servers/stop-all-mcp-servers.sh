#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping all Dopemux MCP servers..."
docker-compose down

echo "✅ All MCP servers stopped"
