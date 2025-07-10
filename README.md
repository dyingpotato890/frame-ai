# Frame.AI: Video Segmentation For Short-Form Content Using Collaborative AI Agents

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://ai.google.dev/docs/adk">
    <img src="https://img.shields.io/badge/Built%20with-Google%20ADK-blue.svg" alt="Built with Google ADK" />
  </a>
</p>

Frame.AI is an innovative **collaborative AI agent system** specifically designed to revolutionize **shorts and reels content generation**. By intelligently analyzing long-form YouTube videos, Frame.AI identifies and extracts high-potential segments that are primed to go viral on platforms like YouTube Shorts, Instagram Reels, and TikTok.

Built with **Google's Agent Development Kit (ADK)**, Frame.AI operates through a sophisticated multi-agent architecture, featuring a central orchestrating agent and four specialized sub-agents. This collaborative approach ensures deep analysis, precise segmentation, and optimized content output.

---

## Features

* **Viral Content Identification:** Leverages advanced AI to pinpoint moments within long-form videos that have the highest potential to become viral shorts or reels.
* **Intelligent Video Segmentation:** Automatically extracts short, engaging segments based on factors like sudden changes, emotional intensity, key phrases, and speaker focus.
* **Contextual Analysis:** Understands the narrative and context of the video to ensure extracted clips are meaningful and standalone.
* **Multi-Agent Collaboration:** A sophisticated system of specialized AI agents working in concert to achieve optimal results.
* **Google ADK Powered:** Built on a robust and scalable framework, ensuring efficient processing and future extensibility.
* **Optimized for Shorts & Reels:** Generates content with ideal aspect ratios, pacing, and engagement hooks for short-form video platforms.
* **Transcription & Keyword Analysis:** Integrates with transcription services to analyze spoken content for trending keywords and impactful dialogue.
* **Auto Subtitling & Organized Output:** Automatically generates accurate subtitles for each extracted clip and neatly organizes the video-subtitle pairs into dedicated folders for easy access and editing.

---

## Architecture: A Collaborative Agent System

Frame.AI’s core strength lies in its multi-agent architecture, orchestrated by a central VideoSegmentAgent that delegates tasks to specialized sub-agents. Among them, the Video Processing Agent manages a sequence of sub-agents for downloading, clipping, and subtitling content. This design ensures scalable, modular, and efficient short-form content generation using Google’s ADK.

```mermaid
flowchart TD
    A[YouTube Video URL] --> B[VideoSegmentAgent]
    B --> C[URL Parser Agent]
    C --> D[Transcription Agent]
    D --> E[Segmentation Agent]
    E --> F[Video Processing Agent]
    F --> F1[Video Download Agent]
    F1 --> F2[Video Clip Agent]
    F2 --> F3[Subtitles Agent]
    F3 --> H["Viral Shorts & Reels (Video + Subtitles)"]
```

---

## The Agents:

The **VideoSegmentAgent** orchestrates the following sub-agents in a precise sequential flow:

* **URL Parser Agent (`url_parser_agent`):**
    * **Role:** This is our initial gateway. It securely and accurately parses the provided YouTube video URL, validating it and extracting essential details for the next steps.

* **Transcription Agent (`transcription_agent`):**
    * **Role:** This agent dives into the video's audio, converting every spoken word into a detailed transcript. It's crucial for understanding the video's narrative, identifying key phrases, and uncovering moments of high engagement.

* **Segmentation Agent (`segmentation_agent`):**
    * **Role:** The "brain" behind identifying virality. This agent meticulously analyzes the transcribed text, looking for keywords, emotional peaks, rapid topic shifts, and other indicators of viral potential. It then pinpoints precise start and end times for the most compelling clips, applying a sophisticated scoring algorithm.
     
* **Video Processing Agent (`video_processing_agent`):**
    * **Role:** Handles all video-related tasks: downloading, clipping, and subtitling. It executes a pipeline of sub-agents and organizes outputs into folders for each processed clip.
    * **Sub-agents (via AgentTool):**
        * **Video Download Agent (`video_download_agent`)** – Ensures the full YouTube video is downloaded, ready for manipulation.
        * **Video Clip Agent (`video_clip_agent`)** – Precisely extracts the high-potential segments identified by the `segmentation_agent`.
        * **Subtitles Agent (`subtitles_agent`)** – Generates subtitles and organizes the video-subtitle output.

* **Subtitles Agent (`subtitles_agent`):**
    * **Role:** Generates subtitles for each clipped segment and moves both video and subtitle files into structured output folders. It enhances accessibility and simplifies upload or post-production tasks. This agent is invoked internally by the `video_processing_agent`.
