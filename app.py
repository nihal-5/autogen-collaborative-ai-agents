"""
AutoGen Multi-Agent Team - Code Review Scenario
A production-quality multi-agent system using AutoGen
"""

import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
from tools import search_web, execute_python_code, save_to_file

load_dotenv()

# Initialize model
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Create agents
coder = AssistantAgent(
    name="Coder",
    model_client=model_client,
    tools=[execute_python_code, save_to_file],
    system_message="""You are an expert Python developer. Write clean, efficient code. 
When asked to solve a problem, write the code and test it using execute_python_code tool.""",
    reflect_on_tool_use=True
)

reviewer = AssistantAgent(
    name="Reviewer",
    model_client=model_client,
    system_message="""You are a senior code reviewer. Review code for:
- Correctness and logic errors
- Edge cases and error handling
- Code quality and best practices
Provide constructive feedback. When satisfied, say 'APPROVED'."""
)

# Create team
termination = TextMentionTermination("APPROVED")
team = RoundRobinGroupChat([coder, reviewer], termination_condition=termination, max_turns=10)


async def run_code_review(task: str):
    """Run a code review session"""
    print(f"\n🚀 Starting code review task:")
    print(f"📋 Task: {task}\n")
    print("="*80)
    
    result = await team.run(task=task)
    
    print("\n" + "="*80)
    print("\n📊 CONVERSATION SUMMARY:")
    print("="*80)
    
    for i, message in enumerate(result.messages, 1):
        print(f"\n[{i}] {message.source}:")
        print(f"{message.content[:500]}...")  # Truncate for readability
        print("-"*80)
    
    return result


# Example tasks
TASKS = [
    "Write a Python function to calculate fibonacci numbers recursively. Test it with n=10.",
    "Create a function that validates email addresses using regex. Test it with valid and invalid emails.",
    "Write a function to find the longest palindrome in a string. Test with 'babad' and 'cbbd'."
]


async def main():
    print("\n" + "="*80)
    print(" "*20 + "🤖 AutoGen Multi-Agent Code Review System")
    print("="*80)
    
    # Run first task
    await run_code_review(TASKS[0])
    
    print("\n\n✅ Demo complete! Agents collaborated successfully.")


if __name__ == "__main__":
    asyncio.run(main())
