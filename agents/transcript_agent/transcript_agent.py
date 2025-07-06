from google.adk.agents import Agent

from .tools import youtube_transcript

TRANSCRIPTION_PROMPT = """
You are a transcription agent that processes YouTube video transcripts.
Your task is to:
1. Take the raw youtube link URL and extract the video ID.
2. Use the **`youtube_transcript` tool** with the video ID to extract the transcript from the video.
3. Take the raw transcript data with timestamps
4. Clean up and format the text for better readability
5. Combine broken sentences and fragments into coherent paragraphs
6. Preserve important timestamp information
7. Return a well-formatted transcript with timestamps

Format your output as a clean, readable transcript with timestamps at logical paragraph breaks.
"""

transcription_agent = Agent(
    name="transcription_agent",
    model="gemini-2.0-flash",
    description="Transcription agent that converts broken down sentences into a combined text with timestamp.",
    instruction=TRANSCRIPTION_PROMPT,
    tools=[youtube_transcript],
    output_key="transcription_output"
)