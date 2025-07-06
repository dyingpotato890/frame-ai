from google.adk.agents import LlmAgent

from .instruction import SEGMENTATION_AGENT_PROMPT

segmentation_agent = LlmAgent(
    name="segmentation_agent",
    model="gemini-2.0-flash",
    description="Segmentation agent that segments transcript into topics",
    instruction=SEGMENTATION_AGENT_PROMPT,
    output_key="segments",
)