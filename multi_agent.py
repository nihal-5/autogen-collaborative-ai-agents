"""
AutoGen Multi-Agent System - Advanced 4-Agent Collaboration
Demonstrates complex team dynamics with multiple specialized agents
"""

import asyncio
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools import search_web, execute_python_code, save_to_file

load_dotenv()

# Initialize model
model = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Create 4 specialized agents
researcher = AssistantAgent(
    name="Researcher",
    model_client=model,
    tools=[search_web],
    system_message="You are a research specialist. Search for information and provide detailed findings.",
    reflect_on_tool_use=True
)

coder = AssistantAgent(
    name="Coder",
    model_client=model,
    tools=[execute_python_code, save_to_file],
    system_message="You are a Python developer. Write code to solve problems and test it.",
    reflect_on_tool_use=True
)

reviewer = AssistantAgent(
    name="Reviewer",
    model_client=model,
    system_message="You review research and code. Provide constructive feedback and suggest improvements."
)

synthesizer = AssistantAgent(
    name="Synthesizer",
    model_client=model,
    system_message="You synthesize all inputs into a final recommendation. When ready, say 'FINAL ANSWER:' followed by the conclusion."
)

# Create 4-agent team
team = RoundRobinGroupChat(
    [researcher, coder, reviewer, synthesizer],
    termination_condition=MaxMessageTermination(12)
)


async def run_complex_task(task: str):
    """Run a complex multi-agent collaboration"""
    print("\n" + "="*100)
    print("🚀  AUTOGEN 4-AGENT COLLABORATION SYSTEM")
    print("="*100 + "\n")
    
    print(f"📋 Task: {task}\n")
    print("👥 Team:")
    print("   1. Researcher (with web search)")
    print("   2. Coder (with code execution)")
    print("   3. Reviewer (quality control)")
    print("   4. Synthesizer (final decision)\n")
    print("="*100)
    print("\n💬 AGENT COLLABORATION:\n")
    
    result = await team.run(task=task)
    
    for i, msg in enumerate(result.messages, 1):
        agent_emoji = {
            "Researcher": "🔍",
            "Coder": "💻",
            "Reviewer": "👀",
            "Synthesizer": "🎯"
        }
        emoji = agent_emoji.get(msg.source, "🤖")
        
        print(f"\n[{i}] {emoji} {msg.source}:")
        content_preview = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
        print(f"   {content_preview}\n")
        print("-"*100)
    
    print(f"\n\n✅ Collaboration Complete!")
    print(f"📊 Total Messages: {len(result.messages)}")
    print(f"🎭 Agents Involved: 4 (Researcher, Coder, Reviewer, Synthesizer)")
    print(f"🏁 Stop Reason: {result.stop_reason}\n")


# Example complex tasks
TASKS = [
    "Research what is quantum computing, write a simple Python simulation of a qubit, review the code, and provide a final summary.",
    "Find information about machine learning algorithms, implement a simple linear regression in Python, review it, and summarize the approach.",
    "Research blockchain technology, write Python code to create a basic blockchain, review the implementation, and provide conclusions."
]


async def main():
    # Run the first complex task
    await run_complex_task(TASKS[0])


if __name__ == "__main__":
    asyncio.run(main())
