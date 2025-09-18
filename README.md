# Dopemux MVP

**ADHD-Optimized Development Platform with Leantime & Task-Master AI Integration**

Dopemux transforms chaotic development workflows into structured, attention-friendly experiences through intelligent project management and AI-powered task decomposition.

## ✨ Features

### 🧠 ADHD-First Design
- **Attention State Management**: Automatic focus duration tracking and break recommendations
- **Cognitive Load Balancing**: Smart task scheduling based on complexity and mental capacity
- **Context Preservation**: Never lose your place with automatic session saves and restoration
- **Executive Function Support**: Clear next steps and decision reduction to minimize overwhelm
- **ADHD Metadata**: Every task includes cognitive load (1-10), focus level, break reminders, and optimal timing
- **Attention-Aware Filtering**: Get tasks by attention level, cognitive capacity, and current state

### 🚀 AI-Powered Workflow
- **PRD-to-Tasks**: Transform Product Requirements Documents into actionable task breakdowns
- **Intelligent Scheduling**: Optimal task sequencing based on attention patterns and complexity
- **Bidirectional Sync**: Seamless data flow between Leantime project management and Task-Master AI
- **Real-time Optimization**: Continuous workflow adaptation based on performance metrics

### 🐳 Self-Hosted Infrastructure
- **Docker-Based Deployment**: One-command setup with docker-compose
- **Leantime Integration**: Neurodiversity-focused project management platform
- **Task-Master AI**: Advanced PRD parsing and task decomposition via MCP
- **Health Monitoring**: Comprehensive system checks and automated recovery

## 🎯 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- Node.js 18+
- 4GB+ RAM (8GB recommended)

### Installation
```bash
# Clone repository
git clone https://github.com/your-repo/dopemux-mvp.git
cd dopemux-mvp

# Automated installation (recommended)
python installers/leantime/install.py --interactive

# Manual installation
cd docker/leantime
docker-compose up -d
npm install -g claude-task-master
pip install -r requirements.txt
```

### First Use
1. **Access Leantime**: http://localhost:8080 (admin/admin)
2. **Verify Health**: `python installers/leantime/health_check.py`
3. **Create Project**: Start with a simple PRD document
4. **Enable ADHD Mode**: Configure attention tracking preferences

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Leantime      │◄──►│  Sync Manager    │◄──►│ Task-Master AI  │
│   (Projects)    │    │ (Bidirectional)  │    │ (PRD Analysis)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                       ▲
         │              ┌─────────▼─────────┐             │
         │              │ ADHD Optimizations │             │
         │              │ - Attention Mgmt   │             │
         │              │ - Context Preserve │             │
         │              │ - Cognitive Load   │             │
         │              └────────────────────┘             │
         │                                                 │
         ▼                                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Docker Services │    │     MCP Bridge   │    │  Health Checks  │
│ - MySQL         │    │   (Protocol)     │    │   & Monitoring  │
│ - Redis         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Core Components

### Leantime Bridge (`src/integrations/leantime_bridge.py`)
- **MCP Client**: Protocol-based integration with Leantime API
- **Project Management**: Create, read, update, delete operations for projects and tasks
- **ADHD Features**: Attention-level filtering, cognitive load assessment, break reminders

### Task-Master Bridge (`src/integrations/taskmaster_bridge.py`)
- **PRD Processing**: Intelligent analysis of Product Requirements Documents
- **Task Decomposition**: Break complex features into manageable chunks
- **Complexity Assessment**: Cognitive load scoring for optimal scheduling

### Sync Manager (`src/integrations/sync_manager.py`)
- **Bidirectional Sync**: Real-time data synchronization between systems
- **Conflict Resolution**: Intelligent handling of concurrent updates
- **Event Sourcing**: Complete audit trail of all changes

### ADHD Optimizations (`src/utils/adhd_optimizations.py`)
- **Attention Tracking**: Monitor focus states and recommend optimal work patterns
- **Context Management**: Preserve mental models across interruptions
- **Schedule Optimization**: Balance cognitive load and task complexity

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)**: Complete setup instructions
- **[User Guide](docs/USER_GUIDE.md)**: ADHD-optimized workflows and features
- **[API Documentation](docs/API.md)**: Complete technical reference

## 🧪 Testing

### Run Test Suite
```bash
# Full test coverage
python -m pytest tests/ --cov=src --cov-report=html

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Specific test
python -m pytest tests/unit/test_adhd_optimizations.py -v
```

### Test Coverage
- **Unit Tests**: 100% coverage for all modules
- **Integration Tests**: Complete workflow validation
- **Health Checks**: System monitoring and recovery
- **Performance Tests**: Load testing and optimization

## 🎨 ADHD-Friendly Features

### Attention Management
- **Focus Sessions**: 25-minute blocks with automatic break reminders
- **Attention Detection**: Real-time assessment of cognitive state
- **Context Switching**: Minimal disruption with preserved mental models
- **Progress Visualization**: Clear indicators of completion and remaining work

### Cognitive Load Optimization
- **Task Complexity**: 1-10 scoring system for mental effort estimation
- **Schedule Balancing**: Mix of high/medium/low complexity tasks
- **Energy Matching**: Align challenging work with peak attention periods
- **Break Integration**: Regular rest periods built into workflow

### Executive Function Support
- **Decision Reduction**: Maximum 3 options presented at once
- **Clear Next Steps**: Always know what to do next
- **Prerequisites Tracking**: Dependencies clearly identified
- **Completion Celebration**: Positive reinforcement for task completion

## 🤝 Contributing

### Development Setup
```bash
# Development installation
git clone https://github.com/your-repo/dopemux-mvp.git
cd dopemux-mvp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
pip install -r requirements-dev.txt
```

### ADHD-Friendly Contributions
- **Any format welcome**: Bullet points, voice notes, rough ideas
- **No judgment**: All questions and suggestions valued
- **Flexible participation**: Contribute when attention allows
- **Clear guidelines**: Specific steps for each contribution type

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Leantime Team**: For creating neurodiversity-focused project management
- **Task-Master AI**: For intelligent task decomposition capabilities
- **ADHD Community**: For insights into attention-friendly development workflows
- **MCP Protocol**: For enabling seamless AI service integration

---

**Built with ❤️ for the ADHD developer community**

*Making development accessible, one focused session at a time.*
