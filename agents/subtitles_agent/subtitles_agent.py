from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import generate_subtitles
from .instruction import SUBTITLES_PROMPT

GROQ_MODEL_NAME = "llama3-8b-8192"
groq_llm = LiteLlm(
    model=f"groq/{GROQ_MODEL_NAME}",
)

subtitles_agent = Agent(
    name="subtitles_agent",
    model="gemini-2.5-flash",
    description="Generates subtitles for each segment and attach it to the video.",
    instruction=SUBTITLES_PROMPT,
    tools=[generate_subtitles]
)