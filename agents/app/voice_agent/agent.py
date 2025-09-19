from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from app.config.settings import get_settings
from elevenlabs.client import ElevenLabs
from opik.integrations.adk import OpikTracer
from elevenlabs import stream
import asyncio
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Initalizing elevenlabs client
elevenlabs = ElevenLabs(
    api_key=get_settings().ELEVEN_LABS_API_KEY,
)

# Initalizing the app name
APP_NAME = get_settings().APP_NAME

# Intializing the session service
session_service = InMemorySessionService()

# Intializing the knowledge query tool
toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url=get_settings().MCP_SERVER_URL),
)

# Initalizing the agent Observability
voice_agent_tracker = OpikTracer(
    name="voice_agent_tracer",
    tags=["voice", "agent"],
    metadata={
        "environment": "development",
        "model": get_settings().MODEL_NAME,
        "framework": "google-adk",
        "app_name": get_settings().APP_NAME,
    },
    project_name="Voice-Agent",
)

# Initalizing the voice agent
voice_agent = LlmAgent(
    model=get_settings().MODEL_NAME,
    name="voice_agent",
    instruction="""
    You are a specialized knowledge extractor your task is to understand the user query
    and return one line response to the user make sure you sound professional and friendly 
    maintain a good and calm composture and answer within one line
    """,
    tools=[toolset],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_agent_callback=voice_agent_tracker.before_agent_callback,
    after_agent_callback=voice_agent_tracker.after_agent_callback,
    before_model_callback=voice_agent_tracker.before_model_callback,
    after_model_callback=voice_agent_tracker.after_model_callback,
    before_tool_callback=voice_agent_tracker.before_tool_callback,
    after_tool_callback=voice_agent_tracker.after_tool_callback,
)


# Get the current session get the current session if exists or
# create a new session
async def get_current_session(
    session_servie: InMemorySessionService,
    user_id: str,
    session_id: str,
):
    current_session = await session_servie.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not current_session:
        current_session = await session_servie.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    runner = Runner(
        agent=voice_agent, app_name=APP_NAME, session_service=session_servie
    )
    return runner


# Agent Interaction
async def call_agent(query: str, session_id: str, user_id: str):
    runner = await get_current_session(
        session_servie=session_service,
        session_id=session_id,
        user_id=user_id,
    )
    try:
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        )
        async for event in events:
            yield event
    except Exception as e:
        yield f"Agent Stopped Running {e}"
    finally:
        # Check of any close attribute
        if hasattr(runner, "close"):
            # Closing the agent runner
            maybe_close = runner.close()
            if asyncio.iscoroutine(maybe_close):
                await maybe_close


# Converting the text to speech using eleven labs
def text_to_speech(text: str):
    try:
        audio_stream = elevenlabs.text_to_speech.stream(
            text=text,
            voice_id="XrExE9yKIg1WjnnlVkGX",
            model_id="eleven_multilingual_v2",
        )
        # Play the audio
        stream(audio_stream)
        return "Stream Successful"
    except Exception as e:
        return f"Audio Stream broken {e}"
