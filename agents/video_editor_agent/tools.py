import cv2.data
from moviepy.editor import VideoFileClip
import os
import cv2
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
                print(f"⚠️ Skipping segment {i+1}: start_time >= end_time (start={start}, end={end})")
                continue

            if start >= video_clip.duration:
                print(f"⚠️ Skipping segment {i+1}: start_time beyond video length (start={start}, video_duration={video_clip.duration})")
                continue

            # Adjust end time if it exceeds video duration
            if end > video_clip.duration:
                print(f"⚠️ Adjusting end_time to video length (original_end={end}, new_end={video_clip.duration})")
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
                print(f"✅ Saved: {output_path}")
                results.append(output_path)
            except Exception as e:
                print(f"❌ MoviePy failed for segment '{segment.topic}': {e}")
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
                        print(f"✅ Fallback success for segment '{segment.topic}': {output_path}")
                        results.append(output_path)
                    except subprocess.CalledProcessError as err:
                        print(f"❌ FFmpeg failed for segment '{segment.topic}': {err.stderr.decode()}")
                        traceback.print_exc()
                        raise
                    except Exception as err:
                        print(f"❌ Unexpected error during FFmpeg fallback for segment '{segment.topic}': {err}")
                        traceback.print_exc()
                        raise
                else:
                    print("❌ FFmpeg not installed or not found in PATH. Cannot proceed with fallback.")
                    raise RuntimeError("FFmpeg not found. Cannot perform video splitting.")
        except Exception as err:
            # Catch-all for unexpected errors
            print(f"❌ Unexpected error processing segment {i+1} ('{segment.topic if isinstance(segment, Segment) else 'Unknown' }'): {err}")
            traceback.print_exc()
            raise

    video_clip.close()
    return results
        

def convert_to_shorts_ratio(input_path: str, output_path: str = ""):
    """
    Convert a video to shorts format (9:16 aspect ratio) by center-cropping with face detection.

    This function uses OpenCV's Haar cascade classifier to detect faces in the first 30 frames
    and centers the crop around the largest detected face. If no face is detected, it defaults
    to center cropping.

    Args:
        input_path (str): Path to the input video file
        output_path (str, optional): Path for the output video. If None, adds "_shorts.mp4" suffix
                                   to the input filename. Defaults to None.

    Returns:
        str: Path to the converted shorts-format video

    Raises:
        ValueError: If video is too narrow for 9:16 crop (width < height * 9/16)
        Exception: If video file cannot be opened or processed
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_shorts.mp4"

    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Open video
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Determine crop size
    target_width = int(height * 9 / 16)
    if target_width > width:
        raise ValueError("Video too narrow to crop to 9:16 ratio.")

    # Find face center (using first 30 frames max)
    face_center_x = width // 2  # fallback default
    found = False
    for _ in range(min(30, total_frames)):
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) > 0:
            # Focus on largest face
            x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
            face_center_x = x + w // 2
            found = True
            break
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # rewind to beginning

    # Calculate cropping box
    x1 = max(0, face_center_x - target_width // 2)
    x2 = x1 + target_width
    if x2 > width:
        x2 = width
        x1 = width - target_width

    # Output writer
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, height))

    # Process all frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cropped = frame[:, int(x1):int(x2)]
        out.write(cropped)

    cap.release()
    out.release()
    return output_path


# test_segments = [
#   {
#     "topic": "Introduction",
#     "transcript": "Welcome to the video",
#     "start_time": "00:00",
#     "end_time": "00:10",
#     "viral_potential": "LOW",
#     "content_type": "Intro"
#   },
#   {
#     "topic": "Main Point",
#     "transcript": "This is the core content",
#     "start_time": "00:15",
#     "end_time": "00:25",
#     "viral_potential": "MEDIUM",
#     "content_type": "Explainer"
#   }
# ]

# try:
#     print("Attempting to split video...")

#     output_files = split_video(test_segments)
#     print("\nSuccessfully split video into files:")
#     for f in output_files:
#         print(f)
# except FileNotFoundError as e:
#     print(f"Error: {e}. Make sure a video file is in your 'downloads' directory.")
# except Exception as e:
#     print(f"An unexpected error occurred during splitting: {e}")