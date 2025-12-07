# AutoGen Multi-Agent Collaboration System

A production-quality multi-agent system built with Microsoft's AutoGen framework, demonstrating real-time AI agent collaboration with web interface.

## What This Project Does

Watch multiple AI agents work together to solve complex tasks. Agents have specialized roles (Researcher, Coder, Reviewer, Synthesizer) and collaborate like a real team to accomplish goals.

## Key Features

**✨ Multiple Agent Configurations**
- 2-Agent Team: Researcher + Critic (simple collaboration)
- 4-Agent Team: Researcher + Coder + Reviewer + Synthesizer (complex tasks)

**🔧 Real Tools**
- Web Search (Google Serper API)
- Python Code Execution (safe sandbox)
- File Management
- Research & Analysis

**🌐 Web Dashboard**
- Real-time conversation streaming
- Beautiful UI to watch agents collaborate
- Live status updates

**🎯 Production Quality**
- Proper error handling
- Clean architecture
- Natural conversation flow
- Tested end-to-end

## Quick Start

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your API keys to .env

# Run demos
python demo.py              # 2-agent simple demo
python multi_agent.py       # 4-agent complex demo
python dashboard.py         # Web interface (http://localhost:8000)
```

## What Makes This Impressive

**1. Real Agent Collaboration**
Unlike simple chatbots, these agents actually work together:
- Agents build on each other's work
- They provide feedback and iterate
- Each has specialized skills and tools
- Natural team dynamics emerge

**2. Multiple Patterns Demonstrated**
- RoundRobinGroupChat (team coordination)
- Tool-equipped agents (real actions)
- Structured outputs (quality control)
- Termination conditions (smart stopping)

**3. Production Features**
- Web dashboard for live monitoring
- Error handling and retries
- Conversation history
- Clean, maintainable code

## Agent Roles

**Researcher** 🔍
- Searches the web for information
- Gathers data and sources
- Provides research summaries

**Coder** 💻
- Writes Python code
- Executes and tests code
- Saves work to files

**Reviewer** 👀
- Reviews research and code quality
- Provides constructive feedback
- Ensures accuracy

**Synthesizer** 🎯
- Makes final decisions
- Combines all inputs
- Provides recommendations

## Example Tasks

Try these with the multi-agent system:

```bash
"Research quantum computing, write a simul ation, review it, and summarize"
"Find ML algorithms, implement linear regression, review, and explain"
"Research blockchain, create a basic implementation, review, and conclude"
```

## Technical Stack

- **AutoGen 0.4.0**: Multi-agent framework
- **FastAPI**: Web dashboard backend
- **OpenAI GPT-4**: Agent intelligence
- **Google Serper**: Web search
- **Python 3.13**: Runtime

## Architecture

```
AutoGen System
├── Agents (specialized AI roles)
│   ├── AssistantAgent (with tools)
│   └── Team coordination
├── Tools (real-world actions)
│   ├── Web search
│   ├── Code execution
│   └── File management
└── Dashboard (visualization)
    ├── Real-time streaming
    └── Conversation display
```

## Why This Matters

This demonstrates:
1. **Multi-agent collaboration** - how AI agents work together
2. **Tool integration** - agents can take real actions
3. **Production quality** - proper architecture, not just a demo
4. **Team dynamics** - agents have roles and coordinate naturally

Unlike simple chat demos, this shows AI agents truly collaborating to solve problems - like a real development team.

## Lessons Learned

**What worked well:**
- AutoGen's RoundRobinGroupChat makes coordination simple
- Tool integration is straightforward
- Agents naturally develop team dynamics

**Key insights:**
- Message limits prevent infinite loops
- Specialized agents work better than generalists
- Visual feedback (dashboard) makes collaboration clear

## Future Enhancements

- Add more specialized agents (Tester, Designer, etc.)
- Implement AutoGen Core for distributed agents
- Add human-in-the-loop approval
- Persistent conversation history
- Voice interface integration

## License

MIT License - feel free to learn from and build upon this.

---

**Built to showcase production-quality multi-agent AI systems.**

_This project demonstrates advanced agentic AI patterns using Microsoft's AutoGen framework._
