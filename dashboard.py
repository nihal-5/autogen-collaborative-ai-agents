"""
AutoGen Multi-Agent Dashboard - PRODUCTION VERSION
4 specialized agents with real-time collaboration and tool execution
"""

import asyncio
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from tools import search_web, execute_python_code, save_to_file

load_dotenv()

app = FastAPI(title="AutoGen 4-Agent System")
model = OpenAIChatCompletionClient(model="gpt-4o-mini")


async def run_4_agent_system(task: str):
    """Run 4-agent collaboration with tools"""
    
    # Create 4 specialized agents
    researcher = AssistantAgent(
        name="Researcher",
        model_client=model,
        tools=[search_web],
        system_message="You search for information and provide research. Be concise.",
        reflect_on_tool_use=True
    )
    
    coder = AssistantAgent(
        name="Coder",
        model_client=model,
        tools=[execute_python_code, save_to_file],
        system_message="You write and test Python code. Show results.",
        reflect_on_tool_use=True
    )
    
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model,
        system_message="Review work and provide feedback. Be constructive."
    )
    
    synthesizer = AssistantAgent(
        name="Synthesizer",
        model_client=model,
        system_message="Synthesize all inputs and provide final answer."
    )
    
    # Create 4-agent team
    team = RoundRobinGroupChat(
        [researcher, coder, reviewer, synthesizer],
        termination_condition=MaxMessageTermination(12)
    )
    
    # Stream start
    yield f"data: {json.dumps({'type': 'start', 'task': task, 'agents': 4})}\n\n"
    
    # Run collaboration
    result = await team.run(task=task)
    
    # Stream messages
    for i, msg in enumerate(result.messages):
        event_data = {
            'type': 'message',
            'id': i,
            'agent': msg.source,
            'content': msg.content,
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(event_data)}\n\n"
        await asyncio.sleep(0.1)
    
    yield f"data: {json.dumps({'type': 'complete', 'total': len(result.messages)})}\n\n"


@app.get("/")
async def dashboard():
    """Serve production dashboard"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AutoGen 4-Agent System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.98);
                border-radius: 24px;
                box-shadow: 0 25px 80px rgba(0,0,0,0.4);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                text-align: center;
                position: relative;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') bottom;
                background-size: cover;
                opacity: 0.3;
            }
            
            h1 {
                font-size: 3.5em;
                color: white;
                margin-bottom: 15px;
                font-weight: 800;
                letter-spacing: -1px;
                position: relative;
            }
            
            .subtitle {
                font-size: 1.4em;
                color: rgba(255,255,255,0.95);
                font-weight: 300;
                position: relative;
            }
            
            .agent-badges {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-top: 25px;
                flex-wrap: wrap;
                position: relative;
            }
            
            .badge {
                background: rgba(255,255,255,0.25);
                backdrop-filter: blur(10px);
                padding: 12px 24px;
                border-radius: 25px;
                color: white;
                font-weight: 600;
                font-size: 0.95em;
                border: 2px solid rgba(255,255,255,0.3);
            }
            
            .controls {
                padding: 40px;
                background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
            }
            
            .task-section {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                font-weight: 700;
                color: #334155;
                margin-bottom: 12px;
                font-size: 1.1em;
            }
            
            .task-input {
                width: 100%;
                padding: 18px 24px;
                font-size: 17px;
                border: 3px solid #e2e8f0;
                border-radius: 16px;
                transition: all 0.3s;
                font-family: inherit;
            }
            
            .task-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }
            
            .suggestions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 15px;
            }
            
            .suggestion-chip {
                padding: 8px 16px;
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 0.9em;
                color: #475569;
            }
            
            .suggestion-chip:hover {
                background: #667eea;
                color: white;
                border-color: #667eea;
                transform: translateY(-2px);
            }
            
            .start-btn {
                width: 100%;
                padding: 20px;
                font-size: 20px;
                font-weight: 700;
                color: white;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                margin-top: 20px;
            }
            
            .start-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
            }
            
            .start-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .conversation {
                padding: 40px;
                max-height: 700px;
                overflow-y: auto;
                background: #f8fafc;
            }
            
            .message {
                margin-bottom: 25px;
                padding: 24px;
                border-radius: 16px;
                animation: slideIn 0.4s ease-out;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .researcher {
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border-left: 5px solid #3b82f6;
            }
            
            .coder {
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border-left: 5px solid #10b981;
            }
            
            .reviewer {
                background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
                border-left: 5px solid #ec4899;
            }
            
            .synthesizer {
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-left: 5px solid #f59e0b;
            }
            
            .agent-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }
            
            .agent-icon {
                font-size: 28px;
            }
            
            .agent-name {
                font-weight: 800;
                font-size: 1.2em;
                color: #1e293b;
            }
            
            .message-content {
                line-height: 1.7;
                color: #334155;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .status {
                padding: 20px 40px;
                text-align: center;
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-top: 3px solid #f59e0b;
                font-weight: 700;
                font-size: 1.1em;
                color: #92400e;
            }
            
            .thinking {
                display: inline-block;
                margin-left: 10px;
            }
            
            .thinking span {
                animation: blink 1.4s infinite;
                font-size: 24px;
            }
            
            .thinking span:nth-child(2) { animation-delay: 0.2s; }
            .thinking span:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes blink {
                0%, 100% { opacity: 0.2; }
                50% { opacity: 1; }
            }
            
            .empty-state {
                text-align: center;
                padding: 80px 40px;
                color: #94a3b8;
            }
            
            .empty-state-icon {
                font-size: 80px;
                margin-bottom: 20px;
                opacity: 0.5;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AutoGen Multi-Agent System</h1>
                <p class="subtitle">4 Specialized AI Agents Collaborating in Real-Time</p>
                <div class="agent-badges">
                    <div class="badge">🔍 Researcher</div>
                    <div class="badge">💻 Coder</div>
                    <div class="badge">👀 Reviewer</div>
                    <div class="badge">🎯 Synthesizer</div>
                </div>
            </div>
            
            <div class="controls">
                <div class="task-section">
                    <label>Enter Your Task</label>
                    <input type="text" class="task-input" id="taskInput" 
                           placeholder="What would you like the agents to work on?"
                           value="Research quantum computing, write a Python simulation of a qubit, review the code, and provide a summary">
                    
                    <div class="suggestions">
                        <div class="suggestion-chip" onclick="setTask('Research quantum computing, write a Python simulation, review it, and summarize')">⚛️ Quantum Computing</div>
                        <div class="suggestion-chip" onclick="setTask('Explain machine learning, implement linear regression in Python, review, and explain')">🧠 Machine Learning</div>
                        <div class="suggestion-chip" onclick="setTask('Research blockchain technology, create a simple implementation, review, and conclude')">⛓️ Blockchain</div>
                    </div>
                </div>
                
                <button class="start-btn" id="startBtn" onclick="startConversation()">
                    🚀 Start 4-Agent Collaboration
                </button>
            </div>
            
            <div id="status" class="status" style="display: none;">
                4 AI agents are working<span class="thinking"><span>.</span><span>.</span><span>.</span></span>
            </div>
            
            <div class="conversation" id="conversation">
                <div class="empty-state">
                    <div class="empty-state-icon">💭</div>
                    <h3>Ready to Watch AI Agents Collaborate</h3>
                    <p>Click the button above to see 4 specialized agents work together</p>
                </div>
            </div>
        </div>
        
        <script>
            function setTask(task) {
                document.getElementById('taskInput').value = task;
            }
            
            async function startConversation() {
                const task = document.getElementById('taskInput').value;
                const btn = document.getElementById('startBtn');
                const status = document.getElementById('status');
                const conv = document.getElementById('conversation');
                
                btn.disabled = true;
                btn.textContent = '⏳ Agents Working...';
                status.style.display = 'block';
                conv.innerHTML = '';
                
                const response = await fetch(`/stream?task=${encodeURIComponent(task)}`);
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                const agentIcons = {
                    'Researcher': '🔍',
                    'Coder': '💻',
                    'Reviewer': '👀',
                    'Synthesizer': '🎯'
                };
                
                while (true) {
                    const {value, done} = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.type === 'message') {
                                const agentClass = data.agent.toLowerCase();
                                const icon = agentIcons[data.agent] || '🤖';
                                const preview = data.content.length > 800 ? data.content.substring(0, 800) + '...' : data.content;
                                
                                const msgDiv = document.createElement('div');
                                msgDiv.className = `message ${agentClass}`;
                                msgDiv.innerHTML = `
                                    <div class="agent-header">
                                        <span class="agent-icon">${icon}</span>
                                        <span class="agent-name">${data.agent}</span>
                                    </div>
                                    <div class="message-content">${preview}</div>
                                `;
                                conv.appendChild(msgDiv);
                                conv.scrollTop = conv.scrollHeight;
                            }
                            
                            if (data.type === 'complete') {
                                status.style.display = 'none';
                                btn.disabled = false;
                                btn.textContent = '🚀 Start New Collaboration';
                            }
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/stream")
async def stream_conversation(task: str):
    """Stream 4-agent conversation"""
    return StreamingResponse(
        run_4_agent_system(task),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("🚀 AUTOGEN 4-AGENT DASHBOARD")
    print("="*80)
    print("\n📊 Dashboard: http://localhost:8000")
    print("👥 Agents: Researcher, Coder, Reviewer, Synthesizer")
    print("🔧 Tools: Web Search, Code Execution, File Management\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
