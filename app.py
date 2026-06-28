import os
import sys
import asyncio
from google.adk import Agent, Workflow
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)

    print("Initializing MCP connection...")
    connection_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "server.py"],
            cwd="C:/Users/DELL/kisan-mitra-mcp"
        )
    )

    mcp_tools = McpToolset(connection_params=connection_params)
    print("SUCCESS: Connected cleanly to Kisan-Mitra MCP Server.", file=sys.stderr)

    diagnostician = Agent(
        name="crop_doctor",
        model="gemini-2.5-flash",
        instruction="""You are an expert plant pathologist. Analyze crop inputs and images to detect diseases.
        State clearly what the disease is, then immediately route the district information to the cycle planner."""
    )

    agronomist = Agent(
        name="cycle_planner",
        model="gemini-2.5-flash",
        instruction="""You are a strategic agricultural advisor. You MUST invoke the 'evaluate_agricultural_window'
        tool using the farmer's district to look up live weather conditions. Do not guess parameters.
        Combine the disease diagnosis with the live weather metrics to issue highly specific, time-aware advice.
        
        CRITICAL SAFETY GUARDRAILS:
        1. Rain Protection Loop: If the local MCP weather report detects a WMO code matching precipitation, you MUST completely block any chemical fertilizer recommendations to prevent environmental toxic runoff.
        2. Drone Wind Boundaries: If the local telemetry registers sustained wind velocities exceeding 20 km/h, you MUST flag any aerial drone or sensitive mist-spraying operations with a hard warning.
        
        FORMATTING RULES:
        1. Be straightforward and direct. Answer the user's specific questions directly and concisely at the very beginning.
        2. Highlight ONLY the direct answers to the user's questions. Do not over-highlight extra background details.
        3. Do NOT include conversational filler like "Thank you for the recommendation" or mention the internal "crop doctor" agent. Speak directly to the user as a single unified system.""",
        tools=[mcp_tools]
    )

    kisan_mitra_flow = Workflow(
        name="kisan_mitra_orchestrator",
        edges=[
            ("START", diagnostician),
            (diagnostician, agronomist)
        ]
    )

    runner = InMemoryRunner(agent=kisan_mitra_flow)
    sample_input = "My crop leaves have white fungal powder patterns turning yellow. I am farming in Chennai."
    print(f"\nUser: {sample_input}\n")
    print("Running workflow (this may take a moment)...\n")

    await runner.run_debug(sample_input)

if __name__ == "__main__":
    asyncio.run(main())