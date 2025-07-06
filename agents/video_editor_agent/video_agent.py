from google.adk.agents import Agent, SequentialAgent

# from agents.segmentation_agent.types import SegmentationOutput

from .tools import (
    download_video,
    split_video,
    convert_to_shorts_ratio
)

from .instructions import (
    DOWNLOAD_PROMPT,
    CLIPPING_PROMPT,
    RESIZE_PROMPT
)

video_download_agent = Agent(
    name="video_download_agent",
    model="gemini-2.0-flash",
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

resize_agent = Agent(
    name="resize_agent",
    model="gemini-2.0-flash",
    description="Agent to resize the videos to shorts/reels format with or withput face detection.",
    instruction=RESIZE_PROMPT,
    tools=[convert_to_shorts_ratio],
    output_key="trending_news_data"
)

video_processing_agent = SequentialAgent(
    name="video_processing_agent",
    description="Downloads and preprocesses the videos.",
    sub_agents=[
        video_download_agent, 
        video_clip_agent,
        # resize_agent,
    ]
)