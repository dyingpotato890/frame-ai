from google.adk.agents import Agent

from .tools import extract_video_id


URL_PARSER_PROMPT = """
You are a helpful assistant that extracts YouTube video IDs from URLs.
Your task is to:
1. Receive a user query containing a YouTube video URL.
2. Once the video ID is extracted, pass this video ID to the 'transcription_agent' to get the transcript.
3. Ensure you only respond with the final output from the transcription agent.
"""

url_parser_agent = Agent(
    name="youtube_url_parser",
    model="gemini-2.0-flash",
    description="Agent that extracts YouTube video IDs from URLs and forwards them for transcription.",
    instruction=URL_PARSER_PROMPT,
    tools=[extract_video_id],
    output_key="parsed_video_id"
)