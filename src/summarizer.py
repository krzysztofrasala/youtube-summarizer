import os
from functools import lru_cache
from google import genai

_MODEL = "gemini-2.5-flash"

_PROMPT_TEMPLATE = """\
You are an expert content analyst specializing in YouTube video summaries.
Below is a transcript with [MM:SS] timestamps. Produce a professional, well-structured summary.

Use exactly this structure:

## Overview
2–3 sentences describing the video's main theme, purpose, and who it's for.

## Key Topics
For each major section use this format:
### [MM:SS] — Section Title
- Key idea or argument
- Supporting detail or example
- Additional point (if relevant)

## Key Takeaways
3–5 concise bullet points with the most actionable or important insights from the whole video.

Rules:
- Match the summary language to the transcript language.
- Be concise but substantive — no filler phrases.
- Timestamps must come from the transcript, not invented.

Transcript:
{transcript}"""


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    """Returns a cached Gemini client, created once per process."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not set. Add it to your .env file — see .env.example."
        )
    return genai.Client(api_key=api_key)


def generate_summary(transcript_text: str) -> str:
    """Sends a timestamped transcript to Gemini and returns a structured Markdown summary."""
    client = _get_client()
    prompt = _PROMPT_TEMPLATE.format(transcript=transcript_text)
    response = client.models.generate_content(model=_MODEL, contents=prompt)
    return response.text


def chat_with_video(transcript_text: str, history: list[dict]) -> str:
    """Answers the latest question in history using the video transcript as context.

    history: list of {"role": "user"|"assistant", "content": str} dicts,
             with the most recent user message last.
    """
    client = _get_client()

    # Prime the conversation with transcript context as a synthetic first exchange
    contents = [
        {
            "role": "user",
            "parts": [{"text": (
                "You are a helpful assistant answering questions about a YouTube video. "
                "Base your answers solely on the transcript below. "
                "Reference specific timestamps when relevant. "
                "If the answer is not in the transcript, say so clearly.\n\n"
                f"Transcript:\n{transcript_text}"
            )}],
        },
        {
            "role": "model",
            "parts": [{"text": "Understood. I have the full transcript and I'm ready to answer your questions about this video."}],
        },
    ]

    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    response = client.models.generate_content(model=_MODEL, contents=contents)
    return response.text
