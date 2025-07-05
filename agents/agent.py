from google.adk.agents import SequentialAgent

from agents.transcript_agent.transcript_agent import transcription_agent
from agents.url_parser_agent.url_parser_agent import url_parser_agent

root_agent = SequentialAgent(
    name="VideoSegmentAgent",
    sub_agents=[url_parser_agent, transcription_agent],
    description="Extracts the video url and returns the transcript.",
)