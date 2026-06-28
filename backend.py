import os
import sys
import asyncio
import base64
from typing import Optional
from contextlib import aclosing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk import Agent, Workflow
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for the Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Runner Instance
runner = None

class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    global runner
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)

    print("Initializing MCP connection for the backend...")
    connection_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "server.py"],
            cwd="C:/Users/DELL/kisan-mitra-mcp"
        )
    )

    mcp_tools = McpToolset(connection_params=connection_params)
    
    diagnostician = Agent(
        name="crop_doctor",
        model="gemini-2.5-flash",
        instruction="""You are an expert plant pathologist and agricultural advisor. Analyze crop inputs and images carefully.
        If an image is provided:
        1. Identify the crop type.
        2. Detect any diseases, pests, or damage shown.
        3. Provide immediate methods to reduce the damage and fix the damaged crop.
        4. Recommend safe practices to avoid future damage.
        Provide accurate responses for all types of crop doubts.
        Finally, clearly state the disease/issue and route the farmer's district information to the cycle planner."""
    )

    agronomist = Agent(
        name="cycle_planner",
        model="gemini-2.5-flash",
        instruction="""You are a strategic agricultural advisor. You receive the detailed analysis from the crop doctor.
        If the user has provided their location or district, invoke the 'evaluate_agricultural_window' tool to look up live weather conditions and incorporate weather metrics into your advice.
        If no district is provided, DO NOT ask for it. Simply provide the crop doctor's diagnosis, fixes, and safe practices.
        
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
    print("Backend initialization complete.")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Kisan-Mitra API is running"}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    global runner
    if not runner:
        return {"error": "Runner not initialized"}

    try:
        parts = []
        if req.image:
            # Assumes format "data:image/jpeg;base64,/9j/4AAQ..."
            try:
                if "," in req.image:
                    mime_type, base64_data = req.image.split(",", 1)
                    mime_type = mime_type.split(";")[0].replace("data:", "")
                else:
                    mime_type = "image/jpeg"
                    base64_data = req.image
                    
                image_bytes = base64.b64decode(base64_data)
                parts.append(types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)))
            except Exception as e:
                return {"error": f"Invalid image format: {e}"}

        parts.append(types.Part(text=req.message))
        
        user_content = types.UserContent(parts=parts)
        
        # Manually run the runner asynchronously to support multimodal inputs
        session = await runner.session_service.get_session(app_name=runner.app_name, user_id="default_user", session_id="default_session")
        if not session:
            session = await runner.session_service.create_session(app_name=runner.app_name, user_id="default_user", session_id="default_session")
            
        events = []
        async with aclosing(
            runner.run_async(
                user_id="default_user",
                session_id=session.id,
                new_message=user_content
            )
        ) as agen:
            async for event in agen:
                events.append(event)
        
        final_output = ""
        # Iterate backwards to find the last valid text output from the agent
        for event in reversed(events):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_output = part.text
                            break
            if final_output:
                break

        if not final_output:
            final_output = "I'm sorry, I couldn't generate a response."

        return {"response": final_output}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
