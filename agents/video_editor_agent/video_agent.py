from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv

from ..subtitles_agent.subtitles_agent import subtitles_agent

load_dotenv()
os.environ['GROQ_API_KEY']

GROQ_MODEL_NAME = "llama3-8b-8192"
groq_llm = LiteLlm(
    model=f"groq/{GROQ_MODEL_NAME}",
)

from .tools import (
    download_video,
    split_video,
)

from .instructions import (
    DOWNLOAD_PROMPT,
    CLIPPING_PROMPT,
    VIDEO_PROCESSING_PROMPT
)

video_download_agent = Agent(
    name="video_download_agent",
    model=groq_llm,
    description="Fetches the video and downloads it to the system.",
    instruction=DOWNLOAD_PROMPT,
    tools=[download_video],
    output_key="video_data"
)

video_clip_agent = Agent(
    name="video_clip_agent",
    model="gemini-2.0-flash",
    description="Breaks down the downloaded video into the required segments using the start and end timestamps.",
    instruction=CLIPPING_PROMPT,
    tools=[split_video],
    output_key="clipped_videos"
)

video_processing_agent = Agent(
    name="video_processing_agent",
    description="Downloads and preprocesses the videos.",
    instruction=VIDEO_PROCESSING_PROMPT,
    model="gemini-2.0-flash",
    tools=[
        AgentTool(agent=video_download_agent),
        AgentTool(agent=video_clip_agent),
        AgentTool(agent=subtitles_agent),
    ],
    output_key="processed_videos"
)