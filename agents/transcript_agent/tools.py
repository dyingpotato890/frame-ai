from youtube_transcript_api import YouTubeTranscriptApi # type: ignore

def youtube_transcript(video_id: str) -> list | None:
    """
    Fetches the transcript of a YouTube video given its video ID.
    This tool is used to retrieve the raw transcript data from a YouTube video link.
    Args:
        video_id: The YouTube video ID.
    """
       
    ytt_api = YouTubeTranscriptApi()
    result = ytt_api.fetch(video_id).snippets

    output = []

    for snippet in result:
        start_time = snippet.start
        end_time = start_time + snippet.duration
        
        start_minutes = int(start_time // 60)
        start_seconds = int(start_time % 60)
        end_minutes = int(end_time // 60)
        end_seconds = int(end_time % 60)
        
        formatted_snippet = {
            "text": snippet.text.strip(),
            "start_time": start_time,
            "end_time": end_time,
            "duration": snippet.duration,
            "timestamp": f"{start_minutes}:{start_seconds:02d}",
            "time_range": f"{start_minutes}:{start_seconds:02d} - {end_minutes}:{end_seconds:02d}"
        }
        
        output.append(formatted_snippet)
        
    return output