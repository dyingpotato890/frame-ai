from moviepy.editor import VideoFileClip
import os
import yt_dlp
import re
import subprocess
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
import traceback


def download_video(video_id: str, output_path: str = "downloads") -> str:
    """
    Download a YouTube video by its video ID using yt-dlp.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Download best quality mp4, fallback to best available
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output filename template
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Get video info first
        info = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info)
        
        # Download the video
        ydl.download([url])
        
        return filename

class Segment(BaseModel):
    topic: str
    start_time: str = Field(pattern=r"^\d{1,2}:\d{2}(:\d{2})?$") # Example: "MM:SS" or "HH:MM:SS"
    end_time: str = Field(pattern=r"^\d{1,2}:\d{2}(:\d{2})?$") # Example: "MM:SS" or "HH:MM:SS"
    transcript: Optional[str] = None
    viral_potential: Optional[str] = None
    content_type: Optional[str] = None

def split_video(segments: List[Segment], base_filename: str = "") -> list:
    """
    Splits video into segments based on start and end times.
    """
    # Explicit Pydantic validation for incoming segments
    validated_segments: List[Segment] = []
    for i, s in enumerate(segments):
        if isinstance(s, dict):
            try:
                validated_segments.append(Segment(**s))
            except ValidationError as e:
                # Print validation error details for debugging
                print(f"ERROR: Pydantic validation failed for segment {i} (input was a dict): {e}")
                print(f"Original dictionary for segment {i}: {s}")
                traceback.print_exc()
                raise TypeError(f"Failed to validate segment {i} due to schema mismatch.")
        elif isinstance(s, Segment):
            validated_segments.append(s)
        else:
            print(f"ERROR: Unexpected type for segment {i}: {type(s)}. Expected dict or Segment.")
            raise TypeError(f"Segment {i} is of unexpected type: {type(s)}.")
    
    segments = validated_segments # Ensure we're working with validated Segment objects

    def find_video_file():
        downloads_dir = os.path.join(os.getcwd(), "downloads")
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        for file in os.listdir(downloads_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                return os.path.join(downloads_dir, file)
        raise FileNotFoundError("No video file found in downloads folder.")

    def time_to_seconds(time_str):
        parts = [int(p) for p in time_str.split(':')]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return int(time_str) # Fallback if single number (should not happen with regex in Field)

    def sanitize_filename(name):
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = re.sub(r'\s+', '_', name)
        return name.strip('._')[:100]

    def find_ffmpeg():
        # Check common paths for ffmpeg executable
        for path in ['ffmpeg', 'C:\\ffmpeg\\bin\\ffmpeg.exe', '/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg']:
            try:
                subprocess.run([path, "-version"], capture_output=True, timeout=5, check=True)
                return path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None

    # Video loading block with error handling
    try:
        video_path = find_video_file()
        video_clip = VideoFileClip(video_path)
    except FileNotFoundError as e:
        print(f"ERROR: Video file not found: {e}")
        traceback.print_exc()
        raise ValueError(f"Video file not found for splitting: {e}")
    except Exception as e:
        print(f"ERROR: Failed to load video clip: {e}")
        traceback.print_exc()
        raise ValueError(f"Failed to load video for splitting: {e}")

    results = []

    for i, segment in enumerate(segments): # 'segment' is now guaranteed to be a Segment instance
        try:
            start = time_to_seconds(segment.start_time)
            end = time_to_seconds(segment.end_time)
            
            start = max(0, start - 3)
            end = end + 3

            # Skip invalid segments
            if start >= end:
                print(f"Skipping segment {i+1}: start_time >= end_time (start={start}, end={end})")
                continue

            if start >= video_clip.duration:
                print(f"Skipping segment {i+1}: start_time beyond video length (start={start}, video_duration={video_clip.duration})")
                continue

            # Adjust end time if it exceeds video duration
            if end > video_clip.duration:
                print(f"Adjusting end_time to video length (original_end={end}, new_end={video_clip.duration})")
                end = video_clip.duration

            # Create output filename from segment properties
            filename_parts = [
                segment.topic,
                segment.content_type or '',
                segment.viral_potential or ''
            ]
            filename = sanitize_filename("_".join(filter(None, filename_parts)))
            output_dir = os.path.join(os.getcwd(), "downloads")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f"{filename}.mp4")

            # Handle duplicate filenames
            counter = 1
            base_output = output_path
            while os.path.exists(output_path):
                output_path = f"{os.path.splitext(base_output)[0]}_{counter}.mp4"
                counter += 1

            clip = video_clip.subclip(start, end)
            try:
                # Try MoviePy first
                clip.write_videofile(
                    output_path,
                    codec="libx264", # Common and standard H.264 codec
                    audio_codec="aac",
                    temp_audiofile=f"temp_audio_{i}.m4a",
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                print(f"Saved: {output_path}")
                results.append(output_path)
            except Exception as e:
                print(f"MoviePy failed for segment '{segment.topic}': {e}")
                traceback.print_exc()
                print("🔄 Trying fallback with FFmpeg...")

                # FFmpeg fallback
                ffmpeg = find_ffmpeg()
                if ffmpeg:
                    cmd = [
                        ffmpeg, '-i', video_path,
                        '-ss', str(start),
                        '-t', str(end - start),
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        '-y', output_path
                    ]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        print(f"Fallback success for segment '{segment.topic}': {output_path}")
                        results.append(output_path)
                    except subprocess.CalledProcessError as err:
                        print(f"FFmpeg failed for segment '{segment.topic}': {err.stderr.decode()}")
                        traceback.print_exc()
                        raise
                    except Exception as err:
                        print(f"Unexpected error during FFmpeg fallback for segment '{segment.topic}': {err}")
                        traceback.print_exc()
                        raise
                else:
                    print("FFmpeg not installed or not found in PATH. Cannot proceed with fallback.")
                    raise RuntimeError("FFmpeg not found. Cannot perform video splitting.")
        except Exception as err:
            # Catch-all for unexpected errors
            print(f"Unexpected error processing segment {i+1} ('{segment.topic if isinstance(segment, Segment) else 'Unknown' }'): {err}")
            traceback.print_exc()
            raise

    video_clip.close()
    return results