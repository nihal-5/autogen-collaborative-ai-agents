"""
AutoGen Multi-Agent Dashboard - Professional Dark Theme
Real-time process transparency with workflow streaming
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

app = FastAPI(title="AutoGen Multi-Agent System")
model = OpenAIChatCompletionClient(model="gpt-4o-mini")


async def run_agent_system(task: str):
    """Run 4-agent system with full process transparency"""
    
    # Create agents
    researcher = AssistantAgent(
        name="Researcher",
        model_client=model,
        tools=[search_web],
        system_message="Research and provide concise findings. Be brief.",
        reflect_on_tool_use=True
    )
    
    coder = AssistantAgent(
        name="Coder",
        model_client=model,
        tools=[execute_python_code],
        system_message="Write and test code. Keep it simple and show results.",
        reflect_on_tool_use=True
    )
    
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model,
        system_message="Review briefly and provide key feedback."
    )
    
    synthesizer = AssistantAgent(
        name="Synthesizer",
        model_client=model,
        system_message="Provide final summary. Be concise."
    )
    
    team = RoundRobinGroupChat(
        [researcher, coder, reviewer, synthesizer],
        termination_condition=MaxMessageTermination(10)
    )
    
    yield f"data: {json.dumps({'type': 'start', 'task': task})}\n\n"
    
    try:
        result = await team.run(task=task)
        
        for i, msg in enumerate(result.messages):
            # Extract content
            content = str(msg.content) if msg.content else ""
            
            # Check if it's a function call
            is_tool = "FunctionCall" in content or "FunctionExecution" in content
            
            event_data = {
                'type': 'message',
                'id': i,
                'agent': str(msg.source),
                'content': content[:1000],  # Limit length
                'is_tool': is_tool,
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(0.05)
        
        yield f"data: {json.dumps({'type': 'complete', 'total': len(result.messages)})}\n\n"
    
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.get("/")
async def dashboard():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>AutoGen Multi-Agent System</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: #1e293b;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            overflow: hidden;
            border: 1px solid #334155;
        }
        
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 32px 40px;
            border-bottom: 1px solid #334155;
        }
        
        h1 {
            font-size: 28px;
            color: #f1f5f9;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            font-size: 15px;
            color: #94a3b8;
            font-weight: 400;
        }
        
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 20px;
        }
        
        .agent-card {
            background: #334155;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #475569;
        }
        
        .agent-name {
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
        }
        
        .agent-role {
            font-size: 11px;
            color: #64748b;
            margin-top: 4px;
        }
        
        .controls {
            padding: 32px 40px;
            background: #1e293b;
            border-bottom: 1px solid #334155;
        }
        
        label {
            display: block;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .task-input {
            width: 100%;
            padding: 14px 16px;
            font-size: 15px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #e2e8f0;
            font-family: inherit;
            transition: all 0.2s;
        }
        
        .task-input:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .suggestions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        
        .chip {
            padding: 6px 14px;
            background: #334155;
            border: 1px solid #475569;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #cbd5e1;
            transition: all 0.2s;
        }
        
        .chip:hover {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }
        
        .start-btn {
            width: 100%;
            padding: 14px;
            font-size: 16px;
            font-weight: 600;
            color: white;
            background: #3b82f6;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 16px;
        }
        
        .start-btn:hover {
            background: #2563eb;
        }
        
        .start-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .status-bar {
            padding: 14px 40px;
            background: #1f2937;
            border-bottom: 1px solid #374151;
            font-size: 13px;
            font-weight: 500;
            color: #9ca3af;
            display: none;
        }
        
        .status-bar.active {
            display: block;
        }
        
        .conversation {
            padding: 24px 40px;
            max-height: 700px;
            overflow-y: auto;
            background: #1e293b;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 16px 20px;
            background: #334155;
            border-radius: 8px;
            border-left: 3px solid #64748b;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.researcher { border-left-color: #3b82f6; }
        .message.coder { border-left-color: #10b981; }
        .message.reviewer { border-left-color: #f59e0b; }
        .message.synthesizer { border-left-color: #8b5cf6; }
        .message.tool { background: #1f2937; border-left-color: #6366f1; }
        
        .msg-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .agent-label {
            font-weight: 700;
            font-size: 13px;
            color: #f1f5f9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .timestamp {
            font-size: 11px;
            color: #64748b;
        }
        
        .msg-content {
            font-size: 14px;
            line-height: 1.6;
            color: #cbd5e1;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .tool-badge {
            display: inline-block;
            background: #6366f1;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .empty {
            text-align: center;
            padding: 80px 40px;
            color: #64748b;
        }
        
        .loading {
            display: inline-block;
        }
        
        .loading::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #475569;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AutoGen Multi-Agent System</h1>
            <p class="subtitle">Real-time collaborative AI agent workflow with process transparency</p>
            
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="agent-name">Researcher</div>
                    <div class="agent-role">Web search & analysis</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name">Coder</div>
                    <div class="agent-role">Code generation & execution</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name">Reviewer</div>
                    <div class="agent-role">Quality control & feedback</div>
                </div>
                <div class="agent-card">
                    <div class="agent-name">Synthesizer</div>
                    <div class="agent-role">Final analysis & summary</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <label>Task Description</label>
            <input type="text" class="task-input" id="taskInput" 
                   placeholder="Enter task for multi-agent collaboration"
                   value="Explain machine learning, implement linear regression in Python, review, and explain">
            
            <div class="suggestions">
                <div class="chip" onclick="setTask('Explain quantum computing basics and implement a simple qubit simulation')">Quantum Computing</div>
                <div class="chip" onclick="setTask('Research blockchain technology and create a basic implementation')">Blockchain</div>
                <div class="chip" onclick="setTask('Explain neural networks and implement a simple perceptron')">Neural Networks</div>
            </div>
            
            <button class="start-btn" id="startBtn" onclick="startWork()">
                Start Collaboration
            </button>
        </div>
        
        <div id="status" class="status-bar">
            Processing workflow<span class="loading"></span>
        </div>
        
        <div class="conversation" id="conv">
            <div class="empty">
                <p>Ready to begin. Click Start Collaboration to watch agents work together.</p>
            </div>
        </div>
    </div>
    
    <script>
        function setTask(task) {
            document.getElementById('taskInput').value = task;
        }
        
        async function startWork() {
            const task = document.getElementById('taskInput').value;
            const btn = document.getElementById('startBtn');
            const status = document.getElementById('status');
            const conv = document.getElementById('conv');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.classList.add('active');
            conv.innerHTML = '';
            
            try {
                const response = await fetch(`/stream?task=${encodeURIComponent(task)}`);
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
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
                                const time = new Date(data.timestamp).toLocaleTimeString();
                                
                                const msgDiv = document.createElement('div');
                                msgDiv.className = `message ${agentClass}`;
                                
                                let content = data.content;
                                let toolBadge = '';
                                if (data.is_tool) {
                                    toolBadge = '<span class=\"tool-badge\">TOOL EXECUTION</span><br>';
                                }
                                
                                msgDiv.innerHTML = `
                                    <div class=\"msg-header\">
                                        <span class=\"agent-label\">${data.agent}</span>
                                        <span class=\"timestamp\">${time}</span>
                                    </div>
                                    ${toolBadge}
                                    <div class=\"msg-content\">${content}</div>
                                `;
                                conv.appendChild(msgDiv);
                                conv.scrollTop = conv.scrollHeight;
                            }
                            
                            if (data.type === 'complete') {
                                status.classList.remove('active');
                                btn.disabled = false;
                                btn.textContent = 'Start New Collaboration';
                            }
                            
                            if (data.type === 'error') {
                                conv.innerHTML += `<div class=\"message\" style=\"border-left-color: #ef4444;\">
                                    <div class=\"msg-header\"><span class=\"agent-label\">ERROR</span></div>
                                    <div class=\"msg-content\">${data.message}</div>
                                </div>`;
                                status.classList.remove('active');
                                btn.disabled = false;
                                btn.textContent = 'Retry';
                            }
                        }
                    }
                }
            } catch (e) {
                conv.innerHTML = `<div class=\"message\" style=\"border-left-color: #ef4444;\">
                    <div class=\"msg-content\">Connection error: ${e.message}</div>
                </div>`;
                status.classList.remove('active');
                btn.disabled = false;
                btn.textContent = 'Retry';
            }
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/stream")
async def stream(task: str):
    return StreamingResponse(
        run_agent_system(task),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("AutoGen Multi-Agent Dashboard")
    print("="*80)
    print("\nDashboard: http://localhost:8000")
    print("Agents: 4 (Researcher, Coder, Reviewer, Synthesizer)")
    print("Features: Real-time streaming, process transparency, tool execution\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
