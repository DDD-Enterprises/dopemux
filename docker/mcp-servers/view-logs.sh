#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -n "$1" ]; then
    echo "📋 Viewing logs for $1..."
    docker-compose logs -f "$1"
else
    echo "📋 Viewing logs for all MCP servers..."
    docker-compose logs -f
fi
