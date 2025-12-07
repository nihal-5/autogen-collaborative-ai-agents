"""
AutoGen Multi-Agent Web Dashboard
Real-time visualization of agent conversations
"""

import asyncio
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AutoGen Multi-Agent Dashboard")

# Initialize model
model = OpenAIChatCompletionClient(model="gpt-4o-mini")


async def run_agent_conversation(task: str):
    """Run multi-agent conversation and stream updates"""
    
    # Create agents
    researcher = AssistantAgent(
        name="Researcher",
        model_client=model,
        system_message="You are a research assistant. Provide brief, informative responses."
    )
    
    critic = AssistantAgent(
        name="Critic",
        model_client=model,
        system_message="You review work and provide feedback. Say 'APPROVED' when satisfied."
    )
    
    # Create team
    team = RoundRobinGroupChat([researcher, critic], termination_condition=MaxMessageTermination(8))
    
    # Stream events
    yield f"data: {json.dumps({'type': 'start', 'task': task})}\n\n"
    
    result = await team.run(task=task)
    
    for i, msg in enumerate(result.messages):
        event_data = {
            'type': 'message',
            'id': i,
            'agent': msg.source,
            'content': msg.content,
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(event_data)}\n\n"
        await asyncio.sleep(0.1)  # Small delay for UI
    
    yield f"data: {json.dumps({'type': 'complete', 'total': len(result.messages)})}\n\n"


@app.get("/")
async def dashboard():
    """Serve dashboard HTML"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AutoGen Multi-Agent Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
 }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { font-size: 1.2em; opacity: 0.9; }
            .controls {
                padding: 30px;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            .task-input {
                width: 100%;
                padding: 15px;
                font-size: 16px;
                border: 2px solid #667eea;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            .start-btn {
                width: 100%;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .start-btn:hover { transform: scale(1.05); }
            .start-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: scale(1);
            }
            .conversation {
                padding: 30px;
                max-height: 600px;
                overflow-y: auto;
            }
            .message {
                margin-bottom: 20px;
                padding: 20px;
                border-radius: 15px;
                animation: fadeIn 0.5s;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .researcher {
                background: #e3f2fd;
                border-left: 4px solid #2196F3;
            }
            .critic {
                background: #f3e5f5;
                border-left: 4px solid #9c27b0;
            }
            .agent-name {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            .message-content {
                line-height: 1.6;
                white-space: pre-wrap;
            }
            .status {
                padding: 15px 30px;
                text-align: center;
                background: #fff3cd;
                border-top: 1px solid #ffc107;
                font-weight: bold;
            }
            .thinking {
                display: inline-block;
                margin-left: 10px;
            }
            .thinking span {
                animation: blink 1.4s infinite;
                font-size: 20px;
            }
            .thinking span:nth-child(2) { animation-delay: 0.2s; }
            .thinking span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes blink {
                0%, 100% { opacity: 0.2; }
                50% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AutoGen Multi-Agent System</h1>
                <p class="subtitle">Watch AI agents collaborate in real-time</p>
            </div>
            
            <div class="controls">
                <input type="text" class="task-input" id="taskInput" 
                       placeholder="Enter a task for the agents..." 
                       value="Explain quantum computing in simple terms">
                <button class="start-btn" id="startBtn" onclick="startConversation()">
                    Start Conversation
                </button>
            </div>
            
            <div id="status" class="status" style="display: none;">
                Agents are thinking<span class="thinking"><span>.</span><span>.</span><span>.</span></span>
            </div>
            
            <div class="conversation" id="conversation"></div>
        </div>
        
        <script>
            async function startConversation() {
                const task = document.getElementById('taskInput').value;
                const btn = document.getElementById('startBtn');
                const status = document.getElementById('status');
                const conv = document.getElementById('conversation');
                
                btn.disabled = true;
                btn.textContent = 'Agents Working...';
                status.style.display = 'block';
                conv.innerHTML = '';
                
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
                                const msgDiv = document.createElement('div');
                                msgDiv.className = `message ${data.agent.toLowerCase()}`;
                                msgDiv.innerHTML = `
                                    <div class="agent-name">${data.agent}</div>
                                    <div class="message-content">${data.content.substring(0, 500)}${data.content.length > 500 ? '...' : ''}</div>
                                `;
                                conv.appendChild(msgDiv);
                                conv.scrollTop = conv.scrollHeight;
                            }
                            
                            if (data.type === 'complete') {
                                status.style.display = 'none';
                                btn.disabled = false;
                                btn.textContent = 'Start New Conversation';
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
    """Stream agent conversation"""
    return StreamingResponse(
        run_agent_conversation(task),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting AutoGen Dashboard...")
    print("📊 Open http://localhost:8000 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
