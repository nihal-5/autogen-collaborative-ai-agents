"""
AutoGen Distributed Runtime - Lab 4 Feature
Demonstrates agents running across multiple worker processes
"""

import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost, GrpcWorkerAgentRuntime

load_dotenv()


@dataclass
class ResearchTask:
    """Message type for research tasks"""
    query: str
    complexity: str


class ResearchAgent(RoutedAgent):
    """Research agent that can run on distributed worker"""
    
    def __init__(self) -> None:
        super().__init__("ResearchAgent")
        model = OpenAIChatCompletionClient(model="gpt-4o-mini")
        self._delegate = AssistantAgent(
            "Researcher",
            model_client=model,
            system_message="You are a research specialist. Provide concise, informative responses."
        )
    
    @message_handler
    async def handle_research(self, message: ResearchTask, ctx: MessageContext) -> ResearchTask:
        """Handle research tasks"""
        print(f"[RESEARCH AGENT] Processing: {message.query}")
        
        text_msg = TextMessage(content=message.query, source="user")
        response = await self._delegate.on_messages([text_msg], ctx.cancellation_token)
        
        result = response.chat_message.content
        print(f"[RESEARCH AGENT] Completed research ({len(result)} chars)")
        
        return ResearchTask(query=result, complexity=message.complexity)


class AnalysisAgent(RoutedAgent):
    """Analysis agent that can run on separate distributed worker"""
    
    def __init__(self) -> None:
        super().__init__("AnalysisAgent")
        model = OpenAIChatCompletionClient(model="gpt-4o-mini")
        self._delegate = AssistantAgent(
            "Analyst",
            model_client=model,
            system_message="You analyze information and provide insights. Be concise."
        )
    
    @message_handler
    async def handle_analysis(self, message: ResearchTask, ctx: MessageContext) -> ResearchTask:
        """Handle analysis tasks"""
        print(f"[ANALYSIS AGENT] Analyzing research results...")
        
        prompt = f"Analyze this research and provide key insights:\n\n{message.query[:500]}"
        text_msg = TextMessage(content=prompt, source="user")
        response = await self._delegate.on_messages([text_msg], ctx.cancellation_token)
        
        result = response.chat_message.content
        print(f"[ANALYSIS AGENT] Analysis complete")
        
        return ResearchTask(query=result, complexity="analyzed")


class CoordinatorAgent(RoutedAgent):
    """Coordinator that orchestrates distributed agents"""
    
    def __init__(self) -> None:
        super().__init__("Coordinator")
    
    @message_handler
    async def coordinate(self, message: ResearchTask, ctx: MessageContext) -> ResearchTask:
        """Coordinate between distributed research and analysis agents"""
        print(f"\n[COORDINATOR] Starting distributed workflow for: {message.query[:50]}...")
        
        # Send to research agent (on worker 1)
        print("[COORDINATOR] → Delegating to Research Agent (Worker 1)")
        research_result = await self.send_message(
            message,
            AgentId("research", "default")
        )
        
        # Send to analysis agent (on worker 2)
        print("[COORDINATOR] → Delegating to Analysis Agent (Worker 2)")
        final_result = await self.send_message(
            research_result,
            AgentId("analysis", "default")
        )
        
        print("[COORDINATOR] ✅ Distributed workflow complete!\n")
        return final_result


async def run_distributed_demo():
    """
    Run distributed multi-agent system with gRPC
    
    Architecture:
    - Host: Coordinates all workers
    - Worker 1: Runs ResearchAgent
    - Worker 2: Runs AnalysisAgent  
    - Worker 3: Runs CoordinatorAgent
    
    All communicate via gRPC network protocol
    """
    
    print("\n" + "="*90)
    print("🌐 AUTOGEN DISTRIBUTED RUNTIME DEMO (Lab 4)")
    print("="*90 + "\n")
    
    print("Architecture:")
    print("  📡 gRPC Host (localhost:50051) - Coordinates workers")
    print("  🔧 Worker 1 - ResearchAgent")
    print("  🔧 Worker 2 - AnalysisAgent")
    print("  🔧 Worker 3 - CoordinatorAgent\n")
    
    # Create and start gRPC host
    print("[SETUP] Creating gRPC host...")
    host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
    host.start()
    print("✅ Host started on localhost:50051\n")
    
    # Create Worker 1 - Research Agent
    print("[SETUP] Starting Worker 1 (ResearchAgent)...")
    worker1 = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker1.start()
    await ResearchAgent.register(worker1, "research", lambda: ResearchAgent())
    print("✅ Worker 1 ready\n")
    
    # Create Worker 2 - Analysis Agent
    print("[SETUP] Starting Worker 2 (AnalysisAgent)...")
    worker2 = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker2.start()
    await AnalysisAgent.register(worker2, "analysis", lambda: AnalysisAgent())
    print("✅ Worker 2 ready\n")
    
    # Create Worker 3 - Coordinator
    print("[SETUP] Starting Worker 3 (CoordinatorAgent)...")
    worker3 = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker3.start()
    await CoordinatorAgent.register(worker3, "coordinator", lambda: CoordinatorAgent())
    print("✅ Worker 3 ready\n")
    
    print("="*90)
    print("🚀 EXECUTING DISTRIBUTED TASK\n")
    
    # Send task to coordinator
    task = ResearchTask(
        query="What are the key benefits of distributed AI agent systems?",
        complexity="medium"
    )
    
    coordinator_id = AgentId("coordinator", "default")
    result = await worker3.send_message(task, coordinator_id)
    
    print("="*90)
    print("\n📊 FINAL RESULT FROM DISTRIBUTED SYSTEM:\n")
    print(result.query[:400] + "...\n")
    
    # Cleanup
    print("\n[CLEANUP] Stopping workers...")
    await worker1.stop()
    await worker2.stop()
    await worker3.stop()
    await host.stop()
    
    print("\n✅ Distributed runtime demo complete!")
    print("\n💡 Key Point: 3 agents ran on 3 separate worker processes,")
    print("   communicating via gRPC network protocol!\n")


if __name__ == "__main__":
    asyncio.run(run_distributed_demo())
