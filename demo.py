"""
AutoGen Multi-Agent Demo - Simple Working Example
Demonstrates team collaboration between two agents
"""

import asyncio
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

# Initialize model
model = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Create two agents
researcher = AssistantAgent(
    name="Researcher",
    model_client=model,
    system_message="You are a helpful research assistant. Find information and provide brief summaries."
)

critic = AssistantAgent(
    name="Critic",
    model_client=model,
    system_message="You review research and provide constructive feedback. When satisfied, respond with 'APPROVED'."
)

# Create team
termination = MaxMessageTermination(8)  # Stop after 8 messages
team = RoundRobinGroupChat([researcher, critic], termination_condition=termination)


async def demo():
    print("\n" + "="*80)
    print("🤖  AUTO GEN MULTI-AGENT DEMO")
    print("="*80 + "\n")
    
    task = "Explain what AutoGen is and why it's useful for AI agent development"
    
    print(f"📋 Task: {task}\n")
    print("👥 Team: Researcher + Critic\n")
    print("="*80)
    print("\n💬 CONVERSATION:\n")
    
    result = await team.run(task=task)
    
    for i, msg in enumerate(result.messages, 1):
        print(f"\n[{i}] {msg.source}:")
        print(f"   {msg.content}\n")
        print("-"*80)
    
    print("\n✅ Collaboration complete!")
    print(f"📊 Total messages: {len(result.messages)}")
    print(f"🏁 Stop reason: {result.stop_reason}\n")


if __name__ == "__main__":
    asyncio.run(demo())
