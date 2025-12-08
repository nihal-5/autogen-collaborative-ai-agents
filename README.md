# AutoGen Multi-Agent System

Production-quality multi-agent collaboration system using Microsoft's AutoGen framework with professional dark theme dashboard.

## 🚀 Live Demo

**[View in AI Portfolio Dashboard](https://unharmable-threadlike-ruth.ngrok-free.dev)** | **[Direct Access](https://unharmable-threadlike-ruth.ngrok-free.dev:8000)**

> Part of **[Nihal's AI Portfolio](https://unharmable-threadlike-ruth.ngrok-free.dev)** - Unified dashboard featuring 5 cutting-edge AI services

## Features

**4 Specialized Agents:**
- Researcher: Web search and information gathering
- Coder: Python code generation and execution
- Reviewer: Quality control and feedback
- Synthesizer: Final analysis and recommendations

**Production Dashboard:**
- Professional dark theme interface
- Real-time agent collaboration streaming
- Process transparency with tool execution visibility
- Timestamped messages with color-coded agents

**Comprehensive Tools:**
- Web search via Google Serper API
- Python code execution (numpy, pandas, matplotlib, scikit-learn)
- File management operations
- Safe sandboxed environment

## Quick Start

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your OPENAI_API_KEY and SERPER_API_KEY to .env

# Run dashboard
python dashboard.py
# Open https://unharmable-threadlike-ruth.ngrok-free.dev:8000
```

## Available Demos

1. **dashboard.py** - Professional web UI with 4-agent system (PRIMARY)
2. **multi_agent.py** - CLI version with 4 agents and tools
3. **demo.py** - Simple 2-agent collaboration
4. **autogen_core_demo.py** - RoutedAgent and Runtime patterns
5. **app.py** - Code review team example

## Technical Stack

- AutoGen 0.4.0 (multi-agent framework)
- FastAPI (web backend)
- Server-Sent Events (real-time streaming)
- OpenAI GPT-4 (agent intelligence)
- Google Serper (web search)
- Python scientific libraries (numpy, pandas, matplotlib, scikit-learn)

## Architecture

```
Dashboard (FastAPI + SSE)
├── 4 Specialized Agents
│   ├── Researcher (web search tool)
│   ├── Coder (code execution tool)
│   ├── Reviewer (quality control)
│   └── Synthesizer (final summary)
├── RoundRobinGroupChat (team coordination)
├── Tool Integration (search, execute, files)
└── Real-time Streaming (process transparency)
```

## Example Tasks

- "Explain quantum computing and implement a qubit simulation"
- "Research machine learning and implement linear regression"
- "Analyze blockchain technology and create basic implementation"

## Requirements

- Python 3.10+
- OpenAI API key
- Google Serper API key (optional, for web search)

## Production Quality

- Clean modular code structure
- Error handling and graceful degradation
- Professional UI/UX design
- Comprehensive documentation
- Tested end-to-end


## License

MIT License

---

**Production-ready multi-agent AI system with professional dashboard and comprehensive tool integration.**
