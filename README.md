# Dopemux MVP

**ADHD-optimized development platform that wraps Claude Code with custom configurations**

Dopemux is a Python CLI tool designed specifically for developers with ADHD, providing specialized accommodations and features that enhance productivity and reduce cognitive load during software development.

## Features

### 🧠 ADHD Core Accommodations
- **Context Preservation**: Automatic saving and restoration of work state every 30 seconds
- **Attention Monitoring**: Real-time tracking of focus patterns and attention state
- **Task Decomposition**: Intelligent breaking of complex tasks into 25-minute chunks
- **Gentle Guidance**: Non-intrusive prompts and decision reduction

### ⚡ Claude Code Integration
- **Custom Launch**: Launches Claude Code with ADHD-optimized configurations
- **MCP Server Management**: Integrates specialized MCP servers for enhanced functionality
- **Project Configuration**: Automatic setup of project-specific `.claude/` configurations

### 📊 Productivity Features
- **Session Management**: Save and restore complete development sessions
- **Time Awareness**: Multiple time displays and deadline warnings
- **Progress Visualization**: ASCII progress bars and completion indicators
- **Memory Augmentation**: External memory system for decisions and context

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/dopemux/dopemux-mvp.git
cd dopemux-mvp

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install dopemux
```

### Basic Usage

```bash
# Initialize a new project with Dopemux
dopemux init

# Start a development session with Claude Code
dopemux start

# Save current context
dopemux save

# Restore previous session
dopemux restore

# Check attention and focus metrics
dopemux status

# Manage tasks with ADHD-friendly chunking
dopemux task
```

## Commands

| Command | Description |
|---------|-------------|
| `dopemux init` | Initialize project with `.dopemux` configuration |
| `dopemux start` | Launch custom Claude Code instance |
| `dopemux save` | Save current development context |
| `dopemux restore` | Restore previous context |
| `dopemux status` | Show attention/focus metrics |
| `dopemux task` | Manage tasks with ADHD chunking |

## Configuration

### Global Configuration
Dopemux uses your existing `~/.claude/` configuration and extends it with ADHD-specific features.

### Project Configuration
Each project gets a `.claude/` directory with:
- `claude.md`: ADHD-first development instructions
- `session.md`: Session persistence patterns
- `context.md`: Context management strategies
- `llms.md`: Multi-model configuration

## ADHD Research Foundation

Dopemux is built on evidence-based ADHD research:

- **Working Memory Deficits**: Large magnitude deficits (d = 1.62-2.03) in ADHD population
- **Executive Function Impairments**: 75-81% experience significant challenges
- **Time Processing**: 25-40% consistent underestimation with temporal distortion
- **AI Support Effectiveness**: 87-93% accuracy in AI-powered accommodation systems

## Architecture

```
dopemux-mvp/
├── src/dopemux/
│   ├── cli.py              # Main CLI entry point
│   ├── adhd/               # ADHD feature modules
│   │   ├── context_manager.py
│   │   ├── attention_monitor.py
│   │   └── task_decomposer.py
│   ├── claude/             # Claude Code integration
│   │   ├── launcher.py
│   │   └── configurator.py
│   └── config/             # Configuration management
│       └── manager.py
├── docs/                   # Documentation
├── tasks/                  # Task management
└── tests/                  # Test suite
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
isort src/ tests/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dopemux

# Run specific test types
pytest -m unit
pytest -m integration
```

## Roadmap

### MVP (Current)
- [x] Project structure and CLI framework
- [ ] Basic Claude Code launcher
- [ ] Context preservation system
- [ ] Simple attention monitoring
- [ ] Task decomposition engine

### Phase 2
- [ ] Advanced MCP server integration
- [ ] Memory system (Letta Framework)
- [ ] Visual workflow UI (Ratatui)
- [ ] Multi-model orchestration (zen-mcp)

### Phase 3
- [ ] TaskMaster integration
- [ ] Enterprise deployment
- [ ] Advanced analytics
- [ ] Custom agent framework

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [Issues](https://github.com/dopemux/dopemux-mvp/issues)
- [Documentation](https://docs.dopemux.dev)
- [Discussions](https://github.com/dopemux/dopemux-mvp/discussions)

---

**Built with ❤️ for the ADHD developer community**
