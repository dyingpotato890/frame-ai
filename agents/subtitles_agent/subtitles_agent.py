from google.adk.agents import Agent

from .tools import generate_subtitles
from .instruction import SUBTITLES_PROMPT

subtitles_agent = Agent(
    name="subtitles_agent",
    model="gemini-2.5-flash",
    description="Generates subtitles for each segment and attach it to the video.",
    instruction=SUBTITLES_PROMPT,
    tools=[generate_subtitles]
)