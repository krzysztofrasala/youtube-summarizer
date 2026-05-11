import re
import ast
import yt_dlp
import subprocess

def extract_video_id(url: str) -> str:
    """
    Extracts the 11-character YouTube video ID from a standard URL.
    """
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    
    raise ValueError("Invalid YouTube URL. Could not extract video ID.")

def get_video_metadata(url: str) -> dict:
    """
    Retrieves basic video metadata (title, channel, duration) using yt-dlp.
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "Unknown Title"),
                "channel": info.get("uploader", "Unknown Channel"),
                "duration": info.get("duration", 0)
            }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch metadata: {str(e)}")

def get_video_transcript(video_id: str) -> str:
    """
    Fetches the transcript using a bulletproof subprocess fallback.
    Since the Python API is failing, we force Python to use the working CLI tool.
    """
    try:
        # Run the working CLI command in the background
        result = subprocess.run(
            ["youtube_transcript_api", video_id, "--languages", "pl", "en"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # The CLI outputs a string representation of a Python list
        # ast.literal_eval safely converts that string back into a real Python list
        output_data = ast.literal_eval(result.stdout.strip())
        
        # The output is usually nested: [[{'text': '...'}, ...]]
        if isinstance(output_data, list) and len(output_data) > 0 and isinstance(output_data[0], list):
            transcript_segments = output_data[0]
        else:
            transcript_segments = output_data
            
        # Extract just the text values and combine them
        full_transcript = " ".join([item['text'] for item in transcript_segments])
        
        # Clean up any weird line breaks
        return full_transcript.replace('\\n', ' ').replace('\n', ' ')
        
    except Exception as e:
        raise RuntimeError(f"Could not retrieve transcript via CLI: {str(e)}")