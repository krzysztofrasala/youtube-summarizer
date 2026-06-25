import argparse
from dotenv import load_dotenv
from src.extractor import extract_video_id, get_video_metadata, get_transcript_with_timestamps
from src.summarizer import generate_summary

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a YouTube video using Gemini AI and print the result."
    )
    parser.add_argument("url", help="Full YouTube video URL (standard or short form).")
    args = parser.parse_args()

    try:
        print("Extracting video ID...")
        video_id = extract_video_id(args.url)

        print("Fetching video metadata...")
        meta = get_video_metadata(video_id)
        print(f"  Title   : {meta['title']}")
        print(f"  Channel : {meta['channel']}")

        print("Downloading transcript...")
        transcript = get_transcript_with_timestamps(video_id)

        print("Generating summary via Gemini AI...\n")
        summary = generate_summary(transcript)

        print("=" * 60)
        print(f"  {meta['title']}")
        print(f"  {meta['channel']}")
        print("=" * 60)
        print(summary)

    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
