import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# YouTube video IDs are 11 characters: letters, digits, hyphens, underscores
_VIDEO_ID_RE = re.compile(r'^[A-Za-z0-9_-]{11}$')


def extract_video_id(url: str) -> str:
    """Parses a YouTube URL and returns the bare 11-character video ID."""
    url = url.strip()

    video_id = None
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0].split("/")[0]
    elif "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]

    if not video_id or not _VIDEO_ID_RE.match(video_id):
        raise ValueError(
            "Invalid YouTube URL. Expected a link containing 'youtu.be/' or '?v=' "
            "with a valid 11-character video ID."
        )
    return video_id


def get_video_metadata(video_id: str) -> dict:
    """Returns title, channel name, and thumbnail URL via YouTube oEmbed (no API key required).

    Falls back to placeholder values if the oEmbed request fails (e.g. private videos).
    """
    try:
        oembed_url = (
            "https://www.youtube.com/oembed"
            f"?url=https://www.youtube.com/watch?v={video_id}&format=json"
        )
        resp = requests.get(oembed_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "title": data.get("title") or "Unknown Title",
            "channel": data.get("author_name") or "Unknown Channel",
            "thumbnail": data.get("thumbnail_url") or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        }
    except requests.RequestException:
        return {
            "title": "Unknown Title",
            "channel": "Unknown Channel",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        }


def _format_timestamp(total_seconds: int) -> str:
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m:02d}:{s:02d}]"


def get_transcript_with_timestamps(video_id: str) -> str:
    """Downloads the video transcript and formats each line as '[MM:SS]' or '[H:MM:SS]' text.

    Tries Polish first, then falls back to English.
    Raises RuntimeError if no transcript is available.
    """
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["pl", "en"])
        lines = []
        for entry in transcript:
            timestamp = _format_timestamp(int(entry.start))
            lines.append(f"{timestamp} {entry.text}")
        return "\n".join(lines)
    except Exception as exc:
        raise RuntimeError(f"Could not retrieve YouTube transcript: {exc}") from exc
