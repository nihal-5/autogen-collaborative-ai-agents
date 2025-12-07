"""
AutoGen Core - Lab 3 Feature
Demonstrates RoutedAgent pattern and SingleThreadedAgentRuntime
"""

import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler, SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


# Define message type for agent communication
@dataclass
class TaskMessage:
    content: str
    task_type: str


# Create RoutedAgent that wraps AssistantAgent
class WorkerAgent(RoutedAgent):
    """Worker agent using AutoGen Core pattern"""
    
    def __init__(self, name: str, specialty: str) -> None:
        super().__init__(name)
        self.specialty = specialty
        model = OpenAIChatCompletionClient(model="gpt-4o-mini")
        self._delegate = AssistantAgent(
            name,
            model_client=model,
            system_message=f"You are a {specialty} specialist. Provide expert advice in your field."
        )
    
    @message_handler
    async def handle_task(self, message: TaskMessage, ctx: MessageContext) -> TaskMessage:
        """Handle incoming task messages"""
        print(f"\n[{self.id.type}] Received: {message.content[:50]}...")
        
        # Process with delegate agent
        text_msg = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_msg], ctx.cancellation_token)
        reply = response.chat_message.content
        
        print(f"[{self.id.type}] Response: {reply[:100]}...")
        
        return TaskMessage(content=reply, task_type=message.task_type)


class CoordinatorAgent(RoutedAgent):
    """Coordinator that delegates to worker agents"""
    
    def __init__(self) -> None:
        super().__init__("Coordinator")
    
    @message_handler
    async def handle_task(self, message: TaskMessage, ctx: MessageContext) -> TaskMessage:
        """Coordinate between multiple workers"""
        print(f"\n[COORDINATOR] Processing task: {message.task_type}")
        
        # Send to appropriate workers
        if "code" in message.task_type.lower():
            worker_id = AgentId("worker", "coder")
        else:
            worker_id = AgentId("worker", "researcher")
        
        # Send message to worker and get response
        response = await self.send_message(message, worker_id)
        
        print(f"[COORDINATOR] Got response from worker")
        return response


async def demo():
    """Demonstrate AutoGen Core with RoutedAgents"""
    print("\n" + "="*80)
    print("🔧 AUTOGEN CORE DEMO (Lab 3 Feature)")
    print("="*80 + "\n")
    
    # Create runtime
    runtime = SingleThreadedAgentRuntime()
    
    # Register agents
    await WorkerAgent.register(
        runtime,
        "worker",
        lambda: WorkerAgent("CodeExpert", "Python programming")
    )
    await CoordinatorAgent.register(
        runtime,
        "coordinator",
        lambda: CoordinatorAgent()
    )
    
    # Start runtime
    runtime.start()
    
    print("✅ Runtime started with 2 agents registered\n")
    print("Agents:")
    print("  - Coordinator (routes tasks)")
    print("  - Worker/CodeExpert (handles coding tasks)\n")
    
    # Send task
    task = TaskMessage(
        content="Explain how to implement a binary search tree in Python",
        task_type="code_question"
    )
    
    coordinator_id = AgentId("coordinator", "default")
    result = await runtime.send_message(task, coordinator_id)
    
    print(f"\n📊 Final Result:")
    print(f"   {result.content[:200]}...\n")
    
    # Cleanup
    await runtime.stop()
    await runtime.close()
    
    print("✅ AutoGen Core demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
