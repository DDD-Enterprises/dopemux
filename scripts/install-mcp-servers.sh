#!/bin/bash
# Dopemux MCP Servers Installation Script
# This script installs all supported MCP servers for optimal ADHD development support

set -e

echo "🚀 Dopemux MCP Servers Installation"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status $BLUE "📋 Checking prerequisites..."

if ! command_exists node; then
    print_status $RED "❌ Node.js not found. Please install Node.js 16+ first."
    exit 1
fi

if ! command_exists npm; then
    print_status $RED "❌ npm not found. Please install npm first."
    exit 1
fi

print_status $GREEN "✅ Node.js and npm found"

# Install TypeScript compiler (required for some servers)
print_status $BLUE "📦 Installing TypeScript compiler..."
npm install -g typescript || {
    print_status $YELLOW "⚠️ TypeScript installation failed, but continuing..."
}

echo ""
print_status $BLUE "🔧 Installing MCP Servers..."
echo ""

# Array of MCP servers to install
declare -A MCP_SERVERS
MCP_SERVERS[context7]="context7-mcp"
MCP_SERVERS[claude-context]="@zilliz/claude-context-mcp@latest"
MCP_SERVERS[morphllm-fast-apply]="morphllm-fast-apply-mcp"
MCP_SERVERS[exa]="exa-mcp"
MCP_SERVERS[leantime]="leantime-mcp"

# Install each server
for server_name in "${!MCP_SERVERS[@]}"; do
    package_name="${MCP_SERVERS[$server_name]}"

    print_status $BLUE "📦 Installing $server_name ($package_name)..."

    if npm install -g "$package_name"; then
        print_status $GREEN "✅ $server_name installed successfully"
    else
        print_status $YELLOW "⚠️ Failed to install $server_name - may have build issues"

        # Special handling for problematic servers
        if [[ "$server_name" == "leantime" ]]; then
            print_status $YELLOW "   Note: Leantime MCP server has known TypeScript compilation issues"
            print_status $YELLOW "   It will be disabled by default in Dopemux configuration"
        fi
    fi
    echo ""
done

echo ""
print_status $BLUE "🔍 Verifying installations..."

# Check which servers are available
available_servers=()
failed_servers=()

for server_name in "${!MCP_SERVERS[@]}"; do
    package_name="${MCP_SERVERS[$server_name]}"

    # Try to find the installed package
    if npm list -g "$package_name" >/dev/null 2>&1; then
        available_servers+=("$server_name")
        print_status $GREEN "✅ $server_name is available"
    else
        failed_servers+=("$server_name")
        print_status $RED "❌ $server_name installation failed"
    fi
done

echo ""
print_status $BLUE "📊 Installation Summary"
print_status $GREEN "✅ Successfully installed: ${#available_servers[@]} servers"
if [[ ${#failed_servers[@]} -gt 0 ]]; then
    print_status $YELLOW "⚠️ Failed installations: ${#failed_servers[@]} servers"
    print_status $YELLOW "   Failed servers: ${failed_servers[*]}"
fi

echo ""
print_status $BLUE "🔧 Next Steps:"
echo "1. Set up required environment variables:"
echo "   export OPENAI_API_KEY='your_openai_key'"
echo "   export OPENROUTER_API_KEY='your_openrouter_key'"
echo "   export EXA_API_KEY='your_exa_key'"
echo "   export LEANTIME_URL='https://your-leantime-instance.com'"
echo "   export LEANTIME_API_KEY='your_leantime_key'"
echo ""
echo "2. Run 'dopemux start' to launch with MCP servers enabled"
echo ""

if [[ ${#failed_servers[@]} -gt 0 ]]; then
    print_status $YELLOW "⚠️ Some servers failed to install. Dopemux will work with available servers."
    print_status $YELLOW "   Check the Dopemux documentation for troubleshooting steps."
fi

print_status $GREEN "🎉 MCP server installation complete!"