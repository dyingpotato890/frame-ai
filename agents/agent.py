from google.adk.agents import SequentialAgent

from agents.transcript_agent.transcript_agent import transcription_agent
from agents.url_parser_agent.url_parser_agent import url_parser_agent
from agents.segmentation_agent.segmentation_agent import segmentation_agent
from agents.video_editor_agent.video_agent import video_processing_agent

root_agent = SequentialAgent(
    name="VideoSegmentAgent",
    sub_agents=[
        url_parser_agent,
        transcription_agent,
        segmentation_agent,
        video_processing_agent,
    ],
    description="Extracts the video url and generates the transcripts and breaks the video down into clips and then generates subtitles.",
)